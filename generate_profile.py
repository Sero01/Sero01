"""Generate profile.svg — neofetch-style GitHub profile card.

Run by .github/workflows/update.yml daily to refresh uptime and GitHub stats.
Reads ascii.txt (the portrait) from the repo root.
"""
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
USER = "Sero01"
BIRTHDATE = date(2001, 5, 13)
WIDTH_CHARS = 72  # width of the info column in monospace chars

# ---------------------------------------------------------------- palette
BG = "#0d1117"
BORDER = "#30363d"
ASCII_C = "#c9d1d9"
TITLE_C = "#58a6ff"
KEY_C = "#ffa657"
HEADER_C = "#d2a8ff"
DOTS_C = "#484f58"
VALUE_C = "#c9d1d9"


def uptime() -> str:
    today = date.today()
    years = today.year - BIRTHDATE.year
    months = today.month - BIRTHDATE.month
    days = today.day - BIRTHDATE.day
    if days < 0:
        months -= 1
        prev = date(today.year, today.month, 1)
        from datetime import timedelta
        days += (prev - timedelta(days=1)).day
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months, {days} days"


def gh(url: str):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def stats() -> dict:
    out = {"repos": "18", "stars": "1", "commits": "239"}  # fallback: last known
    try:
        user = gh(f"https://api.github.com/users/{USER}")
        out["repos"] = str(user["public_repos"])
        repos = gh(f"https://api.github.com/users/{USER}/repos?per_page=100")
        out["stars"] = str(sum(r["stargazers_count"] for r in repos))
        commits = gh(f"https://api.github.com/search/commits?q=author:{USER}")
        out["commits"] = f'{commits["total_count"]:,}'
    except Exception:
        pass  # offline / rate-limited: keep fallbacks
    return out


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def kv_line(key: str, value: str) -> str:
    """'. Key: ...... value' padded to WIDTH_CHARS, as colored tspans."""
    ndots = WIDTH_CHARS - len(". ") - len(key + ":") - len(" " + value) - 1
    dots = "." * max(ndots, 2)
    return (
        f'<tspan fill="{DOTS_C}">. </tspan>'
        f'<tspan fill="{KEY_C}">{esc(key)}:</tspan>'
        f'<tspan fill="{DOTS_C}"> {dots} </tspan>'
        f'<tspan fill="{VALUE_C}">{esc(value)}</tspan>'
    )


def header_line(label: str) -> str:
    dashes = "─" * (WIDTH_CHARS - len(label) - 4)
    return (
        f'<tspan fill="{DOTS_C}">- </tspan>'
        f'<tspan fill="{HEADER_C}" font-weight="bold">{esc(label)}</tspan>'
        f'<tspan fill="{DOTS_C}"> {dashes}</tspan>'
    )


def title_line() -> str:
    label = "parvez@ahmed"
    dashes = "─" * (WIDTH_CHARS - len(label) - 2)
    return (
        f'<tspan fill="{TITLE_C}" font-weight="bold">{label}</tspan>'
        f'<tspan fill="{DOTS_C}"> {dashes}</tspan>'
    )


def build() -> str:
    s = stats()
    info = [
        title_line(),
        kv_line("OS", "Linux, Android"),
        kv_line("Uptime", uptime()),
        kv_line("Host", "Northern Trust"),
        kv_line("IDE", "VS Code, Claude Code"),
        "",
        kv_line("Languages.Programming", "Python, TypeScript, JavaScript, Java"),
        kv_line("Languages.Computer", "HTML, CSS, SQL, JSON, YAML"),
        kv_line("Languages.Real", "English, Hindi, Assamese"),
        "",
        kv_line("Hobbies.IRL", "Photography, Travelling"),
        kv_line("Hobbies.Perpetual", "Making Plans"),
        "",
        header_line("Contact"),
        kv_line("Email", "126ahmedparvez@gmail.com"),
        kv_line("LinkedIn", "itsparvezahmed"),
        "",
        header_line("GitHub Stats"),
        kv_line("Repos", f'{s["repos"]} | Stars: {s["stars"]}'),
        kv_line("Commits", s["commits"]),
    ]

    art = (HERE / "ascii.txt").read_text().rstrip("\n").split("\n")

    ascii_fs, info_fs = 11.5, 13
    ascii_lh, info_lh = 13, 19
    pad_x, pad_y = 36, 44
    art_w = 320
    info_x = pad_x + art_w + 30
    width = 1010
    height = pad_y + max(len(art) * ascii_lh, len(info) * info_lh) + pad_y - 6

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>',
        f'<g font-family="\'SFMono-Regular\',Consolas,\'Liberation Mono\',Menlo,monospace" '
        f'font-size="{ascii_fs}" fill="{ASCII_C}" xml:space="preserve">',
    ]
    y = pad_y
    for row in art:
        # browsers collapse runs of spaces even with xml:space; nbsp keeps alignment
        lines.append(f'<text x="{pad_x}" y="{y}">{esc(row).replace(" ", " ")}</text>')
        y += ascii_lh
    lines.append("</g>")

    lines.append(
        f'<g font-family="\'SFMono-Regular\',Consolas,\'Liberation Mono\',Menlo,monospace" '
        f'font-size="{info_fs}" xml:space="preserve">'
    )
    y = pad_y + 4
    for row in info:
        if row:
            lines.append(f'<text x="{info_x}" y="{y}">{row}</text>')
        y += info_lh
    lines.append("</g></svg>")
    return "\n".join(lines)


if __name__ == "__main__":
    (HERE / "profile.svg").write_text(build())
    print("wrote profile.svg")
