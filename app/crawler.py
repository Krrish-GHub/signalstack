import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser

from . import db, fetch


def _iso(value):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat(timespec="seconds")
    except Exception:
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat(timespec="seconds")
    except Exception:
        return None


def _snippet(text, limit=500):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _store(source, title, url, snippet, published):
    title = (title or "").strip()
    if not title or not url:
        return False
    key = fetch.normalize_url(url)
    dup = db.q("SELECT id FROM items WHERE company_id=? AND dedupe_key=?", (source["company_id"], key), one=True)
    if dup:
        return False
    same_title = db.q(
        "SELECT id FROM items WHERE company_id=? AND lower(title)=lower(?)", (source["company_id"], title), one=True
    )
    if same_title:
        return False
    db.x(
        "INSERT INTO items(company_id,source_id,category,subject,title,url,snippet,published,discovered,dedupe_key,source_reliability) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (
            source["company_id"], source["id"], source["category"], source.get("subject", ""), title[:300], url,
            snippet, published, db.now(), key, source["reliability"],
        ),
    )
    return True


def _crawl_feed(source):
    resp = fetch.get(source["url"])
    feed = feedparser.parse(resp.content)
    if feed.bozo and not feed.entries:
        raise RuntimeError("Feed could not be parsed")
    new = 0
    for entry in feed.entries[:40]:
        published = _iso(entry.get("published") or entry.get("updated"))
        if _store(source, entry.get("title"), entry.get("link"), _snippet(entry.get("summary", "")), published):
            new += 1
    return new


def _crawl_hn(source):
    resp = fetch.get(source["url"], accept="application/json")
    new = 0
    for hit in resp.json().get("hits", []):
        title = hit.get("title") or hit.get("story_title")
        link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        discussion = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        points = hit.get("points") or 0
        comments = hit.get("num_comments") or 0
        snippet = f"Hacker News discussion ({points} points, {comments} comments): {discussion}"
        if _store(source, title, link, snippet, _iso(hit.get("created_at"))):
            new += 1
    return new


def _crawl_page(source):
    resp = fetch.get(source["url"])
    text = fetch.clean_text(resp.text)
    digest = fetch.content_hash(text)
    snap = db.q("SELECT * FROM snapshots WHERE source_id=?", (source["id"],), one=True)
    db.x(
        "INSERT INTO snapshots(source_id,content_hash,text,fetched) VALUES(?,?,?,?) "
        "ON CONFLICT(source_id) DO UPDATE SET content_hash=excluded.content_hash,text=excluded.text,fetched=excluded.fetched",
        (source["id"], digest, text[:60000], db.now()),
    )
    if snap is None:
        return 0
    if snap["content_hash"] == digest:
        return 0
    old_sentences = set(re.split(r"(?<=[.!?])\s+", snap["text"] or ""))
    added = [s for s in re.split(r"(?<=[.!?])\s+", text) if s not in old_sentences and 40 < len(s) < 400]
    if not added:
        return 0
    title = f"Page changed: {source['name']}"
    url = f"{source['url']}#change-{digest[:10]}"
    snippet = " ".join(added[:4])[:700]
    return 1 if _store(source, title, url, "New or changed text: " + snippet, db.now()) else 0


def crawl_source(source):
    kind = source["kind"]
    if kind == "upload":
        return 0
    try:
        if kind == "rss":
            new = _crawl_feed(source)
        elif kind == "hn":
            new = _crawl_hn(source)
        else:
            new = _crawl_page(source)
    except fetch.Blocked as exc:
        db.x(
            "UPDATE sources SET health='blocked', last_error=?, last_checked=? WHERE id=?",
            (str(exc), db.now(), source["id"]),
        )
        return 0
    except Exception as exc:
        fails = (source["fail_count"] or 0) + 1
        health = "dead" if fails >= 3 else "failing"
        db.x(
            "UPDATE sources SET health=?, fail_count=?, last_error=?, last_checked=? WHERE id=?",
            (health, fails, str(exc)[:300], db.now(), source["id"]),
        )
        raise
    db.x(
        "UPDATE sources SET health='ok', fail_count=0, last_error=NULL, last_checked=?, "
        "last_new_item=CASE WHEN ? > 0 THEN ? ELSE last_new_item END WHERE id=?",
        (db.now(), new, db.now(), source["id"]),
    )
    return new


def crawl_company(company_id):
    sources = db.q(
        "SELECT * FROM sources WHERE company_id=? AND status='approved' AND kind!='upload'", (company_id,)
    )
    report = {"sources": len(sources), "new_items": 0, "failed": []}
    for source in sources:
        try:
            report["new_items"] += crawl_source(source)
        except Exception as exc:
            report["failed"].append({"source": source["name"], "error": str(exc)[:200]})
    return report
