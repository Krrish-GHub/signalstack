# Cost statement

Total spend: 0.

| Component | Tool | Cost | Limit |
| --- | --- | --- | --- |
| Web framework | FastAPI, Uvicorn | Free, open source | none |
| Database | SQLite | Free, open source | single writer |
| Scheduler | APScheduler | Free, open source | runs only while the server process is up |
| Crawling | httpx, BeautifulSoup, feedparser | Free, open source | 2 s default delay per host |
| News feeds | Google News RSS | Free public feed | unofficial, may throttle |
| Discussions | Hacker News Algolia API | Free public API | rate limited |
| LLM | Ollama (local) or Gemini free tier or Groq free tier | Free | free tiers have per-minute and per-day caps |
| Hosting | Local machine, or any free tier that runs a Python process | Free | free hosts sleep, which pauses the scheduler |

No paid APIs, scraping platforms or AI services are used.
