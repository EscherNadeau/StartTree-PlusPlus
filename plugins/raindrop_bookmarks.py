# Raindrop.io Bookmarks — authenticated API plugin example
#
# Pulls bookmarks from a Raindrop collection.
#
# Setup:
#   1. Get a token at: https://app.raindrop.io/settings/integrations
#      → Create Test App → copy the "Test token"
#   2. Set RAINDROP_TOKEN below
#   3. Optional: set COLLECTION_ID (0 = all bookmarks; find IDs in the Raindrop URL)
#   4. Drop this file into ~/dashboards/plugins/
#   5. Point a plugin tree at: http://localhost:6969/api/plugin/raindrop_bookmarks

import httpx

CREDENTIALS = {
    "RAINDROP_TOKEN": "Get yours at raindrop.io/settings/integrations → Create Test App → copy the test token",
}

RAINDROP_TOKEN = ""   # injected at runtime from credentials.json
COLLECTION_ID  = 0    # 0 = all bookmarks, or a specific collection ID from the Raindrop URL
LIMIT          = 20
SORT           = "-created"  # newest first; use "title" for alpha, "-score" for relevance
REFRESH_MS     = 3_600_000


async def plugin():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"https://api.raindrop.io/rest/v1/raindrops/{COLLECTION_ID}",
            headers={"Authorization": f"Bearer {RAINDROP_TOKEN}"},
            params={"perpage": LIMIT, "sort": SORT},
        )
        r.raise_for_status()
        items = r.json().get("items", [])

    return [
        {"label": item["title"], "url": item["link"]}
        for item in items
        if item.get("title") and item.get("link")
    ]
