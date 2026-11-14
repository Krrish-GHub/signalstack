# Signal Stack — Local Setup & Reproduction Guide

## Prerequisites
- Python 3.10+ (tested through Python 3.14)
- Git
- Internet access for crawling public news and feeds
- A free Gemini API key from Google AI Studio (or free Groq key or local Ollama)

---

## 1. Quick Start

### Step 1: Clone or Navigate to the Repository
```bash
cd signalstack
```

### Step 2: Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Edit `.env` and paste your Gemini API key:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
CRAWLER_CONTACT=founder@example.com
CRAWL_DELAY_SECONDS=2
```

*(Note: If you prefer Groq, set `LLM_PROVIDER=groq` and provide `GROQ_API_KEY`. If using local Ollama, leave `LLM_PROVIDER=ollama` with `ollama run llama3.1:8b` running).*

### Step 5: Start the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open your browser and navigate to: **`http://localhost:8000`**

---

## 2. End-to-End Demonstration Walkthrough

### Part A: Primary Company Demonstration (MeetUniversity)
1. **Company Setup**:
   - In the **Setup** tab, enter:
     - Company Name: `MeetUniversity`
     - Website: `https://www.meetuniversity.com`
   - Click **Create company**.
   - Click **Research website**. The engine crawls the homepage and key internal links, extracting facts and validating quotes against the text.

2. **Adaptive AI Interview**:
   - Navigate to the **Interview** tab.
   - Click **Start interview**.
   - The engine generates 10 company-specific questions spanning business lines, target student segments, admissions bottlenecks, study abroad competitors, and founder growth priorities.
   - Submit answers sequentially. Notice follow-up questions triggered if answers require further detail. Test skipping confidential questions.
   - Upon completion, the **Company Intelligence Profile** is automatically compiled.

3. **Signal Stack Discovery**:
   - Return to the **Setup** tab (or **Source manager**).
   - Click **Discover sources and competitors**.
   - The system generates 20+ justified sources across **Customers** (Hacker News & student discussion queries), **Competitors** (direct EdTech study abroad platforms like Leverage Edu, IDP, Leap Scholar), **Market** (visa regulations, international student admissions policy), and **Internal**.
   - Click **Approve all suggested sources**.

4. **Internal Document Upload (Optional but Recommended)**:
   - On the **Intelligence feed** tab, upload a sample customer support or sales objection log (`.csv`, `.xlsx`, `.pdf`, or `.txt`).
   - The system extracts findings with verbatim quotes.

5. **Generate Monday Morning Brief**:
   - Navigate to the **Monday brief** tab.
   - Click **Run weekly pipeline now**.
   - The system crawls all approved sources, extracts developments, runs the 6-factor intelligence analysis, and produces the complete **Monday Morning Brief**.
   - Inspect the Executive Summary, Customer Signals, Competitor Intelligence, Opportunities, Risks, Actions, and the full Source Appendix with evidence links.
   - Click **Open email-ready HTML** or **Download markdown** to preview the formatted briefing.

---

## 3. Stress-Testing Multi-Company & Context Change

### Testing Additional Companies
1. In the top bar, click **New company**.
2. Configure Company 2 (e.g. `Postman` at `https://www.postman.com` for DevTools).
3. Configure Company 3 (e.g. `Lemonade` at `https://www.lemonade.com` for InsurTech).
4. Run the interview and discovery on each: observe how the interview questions, competitors, customer query phrases, and market sources shift completely to match the respective industry.

### Testing Context Change Reassessment
1. Select **MeetUniversity** and open the **Company profile** tab.
2. In the "Business context changed?" section, enter:
   > *"We are pivoting away from undergraduate university placement in the UK and expanding exclusively into US AI & STEM master's degree recruitment and corporate upskilling partnerships."*
3. Click **Reassess signal stack**.
4. The system:
   - Identifies and retires obsolete UK undergraduate sources.
   - Recommends new US STEM visa, AI master's, and corporate training sources.
   - Explains what changed and records the audit log under **Runs and changes**.

