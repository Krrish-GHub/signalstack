import json
from datetime import datetime, timedelta, timezone

from . import db, llm

SYSTEM = (
    "You write the Monday Morning Brief for a founder. You may only use the numbered evidence items supplied. "
    "Never invent developments, numbers or sources. Cite evidence by item id like [12]. "
    "Keep what the source reported separate from your interpretation, and label interpretation as such. "
    "If a category has no meaningful evidence, say there was no meaningful development."
)

PROMPT = """Company: {name}
Profile: {profile}
Period: {start} to {end}
Open actions from earlier briefs: {open_actions}

Evidence items (id, category, subject, score, signal_type, verification, title, what_happened, why_it_matters, published, url):
{items}

Return JSON with:
- "executive_summary": up to 5 items {{"headline": str, "detail": str, "evidence": [ids]}}
- "customers": {{"summary": str, "points": [{{"point": str, "evidence": [ids]}}]}}
- "competitors": same shape
- "market": same shape
- "internal": same shape
- "opportunities": at least 3 if evidence supports it, each {{"title": str, "evidence": [ids], "impact": str, "next_step": str, "priority": "high|medium|low"}}. If fewer than 3 are supported, return fewer and say so in "opportunities_note".
- "risks": [{{"title": str, "evidence": [ids], "possible_impact": str, "urgency": "high|medium|low"}}]
- "actions": [{{"action": str, "reason": str, "owner": str, "priority": "high|medium|low", "evidence": [ids]}}]
- "watch": [{{"item": str, "why": str, "evidence": [ids]}}]
- "opportunities_note": str
Use only ids that appear in the evidence list. Summaries must be interpretations clearly tied to the cited items."""

HEADINGS = [
    ("customers", "Customer Signals"),
    ("competitors", "Competitor Intelligence"),
    ("market", "Market Intelligence"),
    ("internal", "Internal Business Intelligence"),
]


def _ids(values, valid):
    out = []
    for v in values or []:
        try:
            v = int(v)
        except (TypeError, ValueError):
            continue
        if v in valid:
            out.append(v)
    return out


def _cite(ids):
    return " " + " ".join(f"[{i}]" for i in ids) if ids else ""


def select_items(company_id, lookback_days, per_category=12):
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat(timespec="seconds")
    chosen = []
    for category in ("customers", "competitors", "market", "internal"):
        chosen += db.q(
            "SELECT * FROM items WHERE company_id=? AND analyzed=1 AND discovered>=? AND category=? "
            "AND COALESCE(relevance,0)>=4 ORDER BY score DESC LIMIT ?",
            (company_id, since, category, per_category),
        )
    return chosen


def generate(company_id, lookback_days=None, kind="weekly"):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    settings = db.get_settings(company_id)
    days = lookback_days or settings["lookback_days"]
    items = select_items(company_id, days)
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    valid = {i["id"] for i in items}
    open_actions = db.q(
        "SELECT action,owner,priority FROM actions WHERE company_id=? AND status='open' LIMIT 10", (company_id,)
    )
    structured = {}
    if items:
        payload = []
        for it in items:
            a = db.jload(it["analysis"], {})
            payload.append(
                {
                    "id": it["id"], "category": it["category"], "subject": it["subject"], "score": it["score"],
                    "signal_type": it["signal_type"], "verification": it["verification"], "title": it["title"],
                    "what_happened": a.get("what_happened", ""), "why_it_matters": a.get("why_it_matters", ""),
                    "published": it["published"], "url": it["url"],
                }
            )
        structured = llm.chat_json(
            SYSTEM,
            PROMPT.format(
                name=company["name"], profile=company["profile"][:3000], start=start, end=end,
                open_actions=json.dumps(open_actions), items=json.dumps(payload),
            ),
            temperature=0.3,
        )
    markdown, used_ids, actions = render(company, structured, items, valid, start, end, days)
    title = f"{company['name']} {'Monday Morning Brief' if kind == 'weekly' else 'Brief'}: week of {end}"
    brief_id = db.x(
        "INSERT INTO briefs(company_id,kind,title,markdown,meta,created) VALUES(?,?,?,?,?,?)",
        (company_id, kind, title, markdown, json.dumps({"item_ids": sorted(used_ids), "period": [str(start), str(end)], "items_considered": len(items)}), db.now()),
    )
    for a in actions:
        db.x(
            "INSERT INTO actions(company_id,brief_id,action,reason,owner,priority,created) VALUES(?,?,?,?,?,?,?)",
            (company_id, brief_id, a.get("action", ""), a.get("reason", ""), a.get("owner", ""), a.get("priority", "medium"), db.now()),
        )
    return {"brief_id": brief_id, "items_considered": len(items)}


def render(company, data, items, valid, start, end, days):
    used = set()
    out = [f"# {company['name']}: Monday Morning Brief", f"Period: {start} to {end} (last {days} days). Items considered: {len(items)}.", ""]
    if not items:
        out += [
            "## Executive Summary",
            "No analysed intelligence records met the relevance threshold in this period. "
            "Either no approved sources produced new content, or nothing was relevant. Nothing has been invented to fill this report.",
            "",
        ]

    def section(title, block):
        out.append(f"## {title}")
        if not block or (not block.get("points") and not block.get("summary")):
            out.append("No meaningful development in this category during the period.")
            out.append("")
            return
        if block.get("summary"):
            out.append(block["summary"])
        for p in block.get("points", []):
            ids = _ids(p.get("evidence"), valid)
            if not ids:
                continue
            used.update(ids)
            out.append(f"- {p.get('point', '')}{_cite(ids)}")
        out.append("")

    if items:
        out.append("## Executive Summary")
        top = data.get("executive_summary", [])[:5]
        shown = 0
        for e in top:
            ids = _ids(e.get("evidence"), valid)
            if not ids:
                continue
            used.update(ids)
            shown += 1
            out.append(f"{shown}. **{e.get('headline', '')}**: {e.get('detail', '')}{_cite(ids)}")
        if not shown:
            out.append("No developments with traceable evidence were identified.")
        out.append("")
        for key, title in HEADINGS:
            section(title, data.get(key))
        out.append("## Opportunities Identified")
        opps = [o for o in data.get("opportunities", []) if _ids(o.get("evidence"), valid)]
        for n, o in enumerate(opps, 1):
            ids = _ids(o.get("evidence"), valid)
            used.update(ids)
            out.append(f"{n}. **{o.get('title', '')}** (priority: {o.get('priority', 'n/a')})")
            out.append(f"   - Impact: {o.get('impact', '')}")
            out.append(f"   - Next step: {o.get('next_step', '')}{_cite(ids)}")
        if len(opps) < 3:
            out.append(f"Only {len(opps)} opportunity(ies) are supported by this week's evidence. {data.get('opportunities_note', '')}")
        out.append("")
        out.append("## Risks and Threats")
        risks = [r for r in data.get("risks", []) if _ids(r.get("evidence"), valid)]
        if not risks:
            out.append("No material risks identified from this week's evidence.")
        for r in risks:
            ids = _ids(r.get("evidence"), valid)
            used.update(ids)
            out.append(f"- **{r.get('title', '')}** (urgency: {r.get('urgency', 'n/a')}). Possible impact: {r.get('possible_impact', '')}{_cite(ids)}")
        out.append("")
    actions = [a for a in data.get("actions", []) if _ids(a.get("evidence"), valid)] if items else []
    out.append("## Recommended Actions for This Week")
    if not actions:
        out.append("No actions recommended; evidence was insufficient.")
    for n, a in enumerate(actions, 1):
        ids = _ids(a.get("evidence"), valid)
        used.update(ids)
        out.append(f"{n}. {a.get('action', '')} (owner: {a.get('owner', 'unassigned')}, priority: {a.get('priority', 'n/a')}). Reason: {a.get('reason', '')}{_cite(ids)}")
    out.append("")
    out.append("## What We Should Watch")
    watch = [w for w in (data.get("watch", []) if items else []) if _ids(w.get("evidence"), valid)]
    if not watch:
        out.append("Nothing flagged for continued monitoring beyond the standing sources.")
    for w in watch:
        ids = _ids(w.get("evidence"), valid)
        used.update(ids)
        out.append(f"- {w.get('item', '')}: {w.get('why', '')}{_cite(ids)}")
    out.append("")
    out.append("## Source Appendix")
    by_id = {i["id"]: i for i in items}
    if not used:
        out.append("No sources cited.")
    for i in sorted(used):
        it = by_id[i]
        a = db.jload(it["analysis"], {})
        out.append(f"**[{i}] {it['title']}**")
        out.append(f"- Link: {it['url']}")
        out.append(f"- Published: {it['published'] or 'not stated'}; discovered: {it['discovered']}")
        out.append(f"- Evidence snippet: {(it['snippet'] or '')[:300]}")
        out.append(f"- Verification: {it['verification']}; source reliability {it['source_reliability']}; evidence strength {it['evidence_strength']}; score {it['score']}")
        out.append(f"- Model interpretation (not verified fact): {a.get('why_it_matters', '')}")
        out.append("")
    return "\n".join(out), used, actions
