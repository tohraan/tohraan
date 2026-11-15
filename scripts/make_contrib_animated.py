#!/usr/bin/env python3
"""Animated contribution graph: wave-in reveal, glowing hot days, live summary row.
Reads data/contributions.json, writes contrib-animated.svg."""
import datetime as dt, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
days = json.loads((ROOT / "data/contributions.json").read_text())["days"]
PAL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
C, G, L, T = 13, 3, 46, 56
first = dt.date.fromisoformat(days[0]["date"]); off = (first.weekday() + 1) % 7
weeks = (len(days) + off + 6) // 7
W = L + weeks * (C + G) + 24; H = T + 7 * (C + G) + 64
total = sum(d["count"] for d in days); best = max(days, key=lambda d: d["count"])
run = longest = 0
for d in days:
    run = run + 1 if d["count"] else 0; longest = max(longest, run)
cur = 0
for d in reversed(days):
    if d["count"]: cur += 1
    elif d is not days[-1]: break
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,monospace">',
 '<style>.c{opacity:0;animation:in .5s ease-out forwards}@keyframes in{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}'
 '.h{animation:in .5s ease-out forwards,glow 2.6s ease-in-out infinite}@keyframes glow{50%{filter:brightness(1.6)}}'
 '.t{fill:#8b9bb0;font-size:11px}.k{fill:#e6edf3;font-size:20px;font-weight:700}.s{animation:fade 1s 2.4s both}@keyframes fade{from{opacity:0}}'
 '.c,.h{transform-box:fill-box;transform-origin:center}</style>',
 f'<rect width="{W}" height="{H}" rx="14" fill="#0d1117" stroke="#30363d"/>',
 '<text class="t" x="20" y="28" fill="#00e5a0" style="fill:#00e5a0;font-size:13px">$ ./contributions.sh --live</text>']
last = -1
for i, d in enumerate(days):
    idx = i + off; w, r = divmod(idx, 7); dd = dt.date.fromisoformat(d["date"])
    if r == 0 and dd.month != last and dd.day <= 7:
        last = dd.month; o.append(f'<text class="t" x="{L+w*(C+G)}" y="{T-8}">{dd.strftime("%b")}</text>')
    cls = "h" if d["level"] >= 4 else "c"
    o.append(f'<rect class="{cls}" x="{L+w*(C+G)}" y="{T+r*(C+G)}" width="{C}" height="{C}" rx="3" fill="{PAL[d["level"]]}" style="animation-delay:{w*0.045:.2f}s"/>')
for r, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    o.append(f'<text class="t" x="12" y="{T+r*(C+G)+10}">{nm}</text>')
y = T + 7 * (C + G) + 28
for k, (num, lab) in enumerate(((total, "contributions / year"), (cur, "day streak"), (longest, "longest streak"), (best["count"], f"best day · {best['date']}"))):
    x = 20 + k * 170
    o.append(f'<text class="k s" x="{x}" y="{y}">{num}</text><text class="t s" x="{x}" y="{y+16}">{lab}</text>')
o.append('</svg>')
(ROOT / "contrib-animated.svg").write_text("\n".join(o))
print("ok", W, H, total, cur, longest)
