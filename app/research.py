import json
import re

from . import db, fetch, llm

SYSTEM = (
    "You are a business analyst building an initial company dossier from website text only. "
    "Never invent facts. A fact may only be listed as verified if you can give an exact quote "
    "copied from the supplied page text that supports it. Everything else is an assumption."
)

PROMPT = """Company: {name}
Website: {url}

Page text (each block starts with its URL):
{pages}

Return JSON with these keys:
- "summary": 2-3 sentence description of what the company does
- "industry": short industry label
- "country_code": two-letter ISO code of the main market (best guess from the text, e.g. "IN", "US")
- "products_services": list of strings
- "customer_segments": list of strings
- "positioning": one sentence
- "verified_facts": list of {{"fact": str, "evidence_url": str, "quote": str}} (quote must be copied verbatim, under 25 words)
- "assumptions": list of {{"assumption": str, "basis": str}} for anything inferred rather than stated
- "open_questions": list of things only the founder can tell us
"""


def _norm(s):
    return re.sub(r"\W+", " ", s).strip().lower()


def research_company(company_id):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    if not company:
        raise ValueError("Company not found")
    pages = []
    try:
        home = fetch.get(company["url"])
    except Exception as exc:
        raise RuntimeError(f"Could not read {company['url']}: {exc}")
    pages.append((company["url"], fetch.clean_text(home.text), fetch.meta_description(home.text)))
    for link in fetch.internal_links(home.text, str(home.url), limit=6):
        try:
            resp = fetch.get(link)
            pages.append((link, fetch.clean_text(resp.text), fetch.meta_description(resp.text)))
        except Exception:
            continue
    blocks = []
    corpus = ""
    for url, text, desc in pages:
        chunk = (desc + " " + text)[:3500]
        blocks.append(f"URL: {url}\n{chunk}")
        corpus += " " + _norm(chunk)
    if not llm.available():
        raise RuntimeError("No LLM reachable. Start Ollama or set GEMINI_API_KEY / GROQ_API_KEY.")
    data = llm.chat_json(
        SYSTEM,
        PROMPT.format(name=company["name"], url=company["url"], pages="\n\n".join(blocks)),
    )
    checked = []
    for fact in data.get("verified_facts", []) or []:
        quote = _norm(str(fact.get("quote", "")))
        fact["quote_found_on_page"] = bool(quote) and quote in corpus
        checked.append(fact)
    data["verified_facts"] = [f for f in checked if f["quote_found_on_page"]]
    dropped = [f for f in checked if not f["quote_found_on_page"]]
    data.setdefault("assumptions", [])
    for f in dropped:
        data["assumptions"].append(
            {"assumption": f.get("fact", ""), "basis": "Model claimed it was stated, but the quote was not found on the crawled pages"}
        )
    data["pages_read"] = [p[0] for p in pages]
    db.x("UPDATE companies SET research=? WHERE id=?", (json.dumps(data), company_id))
    return data
