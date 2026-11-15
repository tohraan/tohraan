#!/usr/bin/env python3
"""Self-hosted stats + top-languages cards (no third-party card service).
Needs GH_TOKEN (Actions GITHUB_TOKEN works) or the gh CLI logged in.
Writes stats-card.svg and langs-card.svg."""
import json, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
USER = "tohraan"


def gh(*args):
    return json.loads(subprocess.run(["gh", "api", *args], capture_output=True, text=True, check=True).stdout)


def api(url, data=None):
    if data:
        return gh("graphql", "-f", f"query={data['query']}", "-f", f"u={data['variables']['u']}")
    return gh(url.replace("https://api.github.com/", ""))


q = """query($u:String!){user(login:$u){
 repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount}
 pullRequests{totalCount} issues{totalCount}
 contributionsCollection{totalCommitContributions restrictedContributionsCount contributionCalendar{totalContributions}}
 repositoriesContributedTo(first:1,contributionTypes:[COMMIT,PULL_REQUEST,ISSUE]){totalCount}}}"""
u = api("https://api.github.com/graphql", {"query": q, "variables": {"u": USER}})["data"]["user"]
repos = [r for r in api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
stars = sum(r["stargazers_count"] for r in repos)
langs = {}
for r in repos:
    for k, v in api(r["languages_url"]).items():
        langs[k] = langs.get(k, 0) + v

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
STYLE = ("<style>.a{opacity:0;animation:up .6s ease-out forwards}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
         ".b{transform-origin:left;transform:scaleX(0);animation:grow .9s cubic-bezier(.2,.7,.2,1) forwards}@keyframes grow{to{transform:scaleX(1)}}"
         ".t{fill:#e6edf3}.m{fill:#8b9bb0}.v{fill:#00e5a0;font-weight:700}</style>")

rows = [("Total stars", stars), ("Commits (last year)", u["contributionsCollection"]["totalCommitContributions"] + u["contributionsCollection"]["restrictedContributionsCount"]),
        ("Pull requests", u["pullRequests"]["totalCount"]), ("Issues", u["issues"]["totalCount"]),
        ("Public repos", u["repositories"]["totalCount"])]
W, H = 330, 60 + len(rows) * 28
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">{STYLE}',
     f'<rect width="{W}" height="{H}" rx="12" fill="#0d1117" stroke="#30363d"/>',
     '<text x="20" y="32" class="t" font-size="15" font-weight="700">Tohraan\'s GitHub Stats</text>',
     f'<rect x="20" y="42" width="{W-40}" height="2" rx="1" fill="#00e5a0" opacity=".5"/>']
for i, (k, v) in enumerate(rows):
    y = 72 + i * 28
    s.append(f'<g class="a" style="animation-delay:{i*.12:.2f}s"><circle cx="26" cy="{y-5}" r="4" fill="#00e5a0"/><text x="40" y="{y}" class="m" font-size="13">{k}</text><text x="{W-20}" y="{y}" class="v" font-size="14" text-anchor="end">{v:,}</text></g>')
s.append("</svg>")
(ROOT / "stats-card.svg").write_text("\n".join(s))

COL = {"Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26", "CSS": "#9b6bdf",
       "Swift": "#F05138", "Shell": "#89e051", "Java": "#b07219", "C": "#8b9bb0", "Dockerfile": "#384d54"}
tot = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
H2 = 60 + len(top) * 30
l = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H2}" viewBox="0 0 {W} {H2}" font-family="{FONT}">{STYLE}',
     f'<rect width="{W}" height="{H2}" rx="12" fill="#0d1117" stroke="#30363d"/>',
     '<text x="20" y="32" class="t" font-size="15" font-weight="700">Top Languages</text>',
     f'<rect x="20" y="42" width="{W-40}" height="2" rx="1" fill="#58a6ff" opacity=".5"/>']
for i, (k, v) in enumerate(top):
    y = 74 + i * 30; pct = v / tot * 100; bw = max(3, (W - 40) * pct / 100)
    c = COL.get(k, "#58a6ff")
    l.append(f'<g class="a" style="animation-delay:{i*.12:.2f}s"><text x="20" y="{y}" class="t" font-size="12.5">{k}</text><text x="{W-20}" y="{y}" class="m" font-size="12" text-anchor="end">{pct:.1f}%</text>'
             f'<rect x="20" y="{y+6}" width="{W-40}" height="6" rx="3" fill="#161b22"/><rect class="b" style="animation-delay:{.2+i*.12:.2f}s" x="20" y="{y+6}" width="{bw:.1f}" height="6" rx="3" fill="{c}"/></g>')
l.append("</svg>")
(ROOT / "langs-card.svg").write_text("\n".join(l))
print("ok", rows, [(k, round(v / tot * 100, 1)) for k, v in top])
