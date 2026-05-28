# TMDB — configurable plugin
# Drag into HomeBase to get a tree of movies or TV shows.
# Each drag creates a new instance with its own settings.
#
# Drop into ~/dashboards/plugins/ then point a tree at:
#   http://localhost:6969/api/plugin/<instance_id>

import httpx

CREDENTIALS = {
    "TMDB_API_KEY": "Get yours free at themoviedb.org/settings/api",
}

OPTIONS = {
    "fetch": {
        "type": "select",
        "label": "What",
        "default": "trending",
        "choices": ["trending", "top_rated", "upcoming", "now_playing"],
    },
    "media": {
        "type": "select",
        "label": "Type",
        "default": "movie",
        "choices": ["movie", "tv"],
    },
    "limit": {
        "type": "number",
        "label": "Results",
        "default": 10,
        "min": 1,
        "max": 20,
    },
}

TMDB_API_KEY = ""
REFRESH_MS   = 3_600_000


async def plugin(options={}):
    fetch = options.get("fetch", "trending")
    media = options.get("media", "movie")
    limit = int(options.get("limit", 10))

    if fetch == "trending":
        url = f"https://api.themoviedb.org/3/trending/{media}/week"
    elif fetch == "top_rated":
        url = f"https://api.themoviedb.org/3/{media}/top_rated"
    elif fetch == "upcoming":
        url = "https://api.themoviedb.org/3/movie/upcoming"
    else:
        url = "https://api.themoviedb.org/3/movie/now_playing"

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params={"api_key": TMDB_API_KEY, "language": "en-US"})
        r.raise_for_status()
        items = r.json().get("results", [])[:limit]

    return [
        {
            "label": ("⭐ " if item.get("vote_average", 0) >= 7 else "🎬 ")
                     + (item.get("title") or item.get("name", "")),
            "url": f"https://www.themoviedb.org/{media}/{item['id']}",
        }
        for item in items
    ]
