#!/usr/bin/env python3
"""Build activity.svg from the public GitHub contribution API."""

import json
import urllib.request
from datetime import datetime
from pathlib import Path

USER = "MachineX41"
URL = f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last"
OUT = Path(__file__).resolve().parents[1] / "activity.svg"

LEVEL = {
    0: "#161b22",
    1: "#3d444d",
    2: "#8b949e",
    3: "#c9d1d9",
    4: "#ffffff",
}


def fetch() -> dict:
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "MachineX41-profile"})
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.load(res)
    except Exception:
        import subprocess
        raw = subprocess.check_output(["curl", "-fsSL", "-A", "MachineX41-profile", URL])
        return json.loads(raw)


def main() -> None:
    data = fetch()

    days = data["contributions"]
    total = data["total"]["lastYear"]
    active = sum(1 for d in days if d["count"] > 0)
    peak = max(d["count"] for d in days)

    columns = []
    for day in days:
        row = (datetime.strptime(day["date"], "%Y-%m-%d").weekday() + 1) % 7
        if row == 0 or not columns:
            columns.append([None] * 7)
        columns[-1][row] = day

    cell, gap, left, top = 11, 3, 16, 58
    width = left * 2 + len(columns) * cell + (len(columns) - 1) * gap
    height = top + 7 * cell + 6 * gap + 28

    rects = []
    for col, week in enumerate(columns):
        x = left + col * (cell + gap)
        for row, day in enumerate(week):
            if day is None:
                continue
            y = top + row * (cell + gap)
            color = LEVEL.get(day["level"], LEVEL[0])
            delay = col * 16
            rects.append(
                f'<rect class="c" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{color}" style="animation-delay:{delay}ms">'
                f'<title>{day["date"]}: {day["count"]}</title></rect>'
            )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total:,} contributions in the last year">
  <style>
    .c {{ opacity: 1; animation: rise 0.45s ease backwards; }}
    @keyframes rise {{ from {{ opacity: 0; }} }}
    text {{ font-family: Georgia, "Times New Roman", serif; fill: #ffffff; }}
    .sub {{ font-family: -apple-system, "Segoe UI", sans-serif; font-size: 13px; fill: #8b949e; }}
  </style>
  <rect width="100%" height="100%" fill="#0d1117"/>
  <text x="{left}" y="28" font-size="20">{total:,} contributions in the last year</text>
  <text class="sub" x="{left}" y="46">{active} active days · peak {peak} in one day · {USER}</text>
  {''.join(rects)}
</svg>
'''
    OUT.write_text(svg)
    print(f"wrote {OUT.name}: {total} contributions, {active} active days, {len(columns)} weeks")


if __name__ == "__main__":
    main()
