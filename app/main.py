import html as html_lib
import json
import re
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

if __package__ is None or __package__ == "":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import app.analysis as analysis
    import app.crawler as crawler
    import app.db as db
    import app.fetch as fetch
    import app.internal as internal
    import app.interview as interview
    import app.llm as llm
    import app.research as research
    import app.scheduler as scheduler
    import app.sources as sources
else:
    from . import analysis, crawler, db, fetch, internal, interview, llm, research, scheduler, sources

STATIC = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app):
    db.init()
    scheduler.start()
    yield
    scheduler.scheduler.shutdown(wait=False)


app = FastAPI(title="Signal Stack", lifespan=lifespan)


class CompanyIn(BaseModel):
    name: str
    url: str


class AnswerIn(BaseModel):
    question_id: int
    answer: Optional[str] = None
    skip: bool = False


class EditAnswerIn(BaseModel):
    answer: str


class SourceIn(BaseModel):
    category: str
    name: str
    url: str
    reason: str
    kind: Optional[str] = None


class StatusIn(BaseModel):
    status: str


class NoteIn(BaseModel):
    note: str


def company_or_404(company_id):
    row = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    if not row:
        raise HTTPException(404, "Company not found")
    return row


def guard(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except HTTPException:
        raise
    except (ValueError, RuntimeError, llm.LLMError) as exc:
        raise HTTPException(400, str(exc))


def background(fn, *args):
    threading.Thread(target=fn, args=args, daemon=True).start()


@app.get("/api/health")
def health():
    return {"llm_provider": str(llm.get_provider()), "llm_reachable": llm.available()}


@app.get("/api/companies")
def list_companies():
    return db.q("SELECT id,name,url,created FROM companies ORDER BY id")


@app.post("/api/companies")
def create_company(body: CompanyIn):
    url = body.url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    cid = db.x("INSERT INTO companies(name,url,created) VALUES(?,?,?)", (body.name.strip(), url, db.now()))
    db.save_settings(cid, {})
    scheduler.schedule_company(cid)
    return {"id": cid}


@app.get("/api/companies/{cid}")
def get_company(cid: int):
    c = company_or_404(cid)
    c["research"] = db.jload(c["research"], {})
    c["profile"] = db.jload(c["profile"], {})
    c["counts"] = {
        "sources_approved": db.q("SELECT COUNT(*) n FROM sources WHERE company_id=? AND status='approved'", (cid,), one=True)["n"],
        "items": db.q("SELECT COUNT(*) n FROM items WHERE company_id=?", (cid,), one=True)["n"],
        "briefs": db.q("SELECT COUNT(*) n FROM briefs WHERE company_id=? AND kind!='audit'", (cid,), one=True)["n"],
    }
    return c


@app.delete("/api/companies/{cid}")
def delete_company(cid: int):
    company_or_404(cid)
    for table in ("interview", "sources", "items", "runs", "briefs", "actions", "settings", "change_log"):
        db.x(f"DELETE FROM {table} WHERE company_id=?", (cid,))
    db.x("DELETE FROM companies WHERE id=?", (cid,))
    scheduler.schedule_company(cid)
    return {"ok": True}


@app.post("/api/companies/{cid}/research")
def run_research(cid: int):
    company_or_404(cid)
    return guard(research.research_company, cid)


@app.put("/api/companies/{cid}/profile")
def save_profile(cid: int, body: dict):
    company_or_404(cid)
    db.x("UPDATE companies SET profile=? WHERE id=?", (json.dumps(body), cid))
    return body


@app.get("/api/companies/{cid}/interview")
def interview_state(cid: int):
    company_or_404(cid)
    return interview.state(cid)


@app.post("/api/companies/{cid}/interview/start")
def interview_start(cid: int, reset: bool = False):
    company_or_404(cid)
    return guard(interview.start, cid, reset)


@app.post("/api/companies/{cid}/interview/answer")
def interview_answer(cid: int, body: AnswerIn):
    company_or_404(cid)
    return guard(interview.answer, cid, body.question_id, body.answer, body.skip)


@app.put("/api/companies/{cid}/interview/{qid}")
def interview_edit(cid: int, qid: int, body: EditAnswerIn):
    company_or_404(cid)
    return guard(interview.edit_answer, cid, qid, body.answer)


@app.post("/api/companies/{cid}/discover")
def discover(cid: int):
    company_or_404(cid)
    result = guard(sources.discover, cid)
    return {"added": result["added"], "plan": result["plan"]}


@app.post("/api/companies/{cid}/sources/approve-all")
def approve_all(cid: int):
    company_or_404(cid)
    sources.approve_all(cid)
    return {"ok": True}


@app.get("/api/companies/{cid}/sources")
def list_sources(cid: int):
    company_or_404(cid)
    rows = db.q(
        "SELECT s.*, (SELECT COUNT(*) FROM items i WHERE i.source_id=s.id) AS item_count FROM sources s "
        "WHERE s.company_id=? ORDER BY s.category, s.status, s.name",
        (cid,),
    )
    names = {}
    for r in rows:
        names.setdefault(r["url"], []).append(r["id"])
    for r in rows:
        r["duplicate_of"] = [i for i in names[r["url"]] if i != r["id"]]
    return rows


@app.post("/api/companies/{cid}/sources")
def add_source(cid: int, body: SourceIn):
    company_or_404(cid)
    if body.category not in sources.CATEGORIES:
        raise HTTPException(400, "Category must be customers, competitors, market or internal")
    if not body.reason.strip():
        raise HTTPException(400, "Every source needs a reason for inclusion")
    url = body.url.strip()
    kind = body.kind
    health, error = "unchecked", None
    if not kind:
        health, error, resp = sources.validate(url)
        kind = "page"
        if resp is not None:
            feeds = fetch.discover_feeds(resp.text, str(resp.url))
            if feeds:
                url, kind = feeds[0], "rss"
    sid = sources._add(cid, body.category, body.name, url, kind, body.reason, status="approved", health=health, error=error, origin="manual")
    if not sid:
        raise HTTPException(409, "That URL is already in the Signal Stack")
    return {"id": sid, "kind": kind, "health": health}


@app.patch("/api/sources/{sid}")
def set_source_status(sid: int, body: StatusIn):
    if body.status not in ("approved", "suggested", "rejected", "retired", "removed"):
        raise HTTPException(400, "Invalid status")
    db.x("UPDATE sources SET status=? WHERE id=?", (body.status, sid))
    return {"ok": True}


@app.delete("/api/sources/{sid}")
def remove_source(sid: int):
    db.x("UPDATE sources SET status='removed' WHERE id=?", (sid,))
    return {"ok": True}


@app.get("/api/companies/{cid}/stack")
def signal_stack(cid: int):
    company_or_404(cid)
    stack = {c: [] for c in sources.CATEGORIES}
    for r in db.q("SELECT * FROM sources WHERE company_id=? AND status IN ('approved','suggested') ORDER BY name", (cid,)):
        stack[r["category"]].append(r)
    return stack


@app.get("/api/companies/{cid}/items")
def feed(
    cid: int, category: Optional[str] = None, subject: Optional[str] = None, since: Optional[str] = None,
    min_relevance: Optional[float] = None, min_impact: Optional[float] = None,
    verification: Optional[str] = None, signal_type: Optional[str] = None, limit: int = 200,
):
    company_or_404(cid)
    sql = "SELECT i.*, s.name AS source_name FROM items i LEFT JOIN sources s ON s.id=i.source_id WHERE i.company_id=?"
    args = [cid]
    for col, val in (("i.category", category), ("i.verification", verification), ("i.signal_type", signal_type)):
        if val:
            sql += f" AND {col}=?"
            args.append(val)
    if subject:
        sql += " AND lower(i.subject) LIKE ?"
        args.append(f"%{subject.lower()}%")
    if since:
        sql += " AND COALESCE(i.published,i.discovered)>=?"
        args.append(since)
    if min_relevance is not None:
        sql += " AND COALESCE(i.relevance,0)>=?"
        args.append(min_relevance)
    if min_impact is not None:
        sql += " AND COALESCE(i.impact,0)>=?"
        args.append(min_impact)
    sql += " ORDER BY COALESCE(i.published,i.discovered) DESC LIMIT ?"
    args.append(limit)
    rows = db.q(sql, tuple(args))
    for r in rows:
        r["analysis"] = db.jload(r["analysis"], {})
    return rows


@app.post("/api/companies/{cid}/crawl")
def crawl_now(cid: int):
    company_or_404(cid)
    run_id = scheduler.start_run(cid, "monitoring", "manual")
    background(scheduler.monitor_only, cid, "manual", run_id)
    return {"started": True, "run_id": run_id}


@app.post("/api/companies/{cid}/analyze")
def analyze_now(cid: int):
    company_or_404(cid)
    return guard(analysis.analyze_company, cid)


@app.post("/api/companies/{cid}/upload")
async def upload(cid: int, file: UploadFile = File(...)):
    company_or_404(cid)
    data = await file.read()
    return guard(internal.ingest, cid, file.filename, data)


@app.post("/api/companies/{cid}/brief")
def generate_brief(cid: int):
    company_or_404(cid)
    run_id = scheduler.start_run(cid, "weekly_brief", "manual")
    background(scheduler.weekly_brief, cid, "manual", run_id)
    return {"started": True, "run_id": run_id}


@app.post("/api/companies/{cid}/audit")
def run_audit(cid: int):
    company_or_404(cid)
    run_id = scheduler.start_run(cid, "source_audit", "manual")
    background(scheduler.monthly_audit, cid, "manual", run_id)
    return {"started": True, "run_id": run_id}


@app.get("/api/companies/{cid}/briefs")
def list_briefs(cid: int, kind: Optional[str] = None):
    company_or_404(cid)
    if kind:
        return db.q("SELECT id,kind,title,created FROM briefs WHERE company_id=? AND kind=? ORDER BY id DESC", (cid, kind))
    return db.q("SELECT id,kind,title,created FROM briefs WHERE company_id=? ORDER BY id DESC", (cid,))


@app.get("/api/briefs/{bid}")
def get_brief(bid: int):
    row = db.q("SELECT * FROM briefs WHERE id=?", (bid,), one=True)
    if not row:
        raise HTTPException(404, "Brief not found")
    row["meta"] = db.jload(row["meta"], {})
    row["actions"] = db.q("SELECT * FROM actions WHERE brief_id=?", (bid,))
    return row


def md_to_html(md):
    out, in_list = [], False
    for line in md.splitlines():
        esc = html_lib.escape(line)
        esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
        esc = re.sub(r"(https?://[^\s<]+)", r'<a href="\1">\1</a>', esc)
        if line.startswith("- ") or re.match(r"^\s+- ", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{esc.strip()[2:]}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("## "):
            out.append(f"<h2>{esc[3:]}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{esc[2:]}</h1>")
        elif line.strip():
            out.append(f"<p>{esc}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


@app.get("/api/briefs/{bid}/export")
def export_brief(bid: int, format: str = "md"):
    row = db.q("SELECT * FROM briefs WHERE id=?", (bid,), one=True)
    if not row:
        raise HTTPException(404, "Brief not found")
    if format == "html":
        body = md_to_html(row["markdown"])
        page = (
            "<!doctype html><html><head><meta charset='utf-8'><title>" + html_lib.escape(row["title"] or "Brief") + "</title>"
            "<style>body{font-family:Arial,sans-serif;max-width:760px;margin:24px auto;line-height:1.5;color:#111}"
            "h1{font-size:22px}h2{font-size:17px;border-bottom:1px solid #ccc;padding-bottom:3px;margin-top:24px}</style></head><body>"
            + body + "</body></html>"
        )
        return HTMLResponse(page)
    return PlainTextResponse(row["markdown"], headers={"Content-Disposition": f"attachment; filename=brief-{bid}.md"})


@app.get("/api/companies/{cid}/actions")
def list_actions(cid: int):
    company_or_404(cid)
    return db.q("SELECT * FROM actions WHERE company_id=? ORDER BY status, id DESC", (cid,))


@app.patch("/api/actions/{aid}")
def update_action(aid: int, body: StatusIn):
    if body.status not in ("open", "in_progress", "done", "dropped"):
        raise HTTPException(400, "Invalid status")
    db.x("UPDATE actions SET status=? WHERE id=?", (body.status, aid))
    return {"ok": True}


@app.get("/api/companies/{cid}/settings")
def get_settings(cid: int):
    company_or_404(cid)
    return {"settings": db.get_settings(cid), "next_runs": scheduler.next_runs(cid)}


@app.put("/api/companies/{cid}/settings")
def put_settings(cid: int, body: dict):
    company_or_404(cid)
    previous = db.get_settings(cid)
    saved = db.save_settings(cid, body)
    try:
        scheduler.schedule_company(cid)
    except Exception as exc:
        db.save_settings(cid, previous)
        scheduler.schedule_company(cid)
        raise HTTPException(400, f"Invalid schedule settings: {exc}")
    return {"settings": saved, "next_runs": scheduler.next_runs(cid)}


@app.get("/api/companies/{cid}/runs")
def list_runs(cid: int):
    company_or_404(cid)
    return db.q("SELECT * FROM runs WHERE company_id=? ORDER BY id DESC LIMIT 100", (cid,))


@app.post("/api/companies/{cid}/context-change")
def context_change(cid: int, body: NoteIn):
    company_or_404(cid)
    return guard(sources.reassess, cid, body.note)


@app.get("/api/companies/{cid}/changes")
def changes(cid: int):
    company_or_404(cid)
    rows = db.q("SELECT * FROM change_log WHERE company_id=? ORDER BY id DESC", (cid,))
    for r in rows:
        r["result"] = db.jload(r["result"], {})
    return rows


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
