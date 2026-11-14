# Signal Stack — Technical Architecture & Engineering Documentation

## 1. System Overview & Core Philosophy

**Signal Stack** is an AI-powered intelligence and continuous monitoring engine that converts an enterprise into an alert, continuously monitored business. It gathers signals across four primary quadrants:
- **Customers**: What unmet needs, recurring pain points, sentiment, and alternatives are discussed in public communities and forums.
- **Competitors**: Movements in product launches, pricing changes, positioning pivots, and partnerships across 5–10 direct competitors and substitutes.
- **Market**: Regulatory mandates, policy shifts, economic signals, and macroeconomic industry developments that materially impact the business.
- **Internal Intelligence**: Ingestion of customer-facing artifacts (CRM exports, sales transcripts, support logs, lost-deal summaries in CSV, Excel, PDF, and plain text) with verbatim quote tracing.

Rather than acting as a static news aggregator or vanity mention collector, Signal Stack applies an **Intelligence Analysis Engine** that separates *verified facts* from *strategic interpretations*, calculates multi-factor priority scores, and delivers an actionable, executive-ready **Monday Morning Brief**.

```
                           ┌────────────────────────┐
                           │   Target Company URL   │
                           └───────────┬────────────┘
                                       │
                                       ▼
                           ┌────────────────────────┐
                           │ Initial Web Research   │
                           │ & Verified Fact Dossier│
                           └───────────┬────────────┘
                                       │
                                       ▼
                           ┌────────────────────────┐
                           │ 10-Question Adaptive   │
                           │    Founder Interview   │
                           └───────────┬────────────┘
                                       │
                                       ▼
                           ┌────────────────────────┐
                           │ Company Intelligence   │
                           │        Profile         │
                           └───────────┬────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
        ┌───────────────────────┐             ┌───────────────────────┐
        │ Signal Stack Discovery│             │  Internal Data Feed   │
        │(Cust/Comp/Mkt Sources)│             │ (CSV, Excel, PDF, TXT)│
        └───────────┬───────────┘             └───────────┬───────────┘
                    │                                     │
                    ▼                                     │
        ┌───────────────────────┐                         │
        │ Ethical Crawler Engine│                         │
        │(robots.txt, delay,    │                         │
        │ deduplication & diff) │                         │
        └───────────┬───────────┘                         │
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                           ┌────────────────────────┐
                           │  Intelligence Analysis │
                           │  & 6-Factor Ranking    │
                           └───────────┬────────────┘
                                       │
                                       ▼
                           ┌────────────────────────┐
                           │ Monday Morning Brief   │
                           │ (Executive Dec. Layer) │
                           └────────────────────────┘
```

---

## 2. Component Architecture

### A. Initial Research & Dossier Generation (`app/research.py`)
- **Web Crawling**: Fetches target website root and up to 6 high-value internal links (`about`, `pricing`, `product`, `service`, `solution`, `university`, etc.).
- **Strict Verification Gate**: Facts extracted by the LLM are checked against the normalized corpus string. An extracted fact is only classified as a **Verified Fact** if its verbatim quote exists in the crawled corpus. If a quote is absent, the engine demotes it to **Assumption** with an explicit audit basis (`Model claimed it was stated, but quote not found on crawled pages`).
- **Storage**: Structured JSON containing summary, industry, ISO country code, customer segments, verified facts, assumptions, and open questions.

### B. Adaptive AI Founder Interview (`app/interview.py`)
- **Context-Grounded 10-Area Roadmap**:
  1. Business lines & revenue streams
  2. Highest-value customer segments
  3. Current customer problems & unmet needs
  4. Core differentiators vs. alternatives
  5. Important competitors & substitutes
  6. Major industry & market changes
  7. Material headwinds and tailwinds
  8. 6–12 month growth priorities
  9. Critical internal data sources
  10. Key decisions the intelligence stack must empower
- **Dynamic Interaction**:
  - Asks 1 question at a time.
  - Generates adaptive follow-ups (up to 3) if an answer is thin or opens new angles.
  - Allows skipping confidential questions (`skipped=1`).
  - Allows editing previous answers at any time, which automatically triggers a real-time re-synthesis of the **Company Intelligence Profile**.

### C. Signal Stack & Source Discovery (`app/sources.py`)
- **Automated Intelligence Sourcing**:
  - **Competitors**: 6–10 competitors (direct vs. substitute) with justification reasons, mapped to company-specific news search feeds and homepage monitoring.
  - **Customers**: 6–8 customer query phrases (identifying problem language, not vanity mentions), routed to Hacker News Algolia API discussions and localized Google News RSS.
  - **Market**: 6–8 market & regulatory search queries capturing government policy, visa regulations, or industry shifts.
  - **Internal**: Dedicated upload channel with reliability weighting.
- **Source Validation & Health**:
  - Real-time pre-flight check checking HTTP status and `robots.txt`.
  - Auto-discovers RSS/Atom feeds when candidate URLs are provided.
  - Calculates baseline source reliability score (0.40–0.90) based on domain TLD (`.gov`, `.edu`, `.org`, public API, general web).
- **Dynamic Context Reassessment**:
  - When the founder inputs a strategic pivot or new market context, the LLM analyzes active sources against the change, retires non-relevant sources to the audit log, recommends new sources, and records the diff in `change_log`.

### D. Ethical Monitoring & Crawler Engine (`app/crawler.py` & `app/fetch.py`)
- **Crawler Guardrails**:
  - Strict compliance with `robots.txt` using Python's `urllib.robotparser`.
  - Mandatory per-host rate-limiting delay (configurable, default 2.0s).
  - Configurable descriptive user agent with operator contact email (`SignalStackBot/1.0`).
  - No authentication bypass or paywall evasion; 401/403 responses gracefully flag source health as `blocked`.
- **Deduplication**:
  - Dual-tier deduplication by normalized URL and case-insensitive title hash.
- **Change Detection**:
  - For static webpages, maintains SHA-256 content hashes and text snapshots in `snapshots`.
  - Diffs new paragraphs/sentences against previous snapshots to isolate genuine updates.

### E. Intelligence Analysis Engine & 6-Factor Ranking (`app/analysis.py`)
Raw items are transformed through an analytical rubric:
- **Separation of Evidence vs. Interpretation**:
  - `what_happened`: Strictly constrained to the stated facts of the item.
  - `why_it_matters`: Strategic interpretation contextualized to the specific company's business model.
  - `reported_as_fact` boolean determines verification label (`primary_source`, `corroborated`, `single_source`, `interpretation_only`).
- **Composite Scoring Formula**:
  $$\text{Score} = 100 \times \left( 0.30 \cdot \frac{\text{Rel}}{10} + 0.25 \cdot \frac{\text{Imp}}{10} + 0.15 \cdot \frac{\text{Urg}}{10} + 0.10 \cdot \text{Cred} + 0.10 \cdot \text{Rec} + 0.10 \cdot \text{Nov} \right)$$
  - **Relevance** ($0.30$): Alignment to company goals and target market.
  - **Impact** ($0.25$): Magnitude of consequence to revenue, operations, or moat.
  - **Urgency** ($0.15$): Reaction horizon (immediate vs. long-term).
  - **Credibility** ($0.10$): Source reliability index (0.4–0.9).
  - **Recency** ($0.10$): Decay function based on days since publication ($\le 2\text{d}=1.0$, $\le 7\text{d}=0.8$, $\le 14\text{d}=0.55$, $\le 30\text{d}=0.3$).
  - **Novelty** ($0.10$): Jaccard distance calculated across token sets of previously processed items to penalize redundant stories.

### F. Monday Morning Executive Brief (`app/brief.py`)
Constructs an executive briefing report strictly referencing numbered evidence items:
1. **Executive Summary**: 5 highest-priority developments with inline citations `[ID]`.
2. **Customer Signals**: Community discussions, complaints, unmet needs.
3. **Competitor Intelligence**: Competitive shifts, product launches, positioning.
4. **Market Intelligence**: Policy, macroeconomic, and regulatory movements.
5. **Internal Business Intelligence**: Verbatim objection and product request patterns.
6. **Actionable Opportunities**: Minimum 3 opportunities (evidence, impact, next step, priority).
7. **Risks & Threats**: Key vulnerabilities with urgency rankings.
8. **Recommended Actions for This Week**: Task assignments with suggested owners and rationales.
9. **What We Should Watch**: Emerging signals slated for continued observation.
10. **Source Appendix**: Complete audit trail with direct URLs, discovery timestamps, verbatim snippets, and verification status.

### G. Automation & Source Health Audit (`app/scheduler.py`)
- **APScheduler Background Jobs**:
  - **Weekly Brief**: Cron-triggered briefing cycle (configurable day/time/timezone) executing crawl $\to$ analysis $\to$ ranking $\to$ markdown report generation.
  - **Periodic Monitoring**: Interval-triggered crawl and analysis cycles (e.g., every 24 hours).
  - **Monthly Signal Stack Audit**: Automated health check diagnosing dead URLs (3+ failures), blocked sources, stale feeds (>45 days inactivity), declining relevance (<3/10 avg), and automated recommendation of replacement sources.

---

## 3. Technology Stack & Justification

| Layer | Technology | Justification |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.10+) | High performance, async native, automatic OpenAPI docs, low memory footprint. |
| **Data Persistence** | SQLite (WAL mode, Foreign Keys) | Zero-maintenance, single-file portability, multi-thread safe with `threading.RLock`. |
| **Scheduling** | APScheduler 3.10 | In-process cron & interval orchestration, timezone aware via `pytz`. |
| **Web Crawling & Parsing** | HTTPX, BeautifulSoup4, feedparser | Respectful crawling, fast XML/RSS parsing, connection pooling. |
| **Document Parsing** | PyPDF, openpyxl, csv | Zero-cloud-dependency extraction of PDFs, Excel spreadsheets, and CSVs. |
| **AI LLM Inference** | Google Gemini (2.0 Flash) / Groq / Ollama | Free-tier compatible, fast structured JSON mode support. |
| **Frontend UI** | HTML5, Vanilla JavaScript, CSS3 | Instant load time, zero build steps, complete visibility into state. |
