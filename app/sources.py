import json
from urllib.parse import quote_plus, urlparse

from . import db, fetch, llm

CATEGORIES = ("customers", "competitors", "market", "internal")

SYSTEM = (
    "You are a competitive-intelligence analyst designing a source list for continuous monitoring. "
    "Be specific to the company and its industry. Only suggest real, well-known organisations and websites; "
    "if unsure a URL exists, leave the url empty rather than guessing."
)

DISCOVERY_PROMPT = """Company: {name} ({url})
Dossier: {research}
Founder profile: {profile}
{extra}
Design the monitoring plan. Return JSON with:
- "competitors": 6-10 items {{"name": str, "url": str, "type": "direct" or "substitute", "why": str}}
- "customer_queries": 6-8 items {{"query": str, "why": str}}. Short search phrases (2-5 words) in the language customers use when they complain about, ask about or compare the problems this company solves. Not company names.
- "market_topics": 6-8 items {{"query": str, "why": str}}. Short news-search phrases about regulation, policy, industry shifts, technology or economic developments that could materially affect this company.
- "candidate_sources": 6-10 items {{"name": str, "url": str, "category": "customers" or "market" or "competitors", "why": str}}. Real pages likely to publish relevant updates: regulators, industry bodies, official notice pages, review sites, communities, trade publications.
- "country_code": two-letter code for the primary market"""

REVIEW_PROMPT = """Company: {name}
The founder reports this change in business context:
\"{note}\"

Current active sources:
{sources}

Decide which sources are no longer useful because of the change. Return JSON:
{{"drop": [{{"id": int, "why": str}}], "keep_note": str, "what_changed": str}}
Only drop a source when the change genuinely makes it less relevant."""


def reliability_for(url, kind):
    host = urlparse(url).netloc.lower()
    if host.endswith((".gov", ".gov.in", ".gov.uk", ".edu", ".ac.in", ".nic.in", ".europa.eu")) or ".gov." in host:
        return 0.9
    if kind == "hn":
        return 0.45
    if kind == "rss" and "news.google.com" in host:
        return 0.65
    if any(w in host for w in ("reddit", "quora", "facebook", "x.com", "twitter", "forum")):
        return 0.4
    if host.endswith(".org"):
        return 0.75
    return 0.6


def _add(company_id, category, name, url, kind, reason, subject="", status="suggested", health="unchecked", error=None, origin="discovery"):
    norm = fetch.normalize_url(url)
    if db.q("SELECT id FROM sources WHERE company_id=? AND url=?", (company_id, norm), one=True):
        return None
    return db.x(
        "INSERT INTO sources(company_id,category,subject,name,url,kind,reason,reliability,status,health,last_error,origin,created) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (company_id, category, subject, name, norm, kind, reason, reliability_for(url, kind), status, health, error, origin, db.now()),
    )


def news_url(query, country):
    cc = (country or "US").upper()
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en&gl={cc}&ceid={cc}:en"


def hn_url(query):
    return f"https://hn.algolia.com/api/v1/search_by_date?query={quote_plus(query)}&tags=story&hitsPerPage=30"


def validate(url):
    try:
        resp = fetch.get(url)
        return "ok", None, resp
    except fetch.Blocked as exc:
        return "blocked", str(exc), None
    except Exception as exc:
        return "dead", str(exc)[:200], None


def discover(company_id, extra_context="", max_validate=24):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    research = db.jload(company["research"], {})
    profile = db.jload(company["profile"], {})
    if not profile:
        raise RuntimeError("Complete the interview first so the profile exists.")
    extra = f"\nAdditional business context to weigh heavily: {extra_context}\n" if extra_context else ""
    plan = llm.chat_json(
        SYSTEM,
        DISCOVERY_PROMPT.format(
            name=company["name"],
            url=company["url"],
            research=json.dumps(research)[:4500],
            profile=json.dumps(profile)[:4500],
            extra=extra,
        ),
        temperature=0.4,
    )
    country = plan.get("country_code") or research.get("country_code") or "US"
    added = []

    def record(sid):
        if sid:
            added.append(sid)

    for comp in plan.get("competitors", [])[:10]:
        name = (comp.get("name") or "").strip()
        if not name:
            continue
        why = comp.get("why", "")
        label = "direct competitor" if comp.get("type") == "direct" else "substitute"
        record(
            _add(
                company_id, "competitors", f"News: {name}", news_url(f'"{name}"', country), "rss",
                f"Press and announcement coverage of {label} {name}. {why}", subject=name,
            )
        )
        site = (comp.get("url") or "").strip()
        if site.startswith("http"):
            record(
                _add(
                    company_id, "competitors", f"Site: {name}", site, "page",
                    f"Detects changes to {name}'s own pages (pricing, positioning, launches). {why}", subject=name,
                )
            )
    for item in plan.get("customer_queries", [])[:8]:
        qtext = (item.get("query") or "").strip()
        if qtext:
            record(
                _add(
                    company_id, "customers", f"Discussions: {qtext}", hn_url(qtext), "hn",
                    f"Public discussion where people raise this problem in their own words. {item.get('why', '')}", subject=qtext,
                )
            )
            record(
                _add(
                    company_id, "customers", f"News on: {qtext}", news_url(qtext, country), "rss",
                    f"Coverage and consumer reporting around the customer problem '{qtext}'. {item.get('why', '')}", subject=qtext,
                )
            )
    for item in plan.get("market_topics", [])[:8]:
        qtext = (item.get("query") or "").strip()
        if qtext:
            record(
                _add(
                    company_id, "market", f"Market: {qtext}", news_url(qtext, country), "rss",
                    f"Tracks developments that could materially change the business. {item.get('why', '')}", subject=qtext,
                )
            )
    record(
        _add(
            company_id, "internal", "Internal uploads (CSV, Excel, PDF, text)", f"internal://{company_id}/uploads", "upload",
            "CRM exports, call transcripts and feedback the founder uploads. Surfaces objections, lost-deal reasons and product requests.",
            status="approved", health="ok",
        )
    )
    checked = 0
    for cand in plan.get("candidate_sources", []):
        url = (cand.get("url") or "").strip()
        category = cand.get("category") if cand.get("category") in CATEGORIES else "market"
        if not url.startswith("http") or checked >= max_validate:
            continue
        checked += 1
        health, error, resp = validate(url)
        if health != "ok":
            record(
                _add(
                    company_id, category, cand.get("name", url), url, "page", cand.get("why", ""),
                    status="rejected", health=health, error=error,
                )
            )
            continue
        feeds = fetch.discover_feeds(resp.text, str(resp.url))
        target, kind = (feeds[0], "rss") if feeds else (url, "page")
        record(_add(company_id, category, cand.get("name", url), target, kind, cand.get("why", ""), health="ok"))
    return {"added": len(added), "country_code": country, "plan": plan}


def approve_all(company_id):
    db.x("UPDATE sources SET status='approved' WHERE company_id=? AND status='suggested'", (company_id,))


def reassess(company_id, note):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    active = db.q(
        "SELECT id,category,name,reason FROM sources WHERE company_id=? AND status IN ('approved','suggested') AND kind!='upload'",
        (company_id,),
    )
    review = llm.chat_json(
        SYSTEM,
        REVIEW_PROMPT.format(name=company["name"], note=note, sources=json.dumps(active)[:7000]),
    )
    dropped = []
    valid_ids = {s["id"] for s in active}
    for entry in review.get("drop", []):
        sid = entry.get("id")
        if sid in valid_ids:
            db.x(
                "UPDATE sources SET status='retired', last_error=? WHERE id=?",
                (f"Retired after context change: {entry.get('why', '')}", sid),
            )
            dropped.append({"id": sid, "why": entry.get("why", "")})
    combined = ((company.get("context_notes") or "") + "\n" + note).strip()
    db.x("UPDATE companies SET context_notes=? WHERE id=?", (combined, company_id))
    from . import interview

    interview.build_profile(company_id)
    before = {r["id"] for r in db.q("SELECT id FROM sources WHERE company_id=?", (company_id,))}
    result = discover(company_id, extra_context=note)
    new_rows = [r for r in db.q("SELECT id,category,name,reason FROM sources WHERE company_id=?", (company_id,)) if r["id"] not in before]
    outcome = {
        "what_changed": review.get("what_changed", ""),
        "retired": dropped,
        "recommended_new": new_rows,
        "discovery_country": result["country_code"],
    }
    db.x(
        "INSERT INTO change_log(company_id,note,result,created) VALUES(?,?,?,?)",
        (company_id, note, json.dumps(outcome), db.now()),
    )
    return outcome
