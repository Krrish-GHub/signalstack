# Signal Stack

Company intelligence and Monday Morning Brief engine. FastAPI + SQLite + APScheduler, plain HTML dashboard, free LLM backends only.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export CRAWLER_CONTACT="you@example.com"      # shown in the bot user agent
```

Pick one free LLM backend:

```bash
# Option A: local, no key, no limits (needs a GPU or patience)
ollama pull llama3.1:8b
export LLM_PROVIDER=ollama

# Option B: Gemini free tier
export LLM_PROVIDER=gemini GEMINI_API_KEY=...

# Option C: Groq free tier
export LLM_PROVIDER=groq GROQ_API_KEY=...
```

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000. The database is `signalstack.db` in the working folder (override with `DB_PATH`).

## Reproduce the demo

1. Setup tab: name `MeetUniversity`, URL `https://www.meetuniversity.com`, create, then Research website.
2. Interview tab: start, answer the 10 questions (follow-ups appear when answers are thin; skip confidential ones).
3. Setup tab: Discover sources and competitors, then review them in Source manager and Approve all.
4. Monday brief tab: Run weekly pipeline now. It crawls, analyses, ranks and writes the brief.
5. Repeat for two other companies from different industries to show the stack changes.
6. Profile tab, "Business context changed": describe a change and read what was retired and recommended.
7. Settings tab: run the source-health audit; reports appear under Runs and changes.

## Layout

| File | Job |
| --- | --- |
| `app/research.py` | Reads the site, separates verified facts (quote must appear on the page) from assumptions |
| `app/interview.py` | Company-specific 10 questions, follow-ups, skip, edit, profile synthesis |
| `app/sources.py` | LLM-planned competitors, customer queries, market topics, candidate sources, validated against robots.txt; context-change reassessment |
| `app/crawler.py` | RSS, Hacker News API and page-change crawling with dedupe and history |
| `app/analysis.py` | Per-item analysis and ranking (relevance, impact, urgency, credibility, recency, novelty) |
| `app/internal.py` | CSV, Excel, PDF, text uploads turned into findings with verbatim quotes |
| `app/brief.py` | Brief generation restricted to cited evidence ids; source appendix built from the database |
| `app/scheduler.py` | Weekly brief, monitoring interval, monthly audit, run log |

## Honest limitations

- Source discovery and analysis need a reachable LLM. Without one the app reports an error instead of guessing.
- Crawling honours robots.txt and a per-host delay. Pages that block bots are marked `blocked` and skipped, never bypassed. Google News RSS, the Hacker News API and the Stack Exchange API are treated as public feeds.
- Reddit and many review sites disallow bots in robots.txt, so customer language mostly comes from Hacker News and news coverage unless the user uploads internal data.
- Gemini and Groq free tiers are rate limited; large first crawls analyse in batches and may need a second run.
- Verification labels describe sourcing (primary source, corroborated, single source, interpretation only), not truth. Model scores are interpretation, not proof.
