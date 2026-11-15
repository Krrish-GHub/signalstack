"""
Signal Stack — High-Fidelity Demo Dataset Seeder (MeetUniversity)
Provides zero-friction instant demo initialization with verified facts,
adaptive interview transcript, 4-quadrant signal stack, scored intelligence items,
and a citation-backed Monday Morning Brief.
"""

import json
from datetime import datetime, timedelta, timezone
from . import db, scheduler

def seed_demo_company():
    # 1. Clean existing demo company if present or create new
    existing = db.q("SELECT id FROM companies WHERE name='MeetUniversity'", one=True)
    if existing:
        cid = existing["id"]
        for table in ("interview", "sources", "items", "runs", "briefs", "actions", "settings", "change_log"):
            db.x(f"DELETE FROM {table} WHERE company_id=?", (cid,))
        db.x("DELETE FROM companies WHERE id=?", (cid,))

    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")

    # 2. Research Dossier
    research_data = {
        "summary": "MeetUniversity is a premier international higher education recruitment and counseling platform. It connects Indian and South Asian students with over 750 global universities across the United States, United Kingdom, Canada, Australia, Ireland, and Germany, providing personalized admissions guidance, visa assistance, and university matchmaking.",
        "industry": "EdTech / International Higher Education",
        "positioning": "Personalized, AI-powered study abroad matchmaking and admissions facilitation for top global institutions.",
        "country_code": "IN",
        "products_services": [
            "University Shortlisting & Matchmaking",
            "SOP & Application Mentorship",
            "Student Visa Guidance & Mock Interviews",
            "Student Accommodation Assistance",
            "Pre-approved Education Loan Marketplace",
            "Pre-departure Briefings & Forex Advisory"
        ],
        "customer_segments": [
            "Undergraduate Study Abroad Aspirants",
            "Master of Science & STEM Degree Candidates",
            "Working Professionals Seeking Global MBAs",
            "International Admissions & Recruitment Offices"
        ],
        "verified_facts": [
            {
                "fact": "Direct institutional partnerships with over 750 accredited global universities across 6 countries.",
                "evidence_url": "https://www.meetuniversity.com/about-us",
                "quote": "Partnered with 750+ global universities across US, UK, Canada, Australia and Europe",
                "quote_found_on_page": True
            },
            {
                "fact": "Assisted over 50,000 students in obtaining international admissions and scholarships.",
                "evidence_url": "https://www.meetuniversity.com/success-stories",
                "quote": "More than 50,000 students placed in top accredited programs worldwide",
                "quote_found_on_page": True
            },
            {
                "fact": "Maintains an audited 98% student visa approval track record across major destination countries.",
                "evidence_url": "https://www.meetuniversity.com/services",
                "quote": "98% visa success rate across US, UK and Canadian study permits",
                "quote_found_on_page": True
            }
        ],
        "assumptions": [
            {
                "assumption": "Primary institutional revenue derives from university commission fees paid per enrolled student.",
                "basis": "Standard agency placement commission model inferred from university partnership listings, though exact commission terms are not published."
            },
            {
                "assumption": "Rapidly growing student interest in STEM AI and Data Science programs over traditional management degrees.",
                "basis": "Featured program listings and marketing banners heavily emphasize computer science, data analytics, and robotics."
            }
        ],
        "pages_read": [
            "https://www.meetuniversity.com",
            "https://www.meetuniversity.com/about-us",
            "https://www.meetuniversity.com/services",
            "https://www.meetuniversity.com/universities",
            "https://www.meetuniversity.com/success-stories"
        ]
    }

    # 3. Company Intelligence Profile
    profile_data = {
        "revenue_streams": [
            "University partner enrollment commissions (10-18% of first year international tuition fee)",
            "Premium student counseling and application mentorship packages (INR 25,000 - 50,000)",
            "Education loan referral commissions from lending partners (1.0-1.5% of sanctioned loan value)"
        ],
        "target_segments": [
            "Indian STEM graduate students targeting US, UK, and German master's programs",
            "Tier-2 and Tier-3 city undergraduate applicants seeking loan guidance and scholarship support",
            "Mid-career tech professionals pursuing 1-year European and Singaporean MBA programs"
        ],
        "core_differentiators": [
            "Direct university agreements providing application fee waivers and expedited offer letters",
            "Dedicated 1-on-1 human mentor matching versus impersonal automated portal bots",
            "End-to-end visa and accommodation desk with an audited 98% visa approval record"
        ],
        "key_competitors": [
            "IDP Education (Mass-market global recruitment giant with legacy physical offices)",
            "Leap Scholar (Heavily venture-backed, aggressively cross-sells student loan financing)",
            "Leverage Edu (Aggressive digital marketing and university fair roadshows)",
            "Shiksha Study Abroad (High organic search SEO traffic and student review portal)"
        ],
        "market_headwinds_tailwinds": [
            "Headwind: Canada federal caps on international student study permits causing anxiety",
            "Headwind: Severe student accommodation shortages in Dublin and London",
            "Tailwind: US 3-year STEM OPT extension maintaining strong tech degree demand",
            "Tailwind: German public universities offering tuition-free English-taught master's degrees"
        ],
        "strategic_growth_priorities": [
            "Expand US STEM and AI master's counseling capacity by 40% for fall intake",
            "Launch pre-approved student education loan portal to counter Leap Scholar's financing moat",
            "Scale direct university spot-assessment fairs in Bangalore, Hyderabad, and Pune"
        ]
    }

    # Insert Company
    cid = db.x(
        "INSERT INTO companies(name, url, research, profile, context_notes, created) VALUES(?,?,?,?,?,?)",
        ("MeetUniversity", "https://www.meetuniversity.com", json.dumps(research_data), json.dumps(profile_data), "Initial onboarding for study abroad admissions and intelligence stack.", now_iso)
    )

    # 4. Settings
    db.save_settings(cid, {
        "briefing_day": "mon",
        "briefing_time": "08:00",
        "timezone": "Asia/Kolkata",
        "monitoring_frequency_hours": 12,
        "source_refresh_days": 7,
        "lookback_days": 7,
        "audit_day_of_month": 1,
        "audit_time": "07:00",
        "scheduler_enabled": True
    })

    # 5. Adaptive Interview Questions & Transcripts
    interview_qas = [
        ("Business lines & revenue streams", "What are MeetUniversity's primary business models and monetization streams?", "We monetize primarily through university placement commissions (10-18% of first year international tuition fee upon enrollment) and premium 1-on-1 counseling packages for competitive programs. We also earn referral commissions on student loans and overseas health insurance.", 0, 0),
        ("Highest-value customer segments", "Which student segments generate the highest lifetime value and conversion rates?", "Indian graduate engineering students applying for Master's in Computer Science, Data Science, and AI in the US and Germany. They have high intent, clear GRE/IELTS readiness, and high visa conversion.", 0, 0),
        ("Current customer problems & unmet needs", "What are the most painful hurdles your prospective students face today?", "US visa appointment backlog in India (dates often 90+ days out), escalating tuition costs driven by rupee-dollar exchange rates, and unexpected loan rejection from public banks.", 0, 0),
        ("Adaptive follow-up: Loan Hurdles", "How do financing bottlenecks specifically impact your student drop-off rate?", "About 32% of students who receive offer letters drop out because loan approvals take 4-6 weeks with public banks. Our competitor Leap Scholar offers pre-approved loans in 48 hours, which gives them a huge advantage.", 0, 1),
        ("Core differentiators vs alternatives", "How does MeetUniversity win against IDP and Leverage Edu?", "IDP pushes whichever university pays the highest commission; we do unconstrained matching based on student profile and career outcomes. Compared to Leverage Edu, we provide dedicated counselors rather than call center reps.", 0, 0),
        ("Important competitors & substitutes", "Who are your most aggressive competitors and what are their latest moves?", "Leap Scholar is our most aggressive competitor. They bundle fast pre-approved collateral-free student loans. Leverage Edu is spending heavily on Instagram and college campus fairs.", 0, 0),
        ("Major industry & market changes", "How are recent government policy changes in Canada and the UK impacting your applicant pipeline?", "Canada's 35% cap on international student permits created panic among diploma seekers. We are actively redirecting students toward Germany, Ireland, and the US where STEM pathways remain strong.", 0, 0),
        ("Material headwinds and tailwinds", "What external factors represent the greatest growth tailwinds for your model?", "The US 3-year STEM OPT extension allows Indian tech graduates to work for 3 years post-degree, making the US the undisputed #1 destination. Germany's low/zero tuition model is also exploding in popularity.", 0, 0),
        ("6–12 month growth priorities", "What key business milestones must the founding team achieve over the next 12 months?", "1. Grow our US STEM applicant base by 40%. 2. Launch an integrated pre-approved education loan desk with non-bank finance partners. 3. Double our institutional partnerships in Germany and Ireland.", 0, 0),
        ("Critical internal data sources", "What internal records or operational transcripts reflect customer sentiment best?", "Our weekly sales call objection logs, counselor notes from student drop-out exit interviews, and university admission liaison reports.", 0, 0),
        ("Key decisions the intelligence stack must empower", "What strategic decisions should the Monday Morning Brief help you make?", "Where to allocate our performance marketing budget each week, early warning of visa appointment rule changes, and tracking competitor promotional discounts and financing products.", 0, 0),
    ]

    for seq, (area, q, a, skipped, is_fu) in enumerate(interview_qas, 1):
        db.x(
            "INSERT INTO interview(company_id, seq, area, question, answer, skipped, is_followup, answered_at) VALUES(?,?,?,?,?,?,?,?)",
            (cid, seq, area, q, a, skipped, is_fu, now_iso)
        )

    # 6. Signal Stack Sources (22 sources across 4 quadrants)
    sources_data = [
        # Customers
        ("customers", "Hacker News: Study Abroad & Visa Discussions", "https://news.ycombinator.com/ask?q=study+abroad+visa", "api", "Captures organic developer & tech discussions on international student visas, admissions hurdles, and overseas STEM degrees.", 0.85),
        ("customers", "Google News: US & UK Student Visa Wait Times", "https://news.google.com/rss/search?q=student+visa+appointment+wait+times+india", "rss", "Monitors student anxiety and reports regarding embassy backlog and appointment availability.", 0.80),
        ("customers", "Reddit r/gradadmissions Discussion RSS", "https://www.reddit.com/r/gradadmissions/.rss", "rss", "Peer discussions on college shortlisting, acceptance rates, and university decision letters.", 0.75),
        ("customers", "Google News: Education Loan Rejection & Rates", "https://news.google.com/rss/search?q=education+loan+rejection+interest+rate+india", "rss", "Tracks student financing distress, collateral challenges, and lending alternatives.", 0.80),
        ("customers", "Student Housing Shortage Forum", "https://news.google.com/rss/search?q=international+student+housing+crisis+dublin+london", "rss", "Uncovers destination bottlenecks regarding housing costs and campus accommodation.", 0.75),
        ("customers", "Hacker News: Computer Science Graduate Programs", "https://news.ycombinator.com/ask?q=CS+masters+degree+US", "api", "Tracks candidate discussions comparing top universities for AI, ML, and Software Engineering.", 0.85),

        # Competitors
        ("competitors", "Leap Scholar Product & Financing Updates", "https://leapscholar.com/blog/feed", "rss", "Monitors our primary competitor's new financing products, loan interest rates, and admissions offerings.", 0.85),
        ("competitors", "Leverage Edu Corporate News & Fairs", "https://leverageedu.com/blog/feed", "rss", "Tracks university fair schedules, spot admissions partnerships, and digital acquisition campaigns.", 0.80),
        ("competitors", "IDP Education Global Recruitment News", "https://www.idp.com/india/news/rss", "rss", "Monitors the world's largest physical recruitment agency for operational shifts and destination advice.", 0.90),
        ("competitors", "Shiksha Study Abroad Insights", "https://studyabroad.shiksha.com/feed", "rss", "Tracks competitor SEO content, university rankings, and student review trends.", 0.78),
        ("competitors", "UpGrad Abroad University Tie-ups", "https://www.upgrad.com/abroad/feed", "rss", "Monitors blended degree models and competing university degree pathway programs.", 0.80),
        ("competitors", "Yocket Study Abroad Platform Announcements", "https://yocket.com/feed", "rss", "Tracks community feature launches, profile evaluations, and counselor services.", 0.80),

        # Market
        ("market", "US Department of State: Visa Bulletin & Appointment News", "https://travel.state.gov/content/travel/en/News/visas-news.html", "page", "Official policy source for US F-1 student visa rules, interview waivers, and appointment slots.", 0.95),
        ("market", "UK Home Office: Student & Graduate Visa Policies", "https://www.gov.uk/government/organisations/uk-visas-and-immigration.atom", "rss", "Official UK immigration bulletins regarding post-study work routes and university compliance.", 0.95),
        ("market", "IRCC Canada: International Student Quotas & Rules", "https://www.canada.ca/en/immigration-refugees-citizenship/news.atom", "rss", "Mandatory tracking of Canadian federal study permit caps and provincial attestation letters.", 0.95),
        ("market", "DAAD Germany: Higher Education Admission Bulletins", "https://www.daad.de/en/rss", "rss", "Official German academic exchange service updates on English-taught degree admissions.", 0.90),
        ("market", "Australian Dept of Home Affairs: Subclass 500 Updates", "https://immi.homeaffairs.gov.au/news-subsite/rss", "rss", "Tracks Australian student visa financial requirements and genuine student assessments.", 0.95),
        ("market", "Reserve Bank of India: LRS Outward Remittance Guidelines", "https://rbi.org.in/scripts/BS_PressReleaseDisplay.aspx", "page", "Tracks currency transfer limits and tax collected at source (TCS) rules on tuition fees.", 0.90),

        # Internal
        ("internal", "Sales Objection & Support Call Log Feed", "internal://sales_calls/meetuniversity", "internal", "Weekly sales call transcripts, counselor notes, and customer objection records.", 0.95),
        ("internal", "University Liaison Weekly Admissions Notes", "internal://liaison/university_admissions", "internal", "Direct intelligence from university international offices regarding applicant conversion.", 0.90),
        ("internal", "Lost Deal & Competitor Discount Tracker", "internal://analytics/lost_deals", "internal", "Analysis of lost leads with competitor quotes and student exit rationales.", 0.90),
    ]

    source_ids = {}
    for cat, name, url, kind, reason, rel in sources_data:
        sid = db.x(
            "INSERT OR IGNORE INTO sources(company_id, category, name, url, kind, reason, reliability, status, health, created) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (cid, cat, name, url, kind, reason, rel, "approved", "healthy", now_iso)
        )
        source_ids[name] = sid

    # 7. Intelligence Items (12 rich signals with 6-factor scores across all quadrants)
    items_data = [
        (
            1, "market", "US Visa Policy",
            "US Embassy opens 250,000 additional visa appointment slots for Indian students and professionals",
            "https://travel.state.gov/content/travel/en/News/visas-news/us-embassy-india-releases-new-slots.html",
            "The US consular mission in India announced the release of 250,000 additional non-immigrant and F-1 student visa appointment slots to clear backlogs across New Delhi, Mumbai, and Hyderabad.",
            "US Consular Mission in India confirms release of 250,000 additional F-1 and B1/B2 appointment slots across consulates.",
            "Directly removes our #1 student bottleneck for spring and fall intakes. Anticipate a 30% surge in completed applications as appointment wait times drop.",
            "Admissions & Student Counseling", "Launch immediate campaign to fast-track pending student visa mock interviews and open appointment booking desks.",
            9.5, 9.2, 8.8, 0.95, 1.0, 0.9, 93.0, "opportunity", "primary_source"
        ),
        (
            2, "competitors", "Competitor Financing",
            "Competitor Leap Scholar launches instant pre-approved education loan with 9.25% fixed interest",
            "https://leapscholar.com/blog/instant-preapproved-student-loans",
            "Leap Scholar announced a partnership with major private credit funds offering collateral-free study abroad loans up to INR 60 lakhs with instant 48-hour digital approval.",
            "Leap Scholar rolled out instant 48-hour pre-approved student loan product up to INR 60 lakhs with collateral-free options.",
            "Poses direct existential threat to our student conversion rate. Our sales transcripts prove we lost 22 deals to Leap Scholar because students needed immediate funding.",
            "Financing Partnerships", "Accelerate our partnership with NBFC lending partners to launch a matching 48-hour pre-approved financing desk within 14 days.",
            9.2, 9.0, 8.5, 0.85, 0.9, 0.85, 90.5, "threat", "corroborated"
        ),
        (
            3, "market", "Canada Immigration",
            "Canada IRCC announces additional 10% reduction in international student study permits for 2026",
            "https://www.canada.ca/en/immigration-refugees-citizenship/news/2026/study-permit-cap-update.html",
            "Immigration Minister announced Canada will cap study permits to 405,000 in 2026, down 10% from 2025 targets, tightening post-graduate work permit eligibility.",
            "IRCC implements 10% further reduction on international student study permits and restricts PGWP eligibility.",
            "Forces immediate strategic pivot away from Canadian non-university diploma programs. Will dampen Canadian intake by an estimated 25%.",
            "Strategic Portfolio & Marketing", "Proactively guide prospective Canada applicants to STEM master's programs in Germany, Ireland, and the US.",
            8.8, 8.5, 7.8, 0.95, 0.85, 0.8, 86.0, "threat", "primary_source"
        ),
        (
            4, "internal", "Student Sales Objections",
            "Sales call transcripts reveal 38% of prospective Ireland STEM applicants cite Dublin accommodation crisis as primary barrier",
            "internal://sales_calls/meetuniversity#batch-nov",
            "Analysis of 240 sales consultation calls indicates that while interest in Irish university master's degrees rose 50%, 38% of offer holders hesitate due to lack of housing in Dublin.",
            "Sales transcript analysis: 38% of accepted Ireland candidates cite inability to secure student housing near Dublin campuses as dealbreaker.",
            "Threatens to derail our strong Ireland conversion funnel despite high student intent and favorable post-study work rights.",
            "Student Experience & Operations", "Partner with verified student housing aggregators (e.g. AmberStudent) to offer pre-reserved Dublin accommodation vouchers.",
            9.0, 8.2, 8.2, 0.95, 0.9, 0.85, 87.5, "threat", "primary_source"
        ),
        (
            5, "market", "Germany Higher Ed",
            "German universities report 28% increase in international enrollments for English-taught AI and Engineering master's",
            "https://www.daad.de/en/news/german-universities-stem-enrollment-surge-2026",
            "DAAD published data showing English-taught graduate programs in public universities reached record 140,000 international students, driven by zero tuition fees.",
            "DAAD reports 28% enrollment surge in English-taught STEM graduate degrees across German public universities.",
            "Massive cost-conscious tailwind for Indian engineering students seeking world-class degrees without prohibitive 50-lakh loan burdens.",
            "European Admissions Team", "Add 20 German public universities to our direct recommendation portal and launch a 'Study Free in Germany' webinar series.",
            8.4, 7.8, 7.0, 0.90, 0.8, 0.75, 80.0, "opportunity", "primary_source"
        ),
        (
            6, "competitors", "Leverage Edu",
            "Leverage Edu partners with 15 UK Russell Group universities for on-the-spot admissions tours across Tier-2 Indian cities",
            "https://leverageedu.com/blog/russell-group-spot-admissions-tour",
            "Leverage Edu kicked off a 12-city roadshow with university delegates from top UK institutions granting conditional offer letters on the spot to qualifying students.",
            "Leverage Edu hosts on-the-spot conditional offer roadshow with 15 UK Russell Group universities in 12 Indian cities.",
            "Direct competitive encroachment into our Tier-2 applicant stronghold in Jaipur, Indore, and Lucknow.",
            "Field Recruitment & University Partnerships", "Host counter digital spot-offer sessions with partner universities offering application fee waivers.",
            8.0, 7.5, 7.2, 0.80, 0.8, 0.7, 77.0, "threat", "corroborated"
        ),
        (
            7, "customers", "Hacker News Discussions",
            "Hacker News discussion thread highlights frustration with slow 3-week response times on legacy study abroad counseling platforms",
            "https://news.ycombinator.com/item?id=38914820",
            "Developers discussing graduate school admissions noted that traditional overseas agencies take weeks to evaluate transcripts, favoring automated fast-turnaround services.",
            "HN tech community complains of 2-3 week delays in receiving profile evaluations from legacy study abroad agents.",
            "Validates our high-touch speed advantage. Students are willing to pay premium fees for same-day AI-assisted transcript assessment.",
            "Product & Counselor SLA", "Institute a guaranteed 24-hour university shortlist SLA for all STEM applicants to differentiate from legacy agencies.",
            8.2, 7.0, 6.8, 0.85, 0.8, 0.8, 76.5, "opportunity", "single_source"
        ),
        (
            8, "customers", "Student Community Sentiment",
            "Applicant surveys show 74% of Indian STEM candidates rank 3-year OPT visa as single most decisive factor in country selection",
            "https://news.google.com/rss/search?q=indian+students+stem+opt+preference",
            "Survey across 5,000 Indian graduate students revealed post-study work authorization outweighing university global ranking in 74% of final destination decisions.",
            "Student sentiment survey reveals 74% prioritizes post-study OPT work authorization over traditional prestige rankings.",
            "Confirms that our marketing messaging should lead with post-study earnings potential and STEM OPT eligibility rather than academic rankings.",
            "Performance Marketing", "Restructure Google & Meta ad headlines to spotlight '3-Year US STEM OPT Work Authorization' across all tech degree campaigns.",
            8.6, 8.0, 7.2, 0.80, 0.8, 0.75, 81.5, "opportunity", "corroborated"
        ),
        (
            9, "internal", "Lost Deal Exit Analysis",
            "Lost-deal exit interviews identify 22 qualified candidates lost directly to Leap Scholar due to upfront loan sanction speed",
            "internal://analytics/lost_deals#oct-nov-exit",
            "Counselor exit review of lost high-intent students revealed 22 candidates who had offer letters chose Leap Scholar solely because they received loan sanctions within 48 hours.",
            "22 qualified students lost to Leap Scholar directly attributable to their 48-hour digital loan approval advantage.",
            "Quantifies the direct revenue loss caused by our lack of an integrated fast-track lending desk (estimated INR 35 lakhs in lost commissions).",
            "Executive Leadership & Partnerships", "Sign partnership with InCred or Avanse to offer 48-hour pre-approval embedded into our application portal.",
            9.4, 8.8, 8.8, 0.95, 0.9, 0.85, 91.0, "threat", "primary_source"
        ),
        (
            10, "market", "UK Policy Review",
            "UK Home Office officially confirms retention of 2-year Graduate Route post-study work visa",
            "https://www.gov.uk/government/news/uk-graduate-route-visa-confirmed-retention",
            "Following the Migration Advisory Committee review, the UK government confirmed international graduates can continue working for 2 years (3 years for PhDs) after graduation.",
            "UK government accepts MAC findings and confirms retention of 2-year post-study Graduate Route without restrictions.",
            "Removes a major dark cloud that depressed UK applications by 20% over the summer. Anticipate immediate rebound in UK master's inquiries.",
            "Marketing & Admissions", "Broadcast urgent news update to over 15,000 prospective UK candidates confirming Graduate Route stability.",
            9.0, 8.4, 7.5, 0.95, 0.85, 0.8, 85.5, "opportunity", "primary_source"
        ),
        (
            11, "competitors", "IDP Global Moves",
            "IDP Education boosts India marketing expenditure by 40% targeting undergraduate enrollments in non-metro centers",
            "https://www.idp.com/india/news/expansion-tier-2",
            "IDP announced opening of 8 new physical counseling centers in Coimbatore, Patna, and Nagpur, backing it with extensive local newspaper and radio advertising.",
            "IDP expands physical presence into 8 new non-metro cities with 40% marketing budget increase.",
            "Increases student acquisition cost in Tier-2 cities for general undergraduate programs.",
            "Digital Growth Marketing", "Focus our non-metro targeting on specialized graduate STEM degrees where digital intent is high and IDP counselors are weak.",
            7.5, 7.0, 6.2, 0.90, 0.75, 0.65, 71.0, "threat", "single_source"
        ),
        (
            12, "customers", "Destination Shift",
            "Customer inquiries for European biotechnology and health science degrees rise 50% as alternatives to Canada",
            "https://news.ycombinator.com/item?id=38982310",
            "Discussions across admissions forums highlight students looking for affordable, high-quality biotech and pharma master's in Ireland and the Netherlands.",
            "Candidate discussions report 50% increase in inquiries for Irish and Dutch biotechnology master's degrees.",
            "High-margin opportunity to build specialized counseling pipelines for pharma and biotech graduates.",
            "Program Development", "Package 10 specialized European Biotechnology & Pharma degrees with partner institutions in Ireland and Sweden.",
            8.0, 7.4, 6.8, 0.85, 0.8, 0.75, 77.0, "opportunity", "corroborated"
        ),
    ]

    for item in items_data:
        (
            item_id, cat, subj, title, url, snippet, what_happened, why_it_matters,
            bus_area, sugg_resp, rel, imp, urg, cred, rec, nov, score, sig_type, ver
        ) = item
        analysis_json = json.dumps({
            "what_happened": what_happened,
            "why_it_matters": why_it_matters,
            "business_area": bus_area,
            "suggested_response": sugg_resp,
            "reported_as_fact": ver == "primary_source"
        })
        db.x(
            "INSERT OR REPLACE INTO items(id, company_id, source_id, category, subject, title, url, snippet, published, discovered, dedupe_key, analysis, relevance, impact, urgency, source_reliability, evidence_strength, novelty, score, signal_type, verification, analyzed) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (item_id, cid, 1, cat, subj, title, url, snippet, week_ago, now_iso, f"meetuni-{item_id}", analysis_json, rel, imp, urg, cred, 0.9, nov, score, sig_type, ver, 1)
        )

    # 8. Monday Morning Brief (Markdown format with citations)
    brief_md = """# MeetUniversity: Monday Morning Brief
Period: 2026-11-08 to 2026-11-15 (last 7 days). Items considered: 12.

## Executive Summary
1. **US Embassy releases 250,000 additional visa appointments in India**: Directly resolves our primary operational bottleneck for prospective spring and fall students [1].
2. **Competitor Leap Scholar launches 48-hour pre-approved student loan product**: Direct competitive threat that has already cost us 22 high-value student enrollments [2] [9].
3. **UK Government officially confirms retention of 2-year Graduate Route visa**: Eliminates policy uncertainty and establishes conditions for a major UK master's enrollment rebound [10].
4. **Canada implements further 10% international student permit reduction**: Forces immediate diversion of applicants toward STEM programs in Germany and Ireland [3].
5. **Sales transcripts expose student accommodation crisis in Dublin**: 38% of accepted Irish university applicants cite housing scarcity as their primary barrier to deposit payment [4].

## Customer Signals
Student demand across community forums and sales calls demonstrates that work authorization and loan approval speed now outweigh university prestige [8]. Prospective applicants report severe frustration with legacy agencies taking 2-3 weeks for university evaluations [7], creating an opening for our guaranteed same-day assessment SLA. Furthermore, inquiries for European biotechnology and engineering programs have surged 50% as alternatives to capped Canadian colleges [12].

- Applicant surveys confirm 74% of STEM applicants prioritize 3-year OPT work rights over university prestige [8]
- Community sentiment reveals widespread frustration over slow 2-3 week agency turnaround times [7]
- Customer inquiries for European biotechnology degrees up 50% following Canadian policy shifts [12]

## Competitor Intelligence
Leap Scholar has escalated its competitive pressure by rolling out instant collateral-free loans up to INR 60 lakhs with 48-hour approval [2]. Meanwhile, Leverage Edu is executing aggressive on-the-spot admission tours with 15 UK Russell Group colleges across non-metro Indian cities [6], and IDP Education has expanded its offline marketing spend by 40% [11].

- Leap Scholar rolls out instant 48-hour pre-approved loan product with 9.25% fixed rates [2]
- Leverage Edu organizes 12-city on-the-spot conditional offer roadshow with UK Russell Group universities [6]
- IDP Education expands physical center footprint across Tier-2 Indian cities with 40% ad budget increase [11]

## Market Intelligence
The external regulatory environment has produced major tailwinds for the US and UK alongside continued headwinds in Canada. The release of 250,000 US visa slots removes the visa appointment drought [1], and the UK's confirmation of the 2-year Graduate Route stabilizes student confidence [10]. Conversely, Canada's study permit cap was reduced by an additional 10% [3], while Germany's tuition-free English-taught graduate programs experienced a 28% enrollment surge [5].

- US Consular Mission releases 250,000 additional F-1 visa slots in India [1]
- UK Government confirms retention of 2-year post-study Graduate Route [10]
- Canada announces additional 10% international study permit cap reduction for 2026 [3]
- German universities report 28% international enrollment surge for English-taught master's degrees [5]

## Internal Business Intelligence
Internal customer log analysis confirms that financing delays and accommodation shortages represent our largest conversion leaks. 22 verified candidates with university offers were lost directly to Leap Scholar due to their 48-hour loan approval advantage [9]. In addition, 38% of accepted Irish candidates hesitate over Dublin housing shortages [4].

- Lost-deal analysis documents 22 candidates lost directly to Leap Scholar loan speed [9]
- Sales transcripts reveal 38% of Ireland applicants blocked by Dublin student housing scarcity [4]

## Opportunities Identified
1. **Launch Expedited US STEM Visa Booking Desk** (priority: high)
   - Impact: Capture immediate 30% conversion uplift from students previously blocked by appointment backlogs.
   - Next step: Fast-track visa documentation and open designated appointment monitoring slots for all enrolled students [1].
2. **Promote Re-stabilized UK 2-Year Graduate Route Campaign** (priority: high)
   - Impact: Immediate reactivation of over 15,000 stalled UK inquiries from summer 2026.
   - Next step: Deploy targeted email broadcast and webinar series highlighting confirmed post-study work rights [10].
3. **Scale Tuition-Free German Master's Program Pipeline** (priority: medium)
   - Impact: Attract cost-conscious engineering talent seeking degrees without 50-lakh loan debt.
   - Next step: Onboard 20 additional public German universities into direct portal shortlisting [5].

## Risks and Threats
- **Leap Scholar Financing Advantage** (urgency: high): Continued loss of enrolled students to Leap Scholar unless we match their 48-hour pre-approved loan capability [2] [9].
- **Dublin Student Housing Scarcity** (urgency: high): Potential loss of up to 40% of Irish university enrollments if students cannot secure accredited campus housing [4].
- **Canada Regulatory Shrinkage** (urgency: medium): Continued attrition in Canadian diploma enrollments requiring proactive pipeline diversion [3].

## Recommended Actions for This Week
- **Action**: Launch dedicated US STEM Visa Advisory desk to capture 250,000 released appointments.
  - Reason: Directly removes our #1 student conversion roadblock [1].
  - Owner: Head of Admissions
  - Priority: high
- **Action**: Finalize partner agreement with NBFC lenders to provide 48-hour pre-approved student loans.
  - Reason: Quantified loss of 22 students to Leap Scholar primarily due to loan sanction speed [2] [9].
  - Owner: CEO / Strategic Partnerships
  - Priority: high
- **Action**: Deploy automated email and WhatsApp broadcast to 15,000 prospective UK students regarding confirmed Graduate Route.
  - Reason: Re-engages stalled applicant pool following confirmed UK Home Office policy [10].
  - Owner: Growth Marketing Lead
  - Priority: high
- **Action**: Partner with AmberStudent to pre-reserve 50 student accommodation units in Dublin.
  - Reason: 38% of Irish offer holders cite housing scarcity as dealbreaker [4].
  - Owner: Student Services Head
  - Priority: medium

## What We Should Watch
- Emerging student loan interest rate adjustments across Indian state banks versus private NBFCs [2].
- Australian genuine student test enforcement trends and visa refusal patterns for semester 1 intake [8].

## Source Appendix
- **[1]** US Embassy in India: 250,000 Additional Visa Slots. *Source: US Department of State (Primary Source).* URL: https://travel.state.gov/content/travel/en/News/visas-news/us-embassy-india-releases-new-slots.html
- **[2]** Leap Scholar Instant Education Loan Launch. *Source: Leap Scholar (Corroborated).* URL: https://leapscholar.com/blog/instant-preapproved-student-loans
- **[3]** IRCC Canada 2026 International Student Cap Update. *Source: IRCC Canada (Primary Source).* URL: https://www.canada.ca/en/immigration-refugees-citizenship/news/2026/study-permit-cap-update.html
- **[4]** Internal Sales Objection Call Logs (Batch Nov). *Source: Internal Ingest (Primary Source).* URL: internal://sales_calls/meetuniversity#batch-nov
- **[5]** DAAD Germany 2026 International Enrollment Data. *Source: DAAD (Primary Source).* URL: https://www.daad.de/en/news/german-universities-stem-enrollment-surge-2026
- **[6]** Leverage Edu Russell Group Tour. *Source: Leverage Edu (Corroborated).* URL: https://leverageedu.com/blog/russell-group-spot-admissions-tour
- **[7]** Hacker News: Admissions Agency Delays. *Source: Hacker News (Single Source).* URL: https://news.ycombinator.com/item?id=38914820
- **[8]** STEM OPT Student Survey Data. *Source: Student Community (Corroborated).* URL: https://news.google.com/rss/search?q=indian+students+stem+opt+preference
- **[9]** Internal Lost Deal Exit Report (Oct-Nov). *Source: Internal Ingest (Primary Source).* URL: internal://analytics/lost_deals#oct-nov-exit
- **[10]** UK Home Office Graduate Route Decision. *Source: UK Home Office (Primary Source).* URL: https://www.gov.uk/government/news/uk-graduate-route-visa-confirmed-retention
- **[11]** IDP Non-Metro Expansion. *Source: IDP Education (Single Source).* URL: https://www.idp.com/india/news/expansion-tier-2
- **[12]** European Biotechnology Inquiries. *Source: Community Feeds (Corroborated).* URL: https://news.ycombinator.com/item?id=38982310
"""

    bid = db.x(
        "INSERT INTO briefs(company_id, kind, title, markdown, meta, created) VALUES(?,?,?,?,?,?)",
        (cid, "weekly", f"MeetUniversity Monday Morning Brief: week of {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", brief_md, json.dumps({"item_ids": list(range(1, 13)), "period": [str(week_ago[:10]), str(now_iso[:10])], "items_considered": 12}), now_iso)
    )

    # 9. Actions
    actions_list = [
        ("Launch dedicated US STEM Visa Advisory desk to capture 250,000 released appointments", "Directly removes our #1 student conversion roadblock [1]", "Head of Admissions", "high", "in_progress"),
        ("Finalize partner agreement with NBFC lenders to provide 48-hour pre-approved student loans", "Quantified loss of 22 students to Leap Scholar primarily due to loan sanction speed [2] [9]", "CEO / Partnerships", "high", "open"),
        ("Deploy automated email and WhatsApp broadcast to 15,000 prospective UK students regarding confirmed Graduate Route", "Re-engages stalled applicant pool following confirmed UK Home Office policy [10]", "Growth Marketing Lead", "high", "open"),
        ("Partner with AmberStudent to pre-reserve 50 student accommodation units in Dublin", "38% of Irish offer holders cite housing scarcity as dealbreaker [4]", "Student Services Head", "medium", "open"),
        ("Publish comparison matrix highlighting 1-on-1 human mentorship vs Leap Scholar automated bots", "Differentiates counselor quality and counters competitor marketing push [6]", "Growth Marketing", "medium", "done"),
    ]

    for act, rsn, own, pri, sta in actions_list:
        db.x(
            "INSERT INTO actions(company_id, brief_id, action, reason, owner, priority, status, created) VALUES(?,?,?,?,?,?,?,?)",
            (cid, bid, act, rsn, own, pri, sta, now_iso)
        )

    # 10. Runs log
    db.x(
        "INSERT INTO runs(company_id, kind, trigger, status, started, finished, summary, error) VALUES(?,?,?,?,?,?,?,?)",
        (cid, "weekly_brief", "manual", "success", week_ago, now_iso, "Successfully crawled 22 approved sources, evaluated 12 items, and compiled Monday Morning Brief with 5 executive initiatives.", None)
    )

    scheduler.schedule_company(cid)
    return {"id": cid, "name": "MeetUniversity", "brief_id": bid, "sources_count": len(sources_data), "items_count": len(items_data), "actions_count": len(actions_list)}
