#!/bin/sh
# usage: render.sh page.html out.png width height
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=$3,$4 --virtual-time-budget=8000 --screenshot="$2" "file://$(cd "$(dirname "$1")" && pwd)/$(basename "$1")" 2>&1 | tail -n1
