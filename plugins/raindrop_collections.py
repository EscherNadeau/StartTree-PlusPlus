# Raindrop Collections — multi-tree plugin
# One drag installs ALL your Raindrop collections as separate trees.
# A picker lets you choose which ones to keep. Auto-syncs on a schedule.
#
# Drop into ~/dashboards/plugins/ then drag the file onto HomeBase.

import httpx

CREDENTIALS = {
    "RAINDROP_TOKEN": "Get yours at raindrop.io/settings/integrations → Create Test App → copy test token",
}

OPTIONS = {
    "selected": {
        "type":    "multiselect",
        "label":   "Collections",
        "default": [],
        "dynamic": True,   # choices come from the API, not hardcoded
    },
    "limit": {
        "type":    "number",
        "label":   "Items per collection",
        "default": 20,
        "min":     5,
        "max":     50,
    },
}

MULTI_TREE   = True
RAINDROP_TOKEN = ""
REFRESH_MS   = 3_600_000


async def _fetch_collections(headers):
    async with httpx.AsyncClient(timeout=15) as client:
        r1 = await client.get("https://api.raindrop.io/rest/v1/collections",          headers=headers)
        r2 = await client.get("https://api.raindrop.io/rest/v1/collections/childrens", headers=headers)
    root  = r1.json().get("items", []) if r1.status_code == 200 else []
    child = r2.json().get("items", []) if r2.status_code == 200 else []

    colls = {}
    for c in root:
        colls[c["_id"]] = {"name": c["title"], "path": c["title"], "count": c.get("count", 0)}
    for c in child:
        pid = (c.get("parent") or {}).get("$id")
        parent_path = colls.get(pid, {}).get("path", "")
        path = f"{parent_path}/{c['title']}" if parent_path else c["title"]
        colls[c["_id"]] = {"name": c["title"], "path": path, "count": c.get("count", 0)}
    return colls


async def plugin(options={}):
    selected = options.get("selected", [])
    limit    = int(options.get("limit", 20))
    headers  = {"Authorization": f"Bearer {RAINDROP_TOKEN}"}

    colls = await _fetch_collections(headers)

    # ── Preview mode: no selection yet → return all with counts, no links ──
    if not selected:
        return {
            "trees": [
                {"id": str(cid), "name": meta["path"], "count": meta["count"], "links": []}
                for cid, meta in colls.items()
            ],
            "preview": True,
        }

    # ── Fetch items only for selected collections ──
    trees = []
    async with httpx.AsyncClient(timeout=15) as client:
        for cid_str in selected:
            try:
                cid = int(cid_str)
            except (ValueError, TypeError):
                continue
            meta = colls.get(cid)
            if not meta:
                continue
            r = await client.get(
                f"https://api.raindrop.io/rest/v1/raindrops/{cid}",
                headers=headers,
                params={"perpage": limit, "sort": "-created"},
            )
            if r.status_code != 200:
                continue
            links = [
                {"label": item["title"], "url": item["link"]}
                for item in r.json().get("items", [])
                if item.get("title") and item.get("link")
            ]
            trees.append({"id": cid_str, "name": meta["path"], "links": links})

    return {"trees": trees}
