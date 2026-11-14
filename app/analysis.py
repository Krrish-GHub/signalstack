import json
import re
from datetime import datetime, timezone

from . import db, llm

SYSTEM = (
    "You are a strategy analyst for one specific company. You are given scraped items (title and snippet only). "
    "Separate what the item literally reports from your interpretation. Never add facts that are not in the item. "
    "Score honestly: most items are not important, and generic industry news should score low relevance."
)

PROMPT = """Company: {name}
What they do: {summary}
Profile: {profile}

Items (id, category, source, title, snippet, published):
{items}

For every item return an object in JSON {{"results": [...]}} with:
- "id": the item id
- "what_happened": one sentence restating only what the item says
- "relevance": 0-10 relevance to THIS company's problem space and decisions
- "impact": 0-10 potential business impact if it is true
- "urgency": 0-10 how soon the company needs to react
- "signal_type": "opportunity", "threat" or "neutral"
- "business_area": e.g. admissions marketing, pricing, partnerships, product, compliance, sales
- "why_it_matters": one or two sentences of interpretation tied to this company; say "no clear implication" if there is none
- "suggested_response": a concrete action to consider, or "none"
- "reported_as_fact": true if the item states it as a concrete event, false if it is opinion, speculation or a rumour"""

W = {"relevance": 0.30, "impact": 0.25, "urgency": 0.15, "credibility": 0.10, "recency": 0.10, "novelty": 0.10}


def _tokens(title):
    return {t for t in re.findall(r"[a-z0-9]{4,}", title.lower())}


def novelty_for(item, others):
    mine = _tokens(item["title"])
    if not mine:
        return 0.5
    best = 0.0
    for other in others:
        theirs = _tokens(other["title"])
        if not theirs:
            continue
        sim = len(mine & theirs) / len(mine | theirs)
        best = max(best, sim)
    return round(1.0 - best, 2)


def evidence_strength(item, corroboration):
    score = 0.2
    if item.get("snippet") and len(item["snippet"]) > 80:
        score += 0.2
    if item.get("published"):
        score += 0.1
    if (item.get("url") or "").startswith("http"):
        score += 0.1
    score += min(0.4, 0.2 * corroboration)
    return round(min(score, 1.0), 2)


def recency_for(published, discovered):
    ref = published or discovered
    try:
        dt = datetime.fromisoformat(ref.replace("Z", "+00:00"))
    except Exception:
        return 0.3
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    age = (datetime.now(timezone.utc) - dt).days
    if age <= 2:
        return 1.0
    if age <= 7:
        return 0.8
    if age <= 14:
        return 0.55
    if age <= 30:
        return 0.3
    return 0.1


def final_score(item):
    credibility = item["source_reliability"] or 0.5
    recency = recency_for(item["published"], item["discovered"])
    novelty = item["novelty"] if item["novelty"] is not None else 0.5
    total = (
        W["relevance"] * (item["relevance"] or 0) / 10
        + W["impact"] * (item["impact"] or 0) / 10
        + W["urgency"] * (item["urgency"] or 0) / 10
        + W["credibility"] * credibility
        + W["recency"] * recency
        + W["novelty"] * novelty
    )
    return round(total * 100, 1)


def _verification(source_kind, reliability, reported_as_fact, corroboration):
    if not reported_as_fact:
        return "interpretation_only"
    if source_kind == "page" and reliability >= 0.75:
        return "primary_source"
    if corroboration >= 1:
        return "corroborated"
    return "single_source"


def analyze_company(company_id, batch_size=8, limit=80):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    research = db.jload(company["research"], {})
    profile = db.jload(company["profile"], {})
    pending = db.q(
        "SELECT i.*, s.name AS source_name, s.kind AS source_kind FROM items i "
        "LEFT JOIN sources s ON s.id=i.source_id WHERE i.company_id=? AND i.analyzed=0 "
        "ORDER BY COALESCE(i.published,i.discovered) DESC LIMIT ?",
        (company_id, limit),
    )
    done = 0
    for start in range(0, len(pending), batch_size):
        batch = pending[start : start + batch_size]
        payload = [
            {
                "id": it["id"], "category": it["category"], "source": it["source_name"],
                "title": it["title"], "snippet": (it["snippet"] or "")[:350], "published": it["published"],
            }
            for it in batch
        ]
        out = llm.chat_json(
            SYSTEM,
            PROMPT.format(
                name=company["name"],
                summary=research.get("summary", ""),
                profile=json.dumps(profile)[:2500],
                items=json.dumps(payload),
            ),
        )
        results = {r.get("id"): r for r in out.get("results", []) if isinstance(r, dict)}
        history = db.q(
            "SELECT title FROM items WHERE company_id=? AND analyzed=1 ORDER BY id DESC LIMIT 300", (company_id,)
        )
        for it in batch:
            res = results.get(it["id"])
            if not res:
                continue
            others = history + [{"title": o["title"]} for o in batch if o["id"] != it["id"]]
            novelty = novelty_for(it, others)
            same_story = [
                o for o in batch if o["id"] != it["id"] and o["source_id"] != it["source_id"]
                and len(_tokens(o["title"]) & _tokens(it["title"])) >= 3
            ]
            corroboration = len(same_story)
            strength = evidence_strength(it, corroboration)
            verification = _verification(
                it.get("source_kind"), it["source_reliability"] or 0.5, bool(res.get("reported_as_fact")), corroboration
            )
            row = dict(it)
            row.update(
                relevance=float(res.get("relevance", 0)), impact=float(res.get("impact", 0)),
                urgency=float(res.get("urgency", 0)), novelty=novelty,
            )
            db.x(
                "UPDATE items SET analysis=?, relevance=?, impact=?, urgency=?, novelty=?, evidence_strength=?, "
                "score=?, signal_type=?, verification=?, analyzed=1 WHERE id=?",
                (
                    json.dumps(res), row["relevance"], row["impact"], row["urgency"], novelty, strength,
                    final_score(row), res.get("signal_type", "neutral"), verification, it["id"],
                ),
            )
            done += 1
    return {"analyzed": done, "pending_seen": len(pending)}
