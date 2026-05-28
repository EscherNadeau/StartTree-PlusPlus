# TMDB Trending Movies — dev plugin example
#
# Shows the top trending movies of the day from The Movie Database.
#
# Setup:
#   1. Get a free API key at: https://www.themoviedb.org/settings/api
#   2. Set TMDB_API_KEY below
#   3. Drop this file into ~/dashboards/plugins/
#   4. Point a plugin tree at: http://localhost:6969/api/plugin/tmdb_trending

import httpx

CREDENTIALS = {
    "TMDB_API_KEY": "Get yours free at themoviedb.org/settings/api",
}

TMDB_API_KEY = ""   # injected at runtime from credentials.json
LIMIT        = 10
REFRESH_MS   = 3_600_000  # re-fetch hourly


async def plugin():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            "https://api.themoviedb.org/3/trending/movie/day",
            params={"api_key": TMDB_API_KEY, "language": "en-US"},
        )
        r.raise_for_status()
        movies = r.json()["results"][:LIMIT]

    return [
        {
            "label": f"{'⭐' if m.get('vote_average', 0) >= 7 else '🎬'} {m['title']}",
            "url":   f"https://www.themoviedb.org/movie/{m['id']}",
        }
        for m in movies
    ]
