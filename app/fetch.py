import hashlib
import os
import re
import threading
import time
import urllib.robotparser as robotparser
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

CONTACT = os.getenv("CRAWLER_CONTACT", "set-CRAWLER_CONTACT-in-env")
UA = f"SignalStackBot/1.0 (research monitor; contact: {CONTACT})"
MIN_GAP = float(os.getenv("CRAWL_DELAY_SECONDS", "2"))
MAX_BYTES = 2_000_000

_robots = {}
_last_hit = {}
_gate = threading.Lock()

PUBLIC_FEED_HOSTS = {
    "news.google.com",
    "hn.algolia.com",
    "api.stackexchange.com",
}


class Blocked(Exception):
    pass


def normalize_url(url):
    p = urlparse(url.strip())
    path = p.path.rstrip("/") or "/"
    query = "&".join(
        sorted(
            part
            for part in p.query.split("&")
            if part and not part.lower().startswith(("utm_", "fbclid", "gclid", "ref="))
        )
    )
    return urlunparse((p.scheme.lower(), p.netloc.lower().removeprefix("www."), path, "", query, ""))


def _robots_for(base):
    parser = _robots.get(base)
    if parser is not None:
        return parser
    parser = robotparser.RobotFileParser()
    try:
        resp = httpx.get(base + "/robots.txt", headers={"User-Agent": UA}, timeout=10, follow_redirects=True)
        if resp.status_code == 200:
            parser.parse(resp.text.splitlines())
        elif resp.status_code in (401, 403):
            parser.parse(["User-agent: *", "Disallow: /"])
        else:
            parser.parse([])
    except Exception:
        parser.parse([])
    _robots[base] = parser
    return parser


def allowed(url):
    p = urlparse(url)
    if p.netloc in PUBLIC_FEED_HOSTS:
        return True
    return _robots_for(f"{p.scheme}://{p.netloc}").can_fetch(UA, url)


def _wait(host):
    with _gate:
        gap = time.time() - _last_hit.get(host, 0)
        if gap < MIN_GAP:
            time.sleep(MIN_GAP - gap)
        _last_hit[host] = time.time()


def get(url, accept="text/html,application/xhtml+xml,application/xml,application/rss+xml,application/json;q=0.9,*/*;q=0.5"):
    if not allowed(url):
        raise Blocked(f"robots.txt disallows {url}")
    _wait(urlparse(url).netloc)
    resp = httpx.get(
        url,
        headers={"User-Agent": UA, "Accept": accept},
        timeout=20,
        follow_redirects=True,
    )
    if resp.status_code in (401, 403):
        raise Blocked(f"HTTP {resp.status_code}: access restricted, not bypassing")
    resp.raise_for_status()
    if len(resp.content) > MAX_BYTES:
        resp._content = resp.content[:MAX_BYTES]
    return resp


def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "form"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)


def page_title(html):
    soup = BeautifulSoup(html, "html.parser")
    return (soup.title.string or "").strip() if soup.title and soup.title.string else ""


def meta_description(html):
    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    return (tag.get("content") or "").strip() if tag else ""


def discover_feeds(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    feeds = []
    for link in soup.find_all("link", attrs={"rel": re.compile("alternate", re.I)}):
        kind = (link.get("type") or "").lower()
        if "rss" in kind or "atom" in kind:
            href = link.get("href")
            if href:
                feeds.append(urljoin(base_url, href.strip()).strip())
    return list(dict.fromkeys(feeds))


def internal_links(html, base_url, limit=8):
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(base_url).netloc.removeprefix("www.")
    keywords = ("about", "pricing", "product", "service", "solution", "how", "student", "partner", "blog", "news", "counsel", "university", "universities", "program")
    found = []
    for a in soup.find_all("a", href=True):
        raw = a["href"].strip()
        if not raw:
            continue
        href = urljoin(base_url, raw).split("#")[0].strip()
        p = urlparse(href)
        if p.netloc.removeprefix("www.") != host or p.scheme not in ("http", "https"):
            continue
        if any(k in href.lower() for k in keywords) and href not in found and href.rstrip("/") != base_url.rstrip("/"):
            found.append(href)
        if len(found) >= limit:
            break
    return found


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()
