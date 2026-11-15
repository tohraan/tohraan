#!/usr/bin/env python3
"""Generates the animated SVGs in assets/ (terminal, marquee, divider)."""
import pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

lines = [("$ whoami", "#00e5a0"), ("tohraan · founder @ triaxon · cs @ bits dubai", "#cdd9e5"),
 ("$ cat wins.txt", "#00e5a0"), ("1st  GDG Ideathon", "#ffd166"), ("1st  ACM-W Broken Brief", "#ffd166"),
 ("2nd  IEEE Campus Ops", "#c0c8d4"), ("3rd  Deriv AI Hackathon (agentic AI)", "#e0a96d"),
 ("$ ls ~/shipped", "#00e5a0"), ("bits-bazaar  orbit  brand-my-mac  cse-lab  flow-tools", "#79c0ff"),
 ("$ git log --oneline -3", "#00e5a0"), ("edf01d3 feat(dijkstra): implement Dijkstra Shortest Paths", "#d2a8ff"),
 ("0304fc0 test(lru_cache): cover LRU Cache", "#d2a8ff"), ("8c114f3 docs(trie): note complexity of Trie", "#d2a8ff")]
W, CH = 640, 8.1
H = 76 + len(lines) * 24 + 28
CYC = 22
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">',
 '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#0a1620"/></linearGradient></defs>',
 f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)" stroke="#30363d"/>',
 '<circle cx="26" cy="24" r="6" fill="#ff5f56"/><circle cx="46" cy="24" r="6" fill="#ffbd2e"/><circle cx="66" cy="24" r="6" fill="#27c93f"/>',
 f'<text x="{W/2}" y="29" fill="#7d8da1" font-size="13" text-anchor="middle">tohraan@github: ~</text>',
 f'<line x1="0" y1="44" x2="{W}" y2="44" stroke="#30363d"/>']
n = len(lines)
for i, (t, c) in enumerate(lines):
    y = 76 + i * 24
    t0 = 0.03 + i * (0.8 / n); t1 = t0 + 0.04
    w = len(t) * CH + 8
    o.append(f'<clipPath id="c{i}"><rect x="24" y="{y-16}" height="22" width="0"><animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0" keyTimes="0;{t0:.3f};{t1:.3f};0.95;1" dur="{CYC}s" repeatCount="indefinite"/></rect></clipPath>')
    o.append(f'<text x="24" y="{y}" fill="{c}" font-size="13.5" clip-path="url(#c{i})" xml:space="preserve">{t}</text>')
o.append(f'<rect x="24" y="{76+n*24-16}" width="9" height="17" fill="#00e5a0"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect></svg>')
(OUT / "terminal.svg").write_text("\n".join(o))

items = ["TypeScript","React 19","Next.js 16","Node.js","PostgreSQL","Supabase","Tailwind v4","Python","Docker","n8n","Remotion","HyperFrames","ffmpeg","Tailscale","Claude Code","MCP","GitHub Actions","Stripe"]
cols = ["#3178c6","#61dafb","#ffffff","#5fa04e","#336791","#3ecf8e","#38bdf8","#ffd43b","#2496ed","#ea4b71","#0b84f3","#a371f7","#4ade80","#9ca3af","#d97757","#58a6ff","#2088ff","#635bff"]
x = 0; pills = []
for t, c in zip(items, cols):
    w = len(t) * 9.4 + 44
    pills.append(f'<g transform="translate({x:.0f},14)"><rect width="{w:.0f}" height="40" rx="20" fill="#0d1117" stroke="{c}" stroke-opacity=".55"/><circle cx="20" cy="20" r="5" fill="{c}"/><text x="34" y="25.5" fill="#e6edf3" font-size="15" font-weight="600">{t}</text></g>')
    x += w + 14
tot = x; vw = 1280
m = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{vw}" height="68" viewBox="0 0 {vw} 68" font-family="{MONO}">',
 '<defs><linearGradient id="f" x1="0" x2="1"><stop offset="0" stop-color="#0d1117"/><stop offset=".08" stop-color="#0d1117" stop-opacity="0"/><stop offset=".92" stop-color="#0d1117" stop-opacity="0"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
 f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{tot:.0f} 0" dur="38s" repeatCount="indefinite"/>',
 "".join(pills), f'<g transform="translate({tot:.0f},0)">' + "".join(pills) + '</g>', f'<g transform="translate({2*tot:.0f},0)">' + "".join(pills) + '</g></g>',
 f'<rect width="{vw}" height="68" fill="url(#f)"/></svg>']
(OUT / "marquee.svg").write_text("".join(m))

(OUT / "divider.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="14" viewBox="0 0 1280 14">
<defs><linearGradient id="d" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="640" y2="0" spreadMethod="repeat">
<stop offset="0" stop-color="#00e5a0" stop-opacity="0"/><stop offset=".5" stop-color="#00e5a0"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="640 0" dur="4s" repeatCount="indefinite"/></linearGradient></defs>
<rect y="6" width="1280" height="2" rx="1" fill="#21262d"/><rect y="5" width="1280" height="4" rx="2" fill="url(#d)"/></svg>''')
print("ok")
