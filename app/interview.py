import json

from . import db, llm

SYSTEM = (
    "You are a sharp business-intelligence consultant interviewing a founder so a monitoring system "
    "can be configured for their company. Questions must be specific to this company, never generic."
)

PLAN_PROMPT = """Company: {name} ({url})
Research dossier:
{research}

Write exactly 10 interview questions for the founder, one per area, in a sensible order:
1 business lines and revenue streams, 2 highest-value customer segments, 3 current customer problems and unmet needs,
4 why customers choose this company over alternatives, 5 important competitors or substitutes,
6 major industry or market changes, 7 developments that could materially hurt or help,
8 growth priorities for the next 6-12 months, 9 internal data that should influence decisions,
10 decisions the intelligence system should help the founder make.
Use the company's own vocabulary and facts from the dossier. Do not ask what the dossier already answers;
instead confirm or go deeper. Return JSON: {{"questions": [{{"area": str, "question": str}}]}}"""

FOLLOWUP_PROMPT = """Company: {name}
Dossier summary: {summary}

Interview so far:
{qa}

The founder just answered: "{answer}" to "{question}".
Questions still to be asked: {remaining}

If the answer is vague, surprising, or opens something important that the remaining questions will not cover,
write ONE follow-up question that is not a repeat of anything above. Otherwise return null.
Return JSON: {{"followup": str or null, "area": str}}"""

PROFILE_PROMPT = """Company: {name} ({url})
Dossier: {research}

Interview answers (skipped means the founder chose not to answer):
{qa}

Build a structured company intelligence profile as JSON with keys:
business_lines, revenue_streams, priority_customer_segments, customer_problems, differentiators,
known_competitors, market_changes, material_developments, growth_priorities, internal_data_sources,
decisions_to_support, monitoring_keywords (8-12 short phrases the monitoring system should watch),
skipped_topics.
Each value is a list of short strings. Use only what the dossier or founder said; leave a list empty if unknown."""

MAX_FOLLOWUPS = 3


def _qa_text(company_id):
    rows = db.q("SELECT * FROM interview WHERE company_id=? ORDER BY seq", (company_id,))
    lines = []
    for r in rows:
        if r["answer"] is not None or r["skipped"]:
            ans = "(skipped)" if r["skipped"] else r["answer"]
            lines.append(f"Q: {r['question']}\nA: {ans}")
    return "\n".join(lines) or "(nothing yet)"


def start(company_id, reset=False):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    existing = db.q("SELECT id FROM interview WHERE company_id=?", (company_id,))
    if existing and not reset:
        return state(company_id)
    if existing:
        db.x("DELETE FROM interview WHERE company_id=?", (company_id,))
    research = db.jload(company["research"], {})
    if not research:
        raise RuntimeError("Run company research before starting the interview.")
    data = llm.chat_json(
        SYSTEM,
        PLAN_PROMPT.format(name=company["name"], url=company["url"], research=json.dumps(research)[:6000]),
        temperature=0.4,
    )
    questions = data.get("questions", [])[:10]
    if len(questions) < 10:
        raise RuntimeError(f"Model produced {len(questions)} questions instead of 10; try again.")
    for i, item in enumerate(questions, 1):
        db.x(
            "INSERT INTO interview(company_id,seq,area,question) VALUES(?,?,?,?)",
            (company_id, i, item.get("area", ""), item.get("question", "")),
        )
    return state(company_id)


def state(company_id):
    rows = db.q("SELECT * FROM interview WHERE company_id=? ORDER BY seq", (company_id,))
    pending = next((r for r in rows if r["answer"] is None and not r["skipped"]), None)
    core = [r for r in rows if not r["is_followup"]]
    core_done = [r for r in core if r["answer"] is not None or r["skipped"]]
    return {
        "started": bool(rows),
        "complete": bool(rows) and pending is None,
        "next": pending,
        "answered": len(core_done),
        "core_total": len(core),
        "followups_used": len(rows) - len(core),
        "history": [r for r in rows if r["answer"] is not None or r["skipped"]],
    }


def answer(company_id, question_id, text=None, skip=False):
    row = db.q("SELECT * FROM interview WHERE id=? AND company_id=?", (question_id, company_id), one=True)
    if not row:
        raise ValueError("Question not found")
    if skip:
        db.x("UPDATE interview SET skipped=1, answer=NULL, answered_at=? WHERE id=?", (db.now(), question_id))
    else:
        if not (text or "").strip():
            raise ValueError("Answer is empty. Use skip for confidential questions.")
        db.x(
            "UPDATE interview SET answer=?, skipped=0, answered_at=? WHERE id=?",
            (text.strip(), db.now(), question_id),
        )
    rows = db.q("SELECT * FROM interview WHERE company_id=? ORDER BY seq", (company_id,))
    used = sum(1 for r in rows if r["is_followup"])
    if not skip and used < MAX_FOLLOWUPS and not row["is_followup"]:
        _maybe_followup(company_id, row, text.strip(), rows)
    st = state(company_id)
    if st["complete"]:
        build_profile(company_id)
    return st


def _maybe_followup(company_id, row, text, rows):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    research = db.jload(company["research"], {})
    remaining = [r["question"] for r in rows if r["answer"] is None and not r["skipped"] and r["id"] != row["id"]]
    try:
        out = llm.chat_json(
            SYSTEM,
            FOLLOWUP_PROMPT.format(
                name=company["name"],
                summary=research.get("summary", ""),
                qa=_qa_text(company_id),
                answer=text,
                question=row["question"],
                remaining=json.dumps(remaining),
            ),
            temperature=0.4,
        )
    except llm.LLMError:
        return
    follow = out.get("followup") if isinstance(out, dict) else None
    if not follow or not str(follow).strip():
        return
    existing = {r["question"].strip().lower() for r in rows}
    if str(follow).strip().lower() in existing:
        return
    db.x("UPDATE interview SET seq = seq + 1 WHERE company_id=? AND seq > ?", (company_id, row["seq"]))
    db.x(
        "INSERT INTO interview(company_id,seq,area,question,is_followup) VALUES(?,?,?,?,1)",
        (company_id, row["seq"] + 1, out.get("area", "follow-up"), str(follow).strip()),
    )


def edit_answer(company_id, question_id, text):
    db.x(
        "UPDATE interview SET answer=?, skipped=0, answered_at=? WHERE id=? AND company_id=?",
        (text.strip(), db.now(), question_id, company_id),
    )
    return build_profile(company_id)


def build_profile(company_id):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    research = db.jload(company["research"], {})
    notes = company.get("context_notes") or ""
    qa = _qa_text(company_id)
    if notes:
        qa += f"\n\nLater business-context update from the founder:\n{notes}"
    profile = llm.chat_json(
        SYSTEM,
        PROFILE_PROMPT.format(
            name=company["name"], url=company["url"], research=json.dumps(research)[:5000], qa=qa
        ),
    )
    db.x("UPDATE companies SET profile=? WHERE id=?", (json.dumps(profile), company_id))
    return profile
