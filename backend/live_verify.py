"""
live_verify.py -- Live claim verification for TruthGuard (upgraded)
Cross-checks a claim against: Google Fact Check + live news (NewsAPI / Google News RSS)
+ optional Gemini AI reasoning. Keys via environment variables:
    setx GOOGLE_FACTCHECK_API_KEY "your_key"
    setx NEWSAPI_KEY "your_key"
    setx GEMINI_API_KEY "your_key"
"""
import os
import re
import html
import urllib.parse
import xml.etree.ElementTree as ET

GOOGLE_FACTCHECK_API_KEY = os.environ.get("GOOGLE_FACTCHECK_API_KEY", "")
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

_UA = {"User-Agent": "Mozilla/5.0 (TruthGuard verifier)"}

_STOP = set("""a an the of to in on for and or but is are was were be been being
this that these those it its as at by with from into about over after before
he she they we you i his her their our your my me us them if then than so such
not no yes will would can could should may might must have has had do does did
new news say says said report reports according breaking update updates""".split())


def _clean(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def _keywords(text, k=8):
    text = _clean(text)
    words = re.findall(r"[A-Za-z0-9']+", text)
    picked = []
    for w in words:
        lw = w.lower()
        if lw in _STOP or len(lw) < 3:
            continue
        picked.append(w)
    seen = set()
    out = []
    for w in picked:
        if w.lower() not in seen:
            seen.add(w.lower())
            out.append(w)
    return " ".join(out[:k]) if out else text[:120]


def check_factcheckers(query):
    if not GOOGLE_FACTCHECK_API_KEY:
        return {"available": False,
                "reason": "No Google Fact Check API key set (GOOGLE_FACTCHECK_API_KEY).",
                "claims": []}
    try:
        import requests
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {"query": query[:300], "key": GOOGLE_FACTCHECK_API_KEY,
                  "languageCode": "en", "pageSize": 5}
        r = requests.get(url, params=params, headers=_UA, timeout=15)
        r.raise_for_status()
        data = r.json()
        out = []
        for c in data.get("claims", [])[:5]:
            reviews = c.get("claimReview", [{}])
            rev = reviews[0] if reviews else {}
            out.append({
                "claim": _clean(c.get("text", "")),
                "claimant": _clean(c.get("claimant", "")),
                "rating": _clean(rev.get("textualRating", "")),
                "publisher": _clean((rev.get("publisher") or {}).get("name", "")),
                "url": rev.get("url", ""),
            })
        return {"available": True, "reason": None, "claims": out}
    except Exception as e:
        return {"available": False, "reason": f"Fact Check API error: {e}", "claims": []}


def search_newsapi(query):
    if not NEWSAPI_KEY:
        return None
    try:
        import requests
        url = "https://newsapi.org/v2/everything"
        params = {"q": query[:300], "apiKey": NEWSAPI_KEY, "language": "en",
                  "sortBy": "relevancy", "pageSize": 6}
        r = requests.get(url, params=params, headers=_UA, timeout=15)
        r.raise_for_status()
        arts = r.json().get("articles", [])
        return [{"title": _clean(a.get("title", "")),
                 "source": _clean((a.get("source") or {}).get("name", "")),
                 "url": a.get("url", ""),
                 "published": (a.get("publishedAt", "") or "")[:10],
                 "desc": _clean(a.get("description", ""))[:160]}
                for a in arts[:6]]
    except Exception:
        return None


def search_google_news_rss(query):
    try:
        import requests
        q = urllib.parse.quote(query[:300])
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        r = requests.get(url, headers=_UA, timeout=15)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        out = []
        for it in root.findall(".//item")[:6]:
            title = it.findtext("title", "")
            link = it.findtext("link", "")
            pub = it.findtext("pubDate", "")
            source_el = it.find("source")
            source = source_el.text if source_el is not None else ""
            out.append({"title": _clean(html.unescape(title)),
                        "source": _clean(source), "url": link,
                        "published": _clean(pub)[:16], "desc": ""})
        return out
    except Exception as e:
        return [{"title": f"(News search failed: {e})", "source": "", "url": "", "published": "", "desc": ""}]


def search_news(query):
    kw = _keywords(query)
    res = search_newsapi(kw) if NEWSAPI_KEY else None
    if res:
        return {"source_used": "NewsAPI", "query_used": kw, "articles": res}
    arts = search_google_news_rss(kw)
    real = [a for a in arts if a.get("url")]
    if not real:
        arts = search_google_news_rss(query)
    return {"source_used": "Google News", "query_used": kw, "articles": arts}


def gemini_reason(claim, ml_result, news_articles):
    if not GEMINI_API_KEY:
        return {"available": False,
                "reason": "No Gemini API key set (GEMINI_API_KEY).", "text": ""}
    try:
        import requests
        ml_line = ""
        if ml_result and ml_result.get("fake_probability") is not None:
            ml_line = f"An ML classifier rated it {ml_result['fake_probability']}% likely fake."
        headlines = "\n".join(f"- {a['title']} ({a.get('source','')})"
                              for a in (news_articles or [])[:5] if a.get("title"))
        prompt = (
            "You are a careful, neutral fact-checking assistant. Analyze this claim for "
            "signs of misinformation. Be concise (3-4 sentences). Do NOT claim certainty; "
            "explain the reasoning and what a reader should check.\n\n"
            f"CLAIM: \"{claim}\"\n\n"
            f"{ml_line}\n\n"
            f"Related news headlines found:\n{headlines or '(none found)'}\n\n"
            "Give: (1) whether the claim shows red flags of fake news and why, "
            "(2) whether reputable coverage seems to support it, "
            "(3) a one-line takeaway."
        )
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               "gemini-flash-latest:generateContent?key=" + GEMINI_API_KEY)
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=body, headers=_UA, timeout=25)
        if r.status_code == 429:
            import time
            time.sleep(20)  # rate limited - wait and retry once
            r = requests.post(url, json=body, headers=_UA, timeout=25)
        r.raise_for_status()
        data = r.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return {"available": True, "reason": None, "text": text}
    except Exception as e:
        msg = str(e)
        if GEMINI_API_KEY:
            msg = msg.replace(GEMINI_API_KEY, "***")
        return {"available": False, "reason": f"Gemini error: {msg}", "text": ""}


def verify(query, ml_result=None):
    query = _clean(query)
    fact = check_factcheckers(query)
    news = search_news(query)
    ai = gemini_reason(query, ml_result, news.get("articles"))

    signals = []
    if ml_result:
        p = ml_result.get("fake_probability")
        if p is not None:
            verdict = "likely FAKE" if ml_result.get("is_fake") else "likely CREDIBLE"
            signals.append(f"Our ML model rates this {verdict} ({p}% fake probability).")
    if fact["available"]:
        if fact["claims"]:
            ratings = [c["rating"] for c in fact["claims"] if c["rating"]]
            if ratings:
                signals.append(f"Professional fact-checkers reviewed similar claims "
                               f"(ratings: {', '.join(ratings[:3])}).")
            else:
                signals.append("Related fact-checks were found.")
        else:
            signals.append("No professional fact-check found for this exact claim.")
    else:
        signals.append("Fact-check database not queried (no Google Fact Check key).")
    n_articles = len([a for a in news["articles"] if a.get("url")])
    if n_articles == 0:
        signals.append("No matching news coverage found — unverified stories often lack "
                       "mainstream coverage. Try a more specific headline.")
    else:
        signals.append(f"Found {n_articles} related news article(s) via {news['source_used']}.")
    if ai["available"]:
        signals.append("AI reasoning added below.")

    return {"query": query, "ml": ml_result, "factcheck": fact,
            "news": news, "ai": ai, "summary": signals}


def status():
    return {"google_factcheck": bool(GOOGLE_FACTCHECK_API_KEY),
            "newsapi": bool(NEWSAPI_KEY), "gemini": bool(GEMINI_API_KEY),
            "google_news_rss": True}