import csv
import io
import re

from . import db, llm

SYSTEM = (
    "You analyse a company's internal business data (CRM exports, call transcripts, feedback, support logs). "
    "Report only patterns that are actually present in the supplied text. Every finding needs a verbatim quote."
)

PROMPT = """Company: {name}
File: {filename}

Content (may be truncated):
{content}

Find recurring objections, lost-deal reasons, product requests, sales patterns, operational issues and emerging risks.
Return JSON {{"findings": [{{"type": "objection|lost_deal|product_request|sales_pattern|operational_issue|risk",
"finding": str, "frequency_hint": str, "quote": str}}]}}.
quote must be copied verbatim from the content (under 30 words). Return an empty list if nothing meaningful is present."""


def extract_text(filename, data):
    name = filename.lower()
    if name.endswith((".txt", ".md", ".log")):
        return data.decode("utf-8", "ignore")
    if name.endswith(".csv"):
        text = data.decode("utf-8", "ignore")
        rows = list(csv.reader(io.StringIO(text)))
        return "\n".join(" | ".join(r) for r in rows)
    if name.endswith((".xlsx", ".xlsm")):
        from openpyxl import load_workbook

        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        lines = []
        for ws in wb.worksheets:
            lines.append(f"[sheet: {ws.title}]")
            for row in ws.iter_rows(values_only=True):
                lines.append(" | ".join("" if v is None else str(v) for v in row))
        return "\n".join(lines)
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    raise ValueError("Unsupported file type. Use CSV, Excel, PDF or text.")


def _norm(s):
    return re.sub(r"\W+", " ", s).strip().lower()


def ingest(company_id, filename, data):
    company = db.q("SELECT * FROM companies WHERE id=?", (company_id,), one=True)
    source = db.q(
        "SELECT * FROM sources WHERE company_id=? AND kind='upload'", (company_id,), one=True
    )
    if not source:
        raise RuntimeError("Run source discovery first; the internal uploads source does not exist yet.")
    text = extract_text(filename, data)
    if not text.strip():
        raise ValueError("No readable text found in the file.")
    corpus = _norm(text)
    stored = 0
    chunk_size = 9000
    chunks = [text[i : i + chunk_size] for i in range(0, min(len(text), chunk_size * 4), chunk_size)]
    for n, chunk in enumerate(chunks):
        out = llm.chat_json(SYSTEM, PROMPT.format(name=company["name"], filename=filename, content=chunk))
        for f in out.get("findings", []):
            quote = (f.get("quote") or "").strip()
            if not quote or _norm(quote) not in corpus:
                continue
            title = f"[{f.get('type', 'finding')}] {f.get('finding', '')}"[:300]
            url = f"internal://{company_id}/{filename}#{n}-{stored}"
            snippet = f"Quote from {filename}: \"{quote}\" ({f.get('frequency_hint', 'frequency unknown')})"
            db.x(
                "INSERT OR IGNORE INTO items(company_id,source_id,category,subject,title,url,snippet,published,discovered,dedupe_key,source_reliability) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (company_id, source["id"], "internal", filename, title, url, snippet, db.now(), db.now(), url, 0.8),
            )
            stored += 1
    db.x("UPDATE sources SET last_checked=?, last_new_item=?, health='ok' WHERE id=?", (db.now(), db.now(), source["id"]))
    return {"findings_stored": stored, "characters_read": len(text)}
