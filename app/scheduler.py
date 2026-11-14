import json
import traceback
from datetime import datetime, timedelta, timezone

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from . import analysis, brief, crawler, db, fetch, llm, sources

scheduler = BackgroundScheduler(timezone=pytz.UTC)

DAYS = {"mon": "mon", "tue": "tue", "wed": "wed", "thu": "thu", "fri": "fri", "sat": "sat", "sun": "sun"}


def start_run(company_id, kind, trigger):
    return db.x(
        "INSERT INTO runs(company_id,kind,trigger,status,started) VALUES(?,?,?,?,?)",
        (company_id, kind, trigger, "running", db.now()),
    )


def _exec_run(run_id, fn):
    try:
        summary = fn()
        db.x(
            "UPDATE runs SET status='success', finished=?, summary=? WHERE id=?",
            (db.now(), json.dumps(summary, default=str)[:4000], run_id),
        )
        return {"run_id": run_id, "status": "success", "summary": summary}
    except Exception as exc:
        db.x(
            "UPDATE runs SET status='failed', finished=?, error=? WHERE id=?",
            (db.now(), f"{exc}\n{traceback.format_exc()[-1500:]}", run_id),
        )
        return {"run_id": run_id, "status": "failed", "error": str(exc)}


def _run(company_id, kind, trigger, fn):
    run_id = start_run(company_id, kind, trigger)
    return _exec_run(run_id, fn)


def crawl_and_analyze(company_id):
    crawl = crawler.crawl_company(company_id)
    result = {"crawl": crawl}
    if llm.available():
        result["analysis"] = analysis.analyze_company(company_id)
    else:
        raise RuntimeError("Crawl finished but no LLM is reachable for analysis: " + json.dumps(crawl)[:300])
    return result


def weekly_brief(company_id, trigger="manual", run_id=None):
    def work():
        result = crawl_and_analyze(company_id)
        result["brief"] = brief.generate(company_id)
        return result

    if run_id:
        return _exec_run(run_id, work)
    return _run(company_id, "weekly_brief", trigger, work)


def monitor_only(company_id, trigger="scheduled", run_id=None):
    if run_id:
        return _exec_run(run_id, lambda: crawl_and_analyze(company_id))
    return _run(company_id, "monitoring", trigger, lambda: crawl_and_analyze(company_id))


def audit_report(company_id):
    rows = db.q("SELECT * FROM sources WHERE company_id=? AND status IN ('approved','suggested')", (company_id,))
    now = datetime.now(timezone.utc)
    dead, blocked, inactive, duplicates, declining = [], [], [], [], []
    seen = {}
    for s in rows:
        if s["kind"] == "upload":
            continue
        if s["status"] == "approved":
            health, error, _ = sources.validate(s["url"]) if s["kind"] == "page" else _probe(s)
            db.x(
                "UPDATE sources SET health=?, last_error=?, last_checked=? WHERE id=?",
                (health, error, db.now(), s["id"]),
            )
            if health == "dead":
                dead.append(s)
            elif health == "blocked":
                blocked.append(s)
        base = fetch.normalize_url(s["url"])
        seen.setdefault(s["name"].lower(), []).append(s)
        seen.setdefault("url:" + base, []).append(s)
        last = s["last_new_item"] or s["created"]
        try:
            age = (now - datetime.fromisoformat(last.replace("Z", "+00:00"))).days
        except Exception:
            age = 0
        if s["status"] == "approved" and age > 45:
            inactive.append((s, age))
        stats = db.q(
            "SELECT AVG(relevance) AS avg_rel, COUNT(*) AS n FROM items WHERE source_id=? AND analyzed=1", (s["id"],), one=True
        )
        if stats and stats["n"] and stats["n"] >= 5 and (stats["avg_rel"] or 0) < 3:
            declining.append((s, round(stats["avg_rel"], 1), stats["n"]))
    for key, group in seen.items():
        if len(group) > 1:
            duplicates.append((key, [g["id"] for g in group]))
    recs = []
    for s in dead:
        recs.append({"action": "remove", "source_id": s["id"], "why": f"Unreachable: {s['last_error']}"})
    for s, age in inactive:
        recs.append({"action": "remove_or_review", "source_id": s["id"], "why": f"No new items for {age} days"})
    for s, avg, n in declining:
        recs.append({"action": "review", "source_id": s["id"], "why": f"Average relevance {avg}/10 across {n} items"})
    suggestions = []
    if llm.available():
        try:
            result = sources.discover(company_id, extra_context="Monthly audit: suggest sources not already covered.")
            suggestions = db.q(
                "SELECT id,category,name,reason FROM sources WHERE company_id=? AND status='suggested' AND created>=?",
                (company_id, (now - timedelta(minutes=5)).isoformat(timespec="seconds")),
            )
            suggestions = suggestions[:15]
        except Exception as exc:
            suggestions = [{"error": f"Discovery step failed: {exc}"}]
    lines = ["# Monthly Signal Stack Audit", f"Generated {db.now()}", ""]
    lines.append(f"Sources checked: {len([r for r in rows if r['status'] == 'approved' and r['kind'] != 'upload'])}")
    lines.append("")
    lines.append("## Dead or unreachable")
    lines += [f"- {s['name']} ({s['url']}): {s['last_error']}" for s in dead] or ["None."]
    lines.append("")
    lines.append("## Blocked by robots.txt or access rules (not crawled)")
    lines += [f"- {s['name']} ({s['url']})" for s in blocked] or ["None."]
    lines.append("")
    lines.append("## Inactive (no new items in 45+ days)")
    lines += [f"- {s['name']}: {age} days" for s, age in inactive] or ["None."]
    lines.append("")
    lines.append("## Duplicate sources")
    lines += [f"- {k}: source ids {ids}" for k, ids in duplicates] or ["None."]
    lines.append("")
    lines.append("## Declining relevance")
    lines += [f"- {s['name']}: average relevance {avg}/10 over {n} items" for s, avg, n in declining] or ["None."]
    lines.append("")
    lines.append("## Newly suggested sources (awaiting approval)")
    lines += [f"- {s.get('name', s.get('error'))}: {s.get('reason', '')}" for s in suggestions] or ["None found."]
    lines.append("")
    lines.append("## Recommendations")
    lines += [f"- {r['action']} source {r['source_id']}: {r['why']}" for r in recs] or ["No removals recommended."]
    db.x(
        "INSERT INTO briefs(company_id,kind,title,markdown,meta,created) VALUES(?,?,?,?,?,?)",
        (company_id, "audit", f"Source health audit {datetime.now().date()}", "\n".join(lines), json.dumps({"recommendations": recs}), db.now()),
    )
    return {"dead": len(dead), "blocked": len(blocked), "inactive": len(inactive), "duplicates": len(duplicates), "recommendations": len(recs)}


def _probe(source):
    try:
        fetch.get(source["url"])
        return "ok", None, None
    except fetch.Blocked as exc:
        return "blocked", str(exc), None
    except Exception as exc:
        return "dead", str(exc)[:200], None


def monthly_audit(company_id, trigger="manual", run_id=None):
    if run_id:
        return _exec_run(run_id, lambda: audit_report(company_id))
    return _run(company_id, "source_audit", trigger, lambda: audit_report(company_id))


def schedule_company(company_id):
    s = db.get_settings(company_id)
    for suffix in ("brief", "monitor", "audit"):
        job_id = f"{suffix}-{company_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
    if not s.get("scheduler_enabled", True):
        return
    tz = pytz.timezone(s["timezone"])
    hh, mm = [int(p) for p in s["briefing_time"].split(":")]
    scheduler.add_job(
        weekly_brief, CronTrigger(day_of_week=DAYS.get(s["briefing_day"], "mon"), hour=hh, minute=mm, timezone=tz),
        args=[company_id, "scheduled"], id=f"brief-{company_id}", replace_existing=True, misfire_grace_time=3600,
    )
    scheduler.add_job(
        monitor_only, IntervalTrigger(hours=int(s["monitoring_frequency_hours"]), timezone=pytz.UTC),
        args=[company_id, "scheduled"], id=f"monitor-{company_id}", replace_existing=True, misfire_grace_time=3600,
    )
    ah, am = [int(p) for p in s["audit_time"].split(":")]
    scheduler.add_job(
        monthly_audit, CronTrigger(day=int(s["audit_day_of_month"]), hour=ah, minute=am, timezone=tz),
        args=[company_id, "scheduled"], id=f"audit-{company_id}", replace_existing=True, misfire_grace_time=86400,
    )


def start():
    if not scheduler.running:
        scheduler.start()
    for row in db.q("SELECT id FROM companies"):
        schedule_company(row["id"])


def next_runs(company_id):
    out = {}
    for suffix in ("brief", "monitor", "audit"):
        job = scheduler.get_job(f"{suffix}-{company_id}")
        out[suffix] = job.next_run_time.isoformat() if job and job.next_run_time else None
    return out
