#!/bin/bash
# Zen Dashboard Setup Script
# Run once: bash setup.sh

set -e

echo "🚀 Setting up Zen Dashboards..."

# Create directories
mkdir -p ~/dashboards/data
mkdir -p ~/dashboards/static

# Copy server files (run from the folder where you extracted the files)
cp server.py ~/dashboards/server.py

# Copy plugin examples (no-clobber — won't overwrite if you've added credentials)
mkdir -p ~/dashboards/plugins
cp -n plugins/*.json ~/dashboards/plugins/ 2>/dev/null || true
cp -n plugins/*.py   ~/dashboards/plugins/ 2>/dev/null || true

# Install Python deps
pip3 install fastapi uvicorn httpx feedparser --break-system-packages

# Install systemd user service
mkdir -p ~/.config/systemd/user
cp zen-dashboard.service ~/.config/systemd/user/zen-dashboard.service

# Enable and start
systemctl --user daemon-reload
systemctl --user enable zen-dashboard
systemctl --user start zen-dashboard

echo ""
echo "✅ Done! Server running at http://localhost:6969"
echo ""
echo "Test it: curl http://localhost:6969/api/health"
echo "Refresh a space: curl http://localhost:6969/api/refresh/linux"
echo ""
echo "Next step: copy your HTML dashboards into ~/dashboards/static/"
echo "Then point each Zen space to: http://localhost:6969/<space>.html"
