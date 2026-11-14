# Signal Stack — Screen Recording & Video Demo Script

**Target Duration**: 6–8 minutes  
**Goal**: Demonstrate the end-to-end intelligence engine meeting all evaluation criteria.

---

## Act 1: Introduction & System Philosophy (0:00 – 1:00)
- **Visual**: Dashboard homepage at `http://localhost:8000`. Show the clean interface and tabs.
- **Talking Points**:
  - Introduce Signal Stack: An AI-powered continuous intelligence and decision layer for founders.
  - Explain why it is not a dumb RSS news aggregator: it discovers tailored sources across Customers, Competitors, Market, and Internal data, enforces strict fact verification, scores signals across 6 dimensions, and generates decision-grade Monday Morning Briefs with verifiable citations.
  - Mention zero-cost constraint: Built on FastAPI, SQLite, APScheduler, ethical crawler engine, and Google Gemini free tier.

---

## Act 2: Company Setup & Verified Fact Research (1:00 – 2:00)
- **Visual**: Setup tab. Enter `MeetUniversity` (`https://www.meetuniversity.com`).
- **Action**: Click **Create company**, then **Research website**.
- **Talking Points**:
  - Show the initial research output.
  - Highlight the distinction between **Verified Facts** (quotes verified verbatim against crawled page corpus) versus **Assumptions** (model inferences where no verbatim quote was present).
  - Emphasize adherence to the prompt rule: no manufactured facts.

---

## Act 3: 10-Question Adaptive Interview (2:00 – 3:30)
- **Visual**: Interview tab.
- **Action**: Click **Start interview**. Answer questions one by one.
- **Talking Points**:
  - Point out that questions are tailored to MeetUniversity's study abroad business (study abroad recruitment, university partnerships, student visa hurdles).
  - Show answering question 1–3, submit an answer, demonstrate a triggered follow-up question.
  - Demonstrate clicking **Skip (confidential)** on a financial question to show user privacy control.
  - Show editing an answer later to demonstrate the dynamic intelligence profile re-synthesis.

---

## Act 4: Signal Stack Discovery & Internal Data (3:30 – 4:45)
- **Visual**: Setup / Signal Stack / Source manager tab.
- **Action**: Click **Discover sources and competitors**.
- **Talking Points**:
  - Show 20+ sources discovered across Customers, Competitors, Market, and Internal.
  - Explain the justifications:
    - **Competitors**: IDP Education, Leverage Edu, Leap Scholar, Shiksha Study Abroad with specific monitoring angles.
    - **Customers**: Queries focusing on customer pain points (e.g., student visa delays, education loan rejection, IELTS preparation) via Hacker News and news feeds.
    - **Market**: Regulatory bodies and embassy visa updates.
  - Approve all sources.
  - Show uploading an internal support/sales transcript (`.csv` or `.txt`) and see findings extracted with verbatim quotes.

---

## Act 5: Pipeline Execution & The Monday Morning Brief (4:45 – 6:15)
- **Visual**: Monday brief tab.
- **Action**: Click **Run weekly pipeline now**.
- **Talking Points**:
  - Show crawler running in background with ethical delay and robots.txt checks.
  - Watch items being ingested, scored (relevance, impact, urgency, credibility, recency, novelty), and ranked.
  - Walk through the generated **Monday Morning Brief**:
    - **Executive Summary**: 5 top developments with evidence citations `[ID]`.
    - **Customer Signals**, **Competitor Moves**, **Market Regulations**, **Internal Findings**.
    - **Opportunities Identified**: Actionable opportunities with next steps and impact.
    - **Risks & Threats** & **Weekly Recommended Actions** with assigned owners.
    - **Source Appendix**: Direct links, publication dates, and evidence snippets.
  - Click **Open email-ready HTML** to show the polished, executive-ready presentation.

---

## Act 6: Multi-Company Stress Test & Context Pivot (6:15 – 7:30)
- **Visual**: Company switch and Profile tab.
- **Action**:
  - Show another configured company (e.g., Postman / DevTools or Lemonade / InsurTech) to prove the questions, competitors, and stack completely change.
  - Return to MeetUniversity, go to **Company profile**, enter a business pivot (e.g. expanding into US STEM AI programs), and click **Reassess signal stack**.
  - Show retired obsolete sources and newly recommended sources in the change log.
  - Show the **Settings** tab with automated weekly schedule, monthly audit trigger, and run logs.
- **Conclusion**: A complete, live, traceable intelligence system ready for production use.
