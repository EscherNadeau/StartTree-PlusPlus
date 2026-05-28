# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HomeBase is a browser new-tab/start page with two layers:

1. **`index.html`** — the main start page. Fully self-contained single-file HTML/CSS/JS. No build step, no dependencies beyond a Google Fonts CDN link. All state lives in `localStorage` under the key `homebase`.

2. **`server.py`** — a FastAPI backend running at `localhost:6969` as a systemd user service. `linux.html` and `music.html` fetch from it for Reddit posts, RSS feeds, YouTube channel updates, weather, and Ollama AI summaries.

## Running the server

```bash
# Start/stop/restart
systemctl --user start zen-dashboard
systemctl --user stop zen-dashboard
systemctl --user restart zen-dashboard

# Logs
journalctl --user -u zen-dashboard -f

# Direct run (dev)
cd ~/dashboards && python3 server.py

# Health check
curl http://localhost:6969/api/health

# Force-refresh a space's cache
curl http://localhost:6969/api/refresh/linux
```

The server runs from `~/dashboards/` (not this repo directory). `setup.sh` copies `server.py` there and installs the systemd service. Python deps: `fastapi uvicorn httpx feedparser`.

## Server architecture

- **Spaces**: named content buckets (`home`, `linux`, `music`, `gaming`, `pirate`). Each has subreddits + RSS feeds configured in `~/dashboards/config.json`.
- **Cache**: fetched data is cached as JSON files in `~/dashboards/data/<space_name>.json` with a 1-hour TTL (`CACHE_TTL = 3600`).
- **`GET /api/space/{name}`** — returns cached or freshly fetched data for a space: `{ reddit, rss, weather?, ai_summary }`.
- **`GET /api/refresh/{name}`** — busts cache and re-fetches.
- **Config CRUD routes** — `POST /api/config/{space}/subreddits/add|remove` and `/rss/add|remove` for in-browser config editing.
- **Ollama**: AI summaries call `localhost:11434` with model `qwen2.5:3b`. Failure is silent (returns `""`).
- **YouTube feeds**: RSS URLs are mapped to human names via the `YT_NAMES` dict in `server.py`. Adding a new channel requires adding its RSS URL to both `DEFAULT_CONFIG["music"]["rss"]` and `YT_NAMES`.

## index.html architecture

All logic is vanilla JS in one file. No framework, no build.

**Config shape** (stored in `localStorage`):
```js
{
  activePage: 0,
  customThemes: [],          // user-saved color themes
  pages: [{
    id, name, theme,         // theme: built-in ID or custom ID or 'custom'
    grid: { cols, rows },
    colors: { bg, bg1, bg2, bg3, br, br2, fg, fg2, fg3, yellow, green, cyan, orange, red, purple },
    trees: [{ id, name, links: [{ id, label, url }] }]
  }]
}
```

**Key functions:**
- `render()` — rebuilds the tree grid from `currentPage().trees`, sets `--gcols` CSS var
- `applyColors()` — sets all CSS custom properties from `currentPage().colors`
- `switchPage(delta)` — animates between pages, updates `cfg.activePage`
- `buildThemeSection(el)` — renders the theme picker tree (built-in + custom) + drop zone + collapsible color pickers
- `buildPanelColorGrid(el, defs)` — collapsible panel color pickers
- `renderSettings()` / `buildTreeCard()` / `buildLinkRow()` — settings panel tree CRUD with HTML5 drag-to-reorder

**Color system**: 16 CSS custom properties on `:root`. `applyColors()` sets them all at once. Built-in themes are in the `THEMES` array. Custom themes are in `cfg.customThemes` (global, not per-page).

**Multi-page**: `←`/`→` arrow keys switch pages when `document.activeElement === document.body`. Each page has independent trees, grid, and colors/theme.

**Plugin tree format** (planned): a tree with `pluginUrl` instead of manual links — fetches `{ links: [{label, url}] }` from a URL.

## Plugin system — DONE ✅

Two-tier plugin system. Drop a file into `~/dashboards/plugins/`, point a tree at `http://localhost:6969/api/plugin/<name>`.

### Tier 1 — Declarative JSON (anyone)
Drop a `.json` file into `~/dashboards/plugins/` **or** drag it onto the HomeBase window to auto-install + create a tree.

Format:
```json
{
  "name": "My Plugin",
  "source": { "type": "json|rss", "url": "...", "headers": {} },
  "map": { "array": "items", "label": "title", "url": "link" },
  "limit": 20,
  "refreshMs": 3600000
}
```

### Tier 2 — Python scripts (devs)
Drop a `.py` file into `~/dashboards/plugins/`. Expose an `async def plugin()` that returns `[{label, url}]`. Optional `REFRESH_MS` constant (default 15 min).

Examples: `plugins/tmdb_trending.py`, `plugins/raindrop_bookmarks.py`

### Proxy endpoint
`GET /api/proxy?url=<url>` — fetches any URL server-side to bypass CORS. Returns JSON if the response is JSON, otherwise `{text, status}`.

## TODO

### Next ideas
- Plugin browser / gallery UI in settings panel (list installed plugins, delete, re-fetch)
- `POST /api/plugin/{name}/refresh` shortcut (already works via `?refresh=true`)
- Support `pluginUrl` pointing at `/api/proxy?url=...` for external APIs with CORS issues

## CSS variable reference

| Variable | Role |
|---|---|
| `--bg` | page background |
| `--bg1` | settings header bg |
| `--bg2` | settings panel bg |
| `--bg3` | tree card bg |
| `--br` / `--br2` | border / border highlight |
| `--fg` / `--fg2` / `--fg3` | text / muted / dim |
| `--yellow` | tree category names, active state |
| `--cyan` | links |
| `--green` | username, add buttons |
| `--red` | delete actions |
| `--purple` | panel title |
| `--orange` | accent |
