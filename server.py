"""
Zen Dashboard Backend Server
Runs on localhost:6969 — starts on boot via systemd
"""

import json
import time
import asyncio
import inspect
import secrets
import importlib.util
import httpx
import feedparser
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Zen Dashboards API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)
CONFIG_FILE  = BASE / "config.json"
PLUGINS_DIR  = BASE / "plugins"
PLUGINS_DIR.mkdir(exist_ok=True)

# ─── DEFAULT CONFIG ────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "home": {
        "subreddits": ["linux", "unixporn", "gamedeals", "FREEMEDIAHECKYEAH", "musicproduction"],
        "rss": ["https://hnrss.org/frontpage", "https://www.phoronix.com/rss.php"],
        "weather_city": "Savannah,US"
    },
    "music": {
        "subreddits": ["edmproduction", "musicproduction", "synthesizers", "ableton", "FL_Studio"],
        "rss": [
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCftYkwXEKmSJSy6f8IjksfA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCSttPJRIqmNEFpiFEIFmnxg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCdcemy56JtVTrsFIOoqvV8g",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UConS8wqg9vGUkZ9wbWL1EfQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCzdjCKfcoEdWG0gtMQsFOKA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCqsuZqlG7SbYFWqIJFX36UQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCshObcm-nLhbu8MY50EZ5Ng",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCQxn3TZUa_gaLcZCKNy2oHg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCATH813AjPo_VLungWByWgg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCwjgHtqBBdbZTUs9joWedag",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCjizmVey_3sCKiyviOYlRfA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCU_ZKTv5Vc3DPsowV1s1B6A",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC6k-gn9VICNXUusw5_mS0wQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCXCXxhRVYvBOX45_gxr0iHA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCTjUJPovU9H7eDssyV7PlNw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCy_bbwPsSwNmdlYpExi9fYQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC4qCQBvERJMyWHrgCKHWVQA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCwirYC6rf7MdTS_lN2Fxc-w",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCChNhjW49smKB3zssiUjENg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCJ901NqoRaXMnIm7aOjLyuA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC8FsjyFryAutsPOzHbqwlsA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCV5aPToT6wmJeHwEknG-CFg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCxOT3aOmZpJAacl2ItUgHYQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCghAHbJNGErO0wtg6wO7_rQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCIcCXe3iWo6lq-iWKV40Oug",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC78mJyZPMa_OG08KLHjhODw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCJa14zeVf8p6clixTOIOVyQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCjfbkA4jJkJY5g0wbjuoZWA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCsIVrho83JfwUieSs_UKCmA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCFIvZYZp70IIrytPaF1eJrA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCux_ZnVANOo_wtcacduNjDw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC4ijq8Cg-8zQKx8OH12dUSw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCcCnNF8S3pqof3kHRCVj39Q",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC4m5liTHZ2vYFwbrRRi22Dw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC3vQEjRhwgH2HAOBKwLjxNA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCafxR2HWJRmMfSdyZXvZMTw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCACSN28q1DAo6qxd5xmHjiw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCi51nOLRe_BDGfkdrcOa3Tw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC6ST6JamqZNxh1hR3nzlcjg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC97YN7gYqtdk6z9jYHOn_lQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCkq1u0ZZCRq1EgZFUuIbh3A",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCYFa5RIwwfcvLRHhEVW5xsA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC4F05QAvbc3y7VN2rHSmjIg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC4K6tc2C0hauYw5SoXNtkbA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCyDZai57BfE_N0SaBkKQyXg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCA0fF9GUBL2Er_skkHKHzkQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCXQbZmsuSr3ndvN8NGlo7oQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCCXatwyYfIUPoZnA58NFPrg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCb8xLPa5RP8TnCsU7E5ASKQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCmHz7DQbbkcY_UoWY8bBJLw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCdbetV_5wxUnBTdb_d51qoA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCvtETS9e9d8OI4INyy_gZdw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCOojfmX4Wq3Ww-XP_IkvviQ",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UChzBUEBwODYh_13i4WkYnLg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCzsd4-oyHhNbAXfceOQ5HTw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCVtJOq_ziepf5MpjsTWxJeg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCBGh93s21DuE9xxb-6qBaXg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCpIlmpFJZ5qHz-NGCD97-Jg",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCmuwwGMbX5mowRw_GBjc6HA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCapo4XcpVOlTLkbKIDL0WlA",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCV4GZRrcATm3xCiWKTMeWsw",
        "https://www.youtube.com/feeds/videos.xml?channel_id=UC3XVLOUisrxzf-PDnaYEJjg"
]
    },
    "linux": {
        "subreddits": ["linux", "unixporn", "archlinux", "selfhosted", "linuxquestions"],
        "rss": ["https://www.phoronix.com/rss.php", "https://itsfoss.com/feed/"]
    },
    "pirate": {
        "subreddits": ["FREEMEDIAHECKYEAH", "Piracy", "DataHoarder", "trackers"],
        "rss": ["https://torrentfreak.com/feed/"]
    },
    "gaming": {
        "subreddits": ["pcgaming", "gamedeals", "patientgamers", "linux_gaming"],
        "rss": ["https://www.rockpapershotgun.com/feed", "https://feeds.arstechnica.com/arstechnica/gaming"]
    }
}


YT_NAMES = {
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCftYkwXEKmSJSy6f8IjksfA": "Abstractive Uncut",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCSttPJRIqmNEFpiFEIFmnxg": "Amfivol\u00eda",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCdcemy56JtVTrsFIOoqvV8g": "ANDREW HUANG",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UConS8wqg9vGUkZ9wbWL1EfQ": "Anthony Marinelli Music",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCzdjCKfcoEdWG0gtMQsFOKA": "AntiPattern",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCqsuZqlG7SbYFWqIJFX36UQ": "Bauke Top",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCshObcm-nLhbu8MY50EZ5Ng": "Benn Jordan",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCQxn3TZUa_gaLcZCKNy2oHg": "bespoke",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCATH813AjPo_VLungWByWgg": "Brendan Park",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCwjgHtqBBdbZTUs9joWedag": "Cableguys",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCjizmVey_3sCKiyviOYlRfA": "Carter Vail",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCU_ZKTv5Vc3DPsowV1s1B6A": "Cleanwithbea",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC6k-gn9VICNXUusw5_mS0wQ": "Coconut Brah",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCXCXxhRVYvBOX45_gxr0iHA": "CROW HILL",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCTjUJPovU9H7eDssyV7PlNw": "Dev Lemons",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCy_bbwPsSwNmdlYpExi9fYQ": "Devin Belanger",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC4qCQBvERJMyWHrgCKHWVQA": "Eirik Brandal",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCwirYC6rf7MdTS_lN2Fxc-w": "ekvyn",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCChNhjW49smKB3zssiUjENg": "Emily Hopkins",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCJ901NqoRaXMnIm7aOjLyuA": "Fallow",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC8FsjyFryAutsPOzHbqwlsA": "GrillsBare",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCV5aPToT6wmJeHwEknG-CFg": "Hamza Music",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCxOT3aOmZpJAacl2ItUgHYQ": "Harp Lady",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCghAHbJNGErO0wtg6wO7_rQ": "HPEIRTAZ",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCIcCXe3iWo6lq-iWKV40Oug": "In The Mix",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC78mJyZPMa_OG08KLHjhODw": "Jaden Williams",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCJa14zeVf8p6clixTOIOVyQ": "jakkuh",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCjfbkA4jJkJY5g0wbjuoZWA": "JHS Pedals",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCsIVrho83JfwUieSs_UKCmA": "John Summit",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCFIvZYZp70IIrytPaF1eJrA": "Jon Makes Beats",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCux_ZnVANOo_wtcacduNjDw": "Juice",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC4ijq8Cg-8zQKx8OH12dUSw": "Kara and Nate",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCcCnNF8S3pqof3kHRCVj39Q": "Kartik is here ",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC4m5liTHZ2vYFwbrRRi22Dw": "Koala McGiver",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC3vQEjRhwgH2HAOBKwLjxNA": "KWOOWK",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCafxR2HWJRmMfSdyZXvZMTw": "LOOK MUM NO COMPUTER",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCACSN28q1DAo6qxd5xmHjiw": "MOONBOY",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCi51nOLRe_BDGfkdrcOa3Tw": "More Codfish",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC6ST6JamqZNxh1hR3nzlcjg": "M\u0101rti\u0146\u0161",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC97YN7gYqtdk6z9jYHOn_lQ": "Noah Kellman",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCkq1u0ZZCRq1EgZFUuIbh3A": "NyxAndChill",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCYFa5RIwwfcvLRHhEVW5xsA": "phritz",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC4F05QAvbc3y7VN2rHSmjIg": "prod milus",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC4K6tc2C0hauYw5SoXNtkbA": "Reid Stefan",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCyDZai57BfE_N0SaBkKQyXg": "Rob Scallon",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCA0fF9GUBL2Er_skkHKHzkQ": "Sage Audio",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCXQbZmsuSr3ndvN8NGlo7oQ": "Sam Bentley",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCCXatwyYfIUPoZnA58NFPrg": "Schlep",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCb8xLPa5RP8TnCsU7E5ASKQ": "Splice",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCmHz7DQbbkcY_UoWY8bBJLw": "Switch Angel",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCdbetV_5wxUnBTdb_d51qoA": "Synthet",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvtETS9e9d8OI4INyy_gZdw": "The Majime Chronicles",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOojfmX4Wq3Ww-XP_IkvviQ": "True Cuckoo",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UChzBUEBwODYh_13i4WkYnLg": "Varsity Beats",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCzsd4-oyHhNbAXfceOQ5HTw": "Venus Theory",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCVtJOq_ziepf5MpjsTWxJeg": "Virtual Riot",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCBGh93s21DuE9xxb-6qBaXg": "Voel",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCpIlmpFJZ5qHz-NGCD97-Jg": "voxoku",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCmuwwGMbX5mowRw_GBjc6HA": "Will Hatton",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCapo4XcpVOlTLkbKIDL0WlA": "You Suck at Producing",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCV4GZRrcATm3xCiWKTMeWsw": "Your Pal Rob",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC3XVLOUisrxzf-PDnaYEJjg": "zuriel"
}

CACHE_TTL = 3600

# ─── CONFIG HELPERS ────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except:
            pass
    # First run — write defaults
    CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    return DEFAULT_CONFIG

def save_config(config: dict):
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

# ─── CACHE ─────────────────────────────────────────────────────────────────────

def cache_path(key: str) -> Path:
    return DATA / f"{key}.json"

def load_cache(key: str, ttl: int = CACHE_TTL):
    p = cache_path(key)
    if p.exists():
        data = json.loads(p.read_text())
        if time.time() - data.get("fetched_at", 0) < ttl:
            return data
    return None

def save_cache(key: str, data: dict):
    data["fetched_at"] = time.time()
    data["fetched_human"] = datetime.now().strftime("%b %d, %H:%M")
    cache_path(key).write_text(json.dumps(data, indent=2))

def bust_cache(key: str):
    p = cache_path(key)
    if p.exists():
        p.unlink()

# ─── FETCHERS ──────────────────────────────────────────────────────────────────

async def fetch_reddit(subreddits: list[str]) -> list[dict]:
    posts = []
    async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "zen-dashboard/1.0"}) as client:
        for sub in subreddits:
            try:
                r = await client.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=5")
                if r.status_code == 200:
                    for p in r.json()["data"]["children"]:
                        d = p["data"]
                        img = ""
                        try:
                            imgs = d.get("preview", {}).get("images", [])
                            if imgs:
                                ress = imgs[0].get("resolutions", [])
                                src = imgs[0].get("source", {})
                                chosen = src.get("url", "")
                                for res in ress:
                                    if res.get("width", 0) >= 320:
                                        chosen = res["url"]
                                        break
                                img = chosen.replace("&amp;", "&")
                        except:
                            pass
                        if not img:
                            thumb = d.get("thumbnail", "")
                            if thumb and thumb not in ("self", "default", "nsfw", "spoiler", "image", ""):
                                img = thumb
                        posts.append({
                            "title": d["title"],
                            "url": d.get("url", f"https://reddit.com{d.get('permalink','')}"),
                            "subreddit": d["subreddit"],
                            "score": d["score"],
                            "comments": d["num_comments"],
                            "permalink": f"https://reddit.com{d.get('permalink','')}",
                            "img": img,
                        })
            except Exception as e:
                print(f"Reddit error for r/{sub}: {e}")
    return sorted(posts, key=lambda x: x["score"], reverse=True)[:20]

async def fetch_single_rss(url: str) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        items = []
        # Use YT_NAMES lookup for YouTube feeds, fallback to feed title
        source = YT_NAMES.get(url) or feed.feed.get("title", url)
        is_yt = "youtube.com/feeds" in url
        for entry in feed.entries[:2]:
            img = ""
            link = entry.get("link", "")
            if is_yt and "v=" in link:
                vid = link.split("v=")[1].split("&")[0]
                img = f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg"
            else:
                try:
                    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                        img = entry.media_thumbnail[0].get("url", "")
                    elif hasattr(entry, "media_content") and entry.media_content:
                        for m in entry.media_content:
                            if m.get("type", "").startswith("image"):
                                img = m.get("url", "")
                                break
                except:
                    pass
            items.append({
                "title": entry.get("title", ""),
                "url": link,
                "source": source,
                "published": entry.get("published", ""),
                "is_youtube": is_yt,
                "img": img,
            })
        return items
    except Exception as e:
        print(f"RSS error for {url}: {e}")
        return []

async def fetch_rss(feeds: list[str]) -> list[dict]:
    # For large feed lists (e.g. 60+ YT channels), batch in groups of 10
    BATCH = 10
    all_items = []
    for i in range(0, len(feeds), BATCH):
        batch = feeds[i:i+BATCH]
        results = await asyncio.gather(*[fetch_single_rss(u) for u in batch])
        for r in results:
            all_items.extend(r)
    # Sort by published date if available, newest first
    return all_items[:40]

async def fetch_weather(city: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://wttr.in/{city}?format=j1")
            if r.status_code == 200:
                w = r.json()
                cur = w["current_condition"][0]
                return {
                    "temp_f": cur["temp_F"],
                    "temp_c": cur["temp_C"],
                    "desc": cur["weatherDesc"][0]["value"],
                    "humidity": cur["humidity"],
                    "feels_like_f": cur["FeelsLikeF"],
                    "city": city,
                }
    except Exception as e:
        print(f"Weather error: {e}")
    return {}

async def summarize_with_ollama(text: str, context: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": f"You are summarizing content for a {context} dashboard. Write a 2-3 sentence casual summary of what's trending based on these post titles. Be specific, mention actual topics. No bullet points, just flowing text.\n\nPosts:\n{text}",
                    "stream": False,
                }
            )
            if r.status_code == 200:
                return r.json().get("response", "").strip()
    except Exception as e:
        print(f"Ollama error: {e}")
    return ""

# ─── SPACE ROUTES ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

@app.get("/api/space/{space_name}")
async def get_space(space_name: str, refresh: bool = False):
    config = load_config()
    if space_name not in config:
        return {"error": f"Unknown space: {space_name}"}

    cache = load_cache(space_name)
    if cache and not refresh:
        return cache

    space_cfg = config[space_name]
    result = {"space": space_name}

    tasks = [fetch_reddit(space_cfg.get("subreddits", []))]
    tasks.append(fetch_rss(space_cfg.get("rss", [])))
    if "weather_city" in space_cfg:
        tasks.append(fetch_weather(space_cfg["weather_city"]))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    result["reddit"] = results[0] if not isinstance(results[0], Exception) else []
    result["rss"] = results[1] if not isinstance(results[1], Exception) else []
    if "weather_city" in space_cfg:
        result["weather"] = results[2] if not isinstance(results[2], Exception) else {}

    if result["reddit"]:
        titles = "\n".join(f"- {p['title']}" for p in result["reddit"][:10])
        result["ai_summary"] = await summarize_with_ollama(titles, space_name)
    else:
        result["ai_summary"] = ""

    save_cache(space_name, result)
    return result

@app.get("/api/refresh/{space_name}")
async def refresh_space(space_name: str):
    return await get_space(space_name, refresh=True)

# ─── CONFIG ROUTES ─────────────────────────────────────────────────────────────

@app.get("/api/config")
async def get_config():
    return load_config()

@app.get("/api/config/{space_name}")
async def get_space_config(space_name: str):
    config = load_config()
    if space_name not in config:
        return {"error": f"Unknown space: {space_name}"}
    return config[space_name]

@app.post("/api/config/{space_name}/subreddits/add")
async def add_subreddit(space_name: str, payload: dict = Body(...)):
    sub = payload.get("subreddit", "").strip().lstrip("r/")
    if not sub:
        return {"error": "no subreddit provided"}
    config = load_config()
    if space_name not in config:
        config[space_name] = {"subreddits": [], "rss": []}
    if sub not in config[space_name]["subreddits"]:
        config[space_name]["subreddits"].append(sub)
        save_config(config)
        bust_cache(space_name)
    return {"ok": True, "subreddits": config[space_name]["subreddits"]}

@app.post("/api/config/{space_name}/subreddits/remove")
async def remove_subreddit(space_name: str, payload: dict = Body(...)):
    sub = payload.get("subreddit", "").strip().lstrip("r/")
    config = load_config()
    if space_name in config and sub in config[space_name]["subreddits"]:
        config[space_name]["subreddits"].remove(sub)
        save_config(config)
        bust_cache(space_name)
    return {"ok": True, "subreddits": config[space_name].get("subreddits", [])}

@app.post("/api/config/{space_name}/rss/add")
async def add_rss(space_name: str, payload: dict = Body(...)):
    url = payload.get("url", "").strip()
    if not url:
        return {"error": "no url provided"}
    config = load_config()
    if space_name not in config:
        config[space_name] = {"subreddits": [], "rss": []}
    if url not in config[space_name]["rss"]:
        config[space_name]["rss"].append(url)
        save_config(config)
        bust_cache(space_name)
    return {"ok": True, "rss": config[space_name]["rss"]}

@app.post("/api/config/{space_name}/rss/remove")
async def remove_rss(space_name: str, payload: dict = Body(...)):
    url = payload.get("url", "").strip()
    config = load_config()
    if space_name in config and url in config[space_name].get("rss", []):
        config[space_name]["rss"].remove(url)
        save_config(config)
        bust_cache(space_name)
    return {"ok": True, "rss": config[space_name].get("rss", [])}

# ─── PLUGIN REGISTRY ───────────────────────────────────────────────────────────

PLUGINS_FILE = BASE / "plugins.json"
CREDS_FILE   = BASE / "credentials.json"

def load_plugins() -> dict:
    if PLUGINS_FILE.exists():
        try:
            return json.loads(PLUGINS_FILE.read_text())
        except:
            pass
    return {}

def save_plugins(plugins: dict):
    PLUGINS_FILE.write_text(json.dumps(plugins, indent=2))

def load_credentials() -> dict:
    if CREDS_FILE.exists():
        try:
            return json.loads(CREDS_FILE.read_text())
        except:
            pass
    return {}

def save_credentials(creds: dict):
    CREDS_FILE.write_text(json.dumps(creds, indent=2))

INSTANCES_FILE = BASE / "plugin_instances.json"

def load_instances() -> dict:
    if INSTANCES_FILE.exists():
        try: return json.loads(INSTANCES_FILE.read_text())
        except: pass
    return {}

def save_instances(instances: dict):
    INSTANCES_FILE.write_text(json.dumps(instances, indent=2))

def instance_uid(plugin_name: str) -> str:
    return plugin_name + "_" + secrets.token_hex(3)

def apply_creds(obj, creds: dict):
    """Recursively substitute {{KEY}} placeholders in a plugin definition dict."""
    if not creds:
        return obj
    text = json.dumps(obj)
    for key, val in creds.items():
        text = text.replace("{{" + key + "}}", val)
    return json.loads(text)

def get_array(data, path: str) -> list:
    """Resolve a dot-path to a list in nested data. e.g. 'data.items'"""
    if not path:
        return data if isinstance(data, list) else []
    for key in path.split('.'):
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return []
        if data is None:
            return []
    return data if isinstance(data, list) else ([data] if data else [])

def get_field(obj, path: str):
    """Resolve a dot-path to a scalar in a dict. e.g. 'metadata.title'"""
    if not path:
        return obj
    for key in path.split('.'):
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
        if obj is None:
            return None
    return obj

def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("hb_plugin_" + path.stem, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _normalize_links(raw) -> list[dict]:
    out = []
    for l in (raw or []):
        if isinstance(l, dict):
            out.append({
                "label": str(l.get("label") or l.get("title") or l.get("name") or ""),
                "url":   str(l.get("url")   or l.get("href")  or ""),
            })
    return out

def extract_schema(path: Path) -> dict:
    """Return OPTIONS schema + CREDENTIALS keys for a plugin file."""
    try:
        mod = _load_module(path)
        raw_opts = getattr(mod, "OPTIONS", {})
        # Verify JSON-serialisable
        json.dumps(raw_opts)
        return {
            "options":    raw_opts,
            "multi_tree": getattr(mod, "MULTI_TREE", False),
            "refresh_ms": getattr(mod, "REFRESH_MS", 900_000),
            "credentials": list(getattr(mod, "CREDENTIALS", {}).keys()),
        }
    except Exception as e:
        print(f"Schema extract error [{path.stem}]: {e}")
        return {"options": {}, "multi_tree": False, "refresh_ms": 900_000, "credentials": []}

async def run_script_plugin(path: Path, creds: dict = None, options: dict = None):
    """Import a .py plugin, inject credentials + options, call plugin().
    Returns list[dict] for single-tree or {trees:[...]} for multi-tree."""
    mod = _load_module(path)

    # Inject credentials
    if creds and hasattr(mod, "CREDENTIALS"):
        for key in mod.CREDENTIALS:
            if key in creds:
                setattr(mod, key, creds[key])

    # Call with or without options depending on signature
    sig = inspect.signature(mod.plugin)
    if options is not None and len(sig.parameters) > 0:
        result = await mod.plugin(options or {})
    else:
        result = await mod.plugin()

    # Multi-tree response
    if isinstance(result, dict) and "trees" in result:
        trees = []
        for t in result["trees"]:
            trees.append({
                "id":    str(t.get("id", t.get("name", ""))),
                "name":  str(t.get("name", "")),
                "count": t.get("count", len(t.get("links", []))),
                "links": _normalize_links(t.get("links", [])),
            })
        return {"trees": trees, "preview": result.get("preview", False)}

    return _normalize_links(result)

async def run_plugin(plugin: dict) -> list[dict]:
    src         = plugin.get("source", {})
    mapping     = plugin.get("map", {})
    limit       = int(plugin.get("limit", 20))
    url         = src.get("url", "")
    headers     = src.get("headers", {})
    src_type    = src.get("type", "json")

    if src_type == "rss":
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            r = await client.get(url)
            r.raise_for_status()
        feed        = feedparser.parse(r.text)
        label_field = mapping.get("label", "title")
        url_field   = mapping.get("url",   "link")
        links = []
        for entry in feed.entries[:limit]:
            label = entry.get(label_field, "")
            href  = entry.get(url_field,   "")
            if label or href:
                links.append({"label": str(label), "url": str(href)})
        return links
    else:
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            r = await client.get(url)
            r.raise_for_status()
        data        = r.json()
        arr         = get_array(data, mapping.get("array", ""))
        label_field = mapping.get("label", "title")
        url_field   = mapping.get("url",   "url")
        links = []
        for item in arr[:limit]:
            if not isinstance(item, dict):
                continue
            label = get_field(item, label_field)
            href  = get_field(item, url_field)
            if label is not None or href is not None:
                links.append({"label": str(label or ""), "url": str(href or "")})
        return links

@app.get("/api/plugins")
async def list_plugins():
    names = list(load_plugins().keys())
    for f in sorted(PLUGINS_DIR.glob("*.py")):
        if f.stem not in names:
            names.append(f.stem)
    return {"plugins": sorted(names)}

@app.post("/api/plugin")
async def register_plugin(payload: dict = Body(...)):
    name = payload.get("name", "").strip().lower().replace(" ", "_")
    if not name:
        return {"error": "plugin must have a name"}
    if not payload.get("source", {}).get("url"):
        return {"error": "plugin must have a source.url"}
    plugins = load_plugins()
    plugins[name] = payload
    save_plugins(plugins)
    bust_cache(f"plugin_{name}")
    return {"ok": True, "name": name}

@app.delete("/api/plugin/{name}")
async def delete_plugin(name: str):
    plugins = load_plugins()
    if name in plugins:
        del plugins[name]
        save_plugins(plugins)
        bust_cache(f"plugin_{name}")
    return {"ok": True}

@app.get("/api/plugin/{name}/schema")
async def get_plugin_schema(name: str):
    script = PLUGINS_DIR / f"{name}.py"
    if not script.exists():
        return {"error": f"Unknown plugin: {name}", "options": {}}
    return {"name": name, **extract_schema(script)}

@app.post("/api/plugin/instance")
async def create_instance(payload: dict = Body(...)):
    """Create a configured instance of a plugin. Returns the instance ID used as the tree URL."""
    plugin_name  = payload.get("plugin", "").strip().lower().replace(" ", "_").replace("-", "_")
    options      = payload.get("options", {})
    display_name = payload.get("display_name", plugin_name)

    if not plugin_name:
        return {"error": "plugin name required"}

    script = PLUGINS_DIR / f"{plugin_name}.py"
    if not script.exists() and plugin_name not in load_plugins():
        return {"error": f"Unknown plugin: {plugin_name}"}

    iid = instance_uid(plugin_name)
    instances = load_instances()
    instances[iid] = {"plugin": plugin_name, "display_name": display_name, "options": options}
    save_instances(instances)
    return {"ok": True, "instance_id": iid}

@app.get("/api/plugin/instance/{iid}")
async def get_instance(iid: str):
    instances = load_instances()
    if iid not in instances:
        return {"error": "Unknown instance"}
    inst   = instances[iid]
    script = PLUGINS_DIR / f"{inst['plugin']}.py"
    schema = extract_schema(script) if script.exists() else {}
    return {"instance_id": iid, **inst, "schema": schema}

@app.patch("/api/plugin/instance/{iid}")
async def update_instance(iid: str, payload: dict = Body(...)):
    """Update options for an existing instance."""
    instances = load_instances()
    if iid not in instances:
        return {"error": "Unknown instance"}
    if "options" in payload:
        instances[iid]["options"].update(payload["options"])
    if "display_name" in payload:
        instances[iid]["display_name"] = payload["display_name"]
    save_instances(instances)
    bust_cache(f"plugin_{iid}")
    return {"ok": True, "schema": extract_schema(PLUGINS_DIR / f"{instances[iid]['plugin']}.py")}

@app.get("/api/plugin/{name}")
async def get_plugin(name: str, refresh: bool = False):
    all_creds = load_credentials()
    instances = load_instances()

    # ── Instance (new-style) ──────────────────────────────────
    if name in instances:
        inst        = instances[name]
        plugin_name = inst["plugin"]
        options     = inst.get("options", {})
        creds       = all_creds.get(plugin_name, {})
        script      = PLUGINS_DIR / f"{plugin_name}.py"
        if not script.exists():
            return {"error": f"Plugin file missing: {plugin_name}", "links": []}
        ttl   = extract_schema(script).get("refresh_ms", 900_000) // 1000
        cache = load_cache(f"plugin_{name}", ttl=ttl)
        if cache and not refresh:
            resp = {"cached": True}
            resp.update({k: cache[k] for k in ("trees", "links") if k in cache})
            return resp
        try:
            result = await run_script_plugin(script, creds, options)
            payload = result if isinstance(result, dict) else {"links": result}
            save_cache(f"plugin_{name}", payload)
            return payload
        except Exception as e:
            print(f"Instance error [{name}]: {e}")
            return {"error": str(e), "links": []}

    # ── JSON registry plugin (legacy) ─────────────────────────
    plugins = load_plugins()
    creds   = all_creds.get(name, {})
    if name in plugins:
        plugin = apply_creds(plugins[name], creds)
        ttl    = int(plugin.get("refreshMs", 3600000)) // 1000
        cache  = load_cache(f"plugin_{name}", ttl=ttl)
        if cache and not refresh:
            return {"links": cache.get("links", []), "cached": True}
        try:
            links = await run_plugin(plugin)
            save_cache(f"plugin_{name}", {"links": links})
            return {"links": links}
        except Exception as e:
            print(f"Plugin error [{name}]: {e}")
            return {"error": str(e), "links": []}

    # ── Python script (legacy, no instance) ───────────────────
    script = PLUGINS_DIR / f"{name}.py"
    if script.exists():
        ttl   = extract_schema(script).get("refresh_ms", 900_000) // 1000
        cache = load_cache(f"plugin_{name}", ttl=ttl)
        if cache and not refresh:
            resp = {"cached": True}
            resp.update({k: cache[k] for k in ("trees", "links") if k in cache})
            return resp
        try:
            result = await run_script_plugin(script, all_creds.get(name, {}))
            payload = result if isinstance(result, dict) else {"links": result}
            save_cache(f"plugin_{name}", payload)
            return payload
        except Exception as e:
            print(f"Script plugin error [{name}]: {e}")
            return {"error": str(e), "links": []}

    return {"error": f"Unknown plugin: {name}", "links": []}

@app.post("/api/plugin/upload")
async def upload_plugin(payload: dict = Body(...)):
    """Save a plugin file + credentials. Returns schema so client can show options modal."""
    content     = payload.get("content", "")
    ptype       = payload.get("type", "json")
    name        = payload.get("name", "").strip().lower().replace(" ", "_").replace("-", "_")
    credentials = payload.get("credentials", {})

    if not name:
        return {"error": "name required"}

    if ptype == "script":
        if not content.strip():
            return {"error": "empty script"}
        dest = PLUGINS_DIR / f"{name}.py"
        dest.write_text(content)
        schema = extract_schema(dest)
    else:
        try:
            definition = json.loads(content)
        except Exception:
            return {"error": "invalid JSON"}
        if not definition.get("source", {}).get("url"):
            return {"error": "plugin must have source.url"}
        plugins = load_plugins()
        plugins[name] = definition
        save_plugins(plugins)
        schema = {}

    if credentials:
        all_creds = load_credentials()
        all_creds.setdefault(name, {}).update(credentials)
        save_credentials(all_creds)

    bust_cache(f"plugin_{name}")
    return {"ok": True, "name": name, "schema": schema}

# ─── PROXY ─────────────────────────────────────────────────────────────────────

@app.get("/api/proxy")
async def proxy_url(url: str):
    """Fetch any URL server-side to bypass CORS restrictions.
    Use in plugin trees: http://localhost:6969/api/proxy?url=https://...
    Returns JSON if the response is JSON, otherwise {text, status}.
    """
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True,
                                     headers={"User-Agent": "homebase-proxy/1.0"}) as client:
            r = await client.get(url)
            ct = r.headers.get("content-type", "")
            if "json" in ct:
                return r.json()
            return {"text": r.text, "status": r.status_code}
    except Exception as e:
        return {"error": str(e)}

# ─── STATIC ────────────────────────────────────────────────────────────────────

if (BASE / "static").exists():
    app.mount("/", StaticFiles(directory=BASE / "static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=6969, reload=False)
