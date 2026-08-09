"""source_credibility.py -- rate the credibility of a news domain (offline heuristic)."""
import re
from urllib.parse import urlparse

RELIABLE = {
    "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "npr.org", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "wsj.com", "economist.com", "bloomberg.com",
    "ft.com", "aljazeera.com", "thehindu.com", "indianexpress.com", "hindustantimes.com",
    "timesofindia.indiatimes.com", "ndtv.com", "cnn.com", "abcnews.go.com", "cbsnews.com",
    "nbcnews.com", "pbs.org", "nature.com", "sciencemag.org", "who.int", "nasa.gov", "cdc.gov",
}
SATIRE = {
    "theonion.com", "babylonbee.com", "clickhole.com", "thedailymash.co.uk",
    "fakingnews.com", "thespoof.com", "waterfordwhispersnews.com",
}
LOW_CREDIBILITY = {
    "infowars.com", "naturalnews.com", "beforeitsnews.com", "yournewswire.com",
    "worldnewsdailyreport.com", "empirenews.net", "nationalreport.net",
    "react365.com", "channel23news.com",
}


def _domain(text):
    text = (text or "").strip()
    if not text:
        return ""
    if not re.match(r"^https?://", text):
        text = "http://" + text
    host = urlparse(text).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _root(host):
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    if parts[-2] in ("co", "com", "org", "gov", "net", "ac") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def rate_source(url_or_domain):
    host = _domain(url_or_domain)
    if not host:
        return {"domain": "", "rating": "unknown", "score": 50, "message": "No domain provided."}
    root = _root(host)
    def hit(coll): return host in coll or root in coll
    if hit(RELIABLE):
        return {"domain": host, "rating": "reliable", "score": 90,
                "message": f"{root} is a well-known, generally reliable news source."}
    if hit(SATIRE):
        return {"domain": host, "rating": "satire", "score": 20,
                "message": f"{root} is a SATIRE/parody site — its stories are fiction, not real news."}
    if hit(LOW_CREDIBILITY):
        return {"domain": host, "rating": "low", "score": 10,
                "message": f"{root} has been flagged by fact-checkers for publishing false or misleading content."}
    return {"domain": host, "rating": "unknown", "score": 50,
            "message": f"{root} is not in our credibility database — evaluate the content carefully."}


def status():
    return {"reliable": len(RELIABLE), "satire": len(SATIRE), "low": len(LOW_CREDIBILITY)}