# StartTree++

A terminal-style browser start page. Single-file, no build step, no framework.

![screenshot placeholder](screenshot.png)

## What it is

StartTree++ is a heavily expanded spiritual successor to [StartTree](https://github.com/Paul-Houser/StartTree) by Paul Houser. Where the original generates a static HTML file from a YAML config, this version is a fully interactive single-file app with live editing, a plugin system, and an optional backend for feeds and widgets.

## Features

- **Live editing** — add, rename, reorder trees and links directly in the UI, no config files or regeneration
- **Multi-page** — multiple pages with `←` / `→` to switch, each with its own layout and theme
- **Themes** — 6 built-in themes (gruvbox, nord, catppuccin, dracula, tokyo night, one dark), custom theme creation and import
- **Plugin system** — drop a `.json` or `.py` file onto the page to install a live-updating link feed
- **Configurable search** — pick from ddg, google, bing, brave, kagi, youtube, or add any custom engine with a `{q}` URL template
- **Quick-add** — hover any tree to add a link inline without opening settings
- **Export / import** — full config backup and restore as JSON

## Optional backend

`server.py` is a FastAPI backend (`localhost:6969`) that powers live feeds: Reddit, RSS, YouTube channel updates, weather, and Ollama AI summaries. It runs as a systemd user service.

```bash
# install deps
pip install fastapi uvicorn httpx feedparser

# run directly
python3 server.py

# or as a systemd service
cp zen-dashboard.service ~/.config/systemd/user/
systemctl --user enable --now zen-dashboard
```

## Usage

Just open `index.html` in your browser and set it as your new tab page. No build step, no dependencies beyond a Google Fonts CDN link.

Settings panel (⚙ top right):
- **links** tab — manage trees and links
- **page** tab — themes, colors, grid layout
- **search** tab — search engine picker and custom engines

## Credits

Inspired by [StartTree](https://github.com/Paul-Houser/StartTree) by [Paul Houser](https://github.com/Paul-Houser), which itself was inspired by a start page originally at notabug.org/nytly/home.
