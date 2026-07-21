#!/usr/bin/env python3
"""Проверяет текущую дату: если она больше last_synced → обновляет ставки по вкладам
с banki.ru/products/deposits/ и делает коммит+пуш в master.
"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing dep: {e}. Run: pip install beautifulsoup4 requests")
    sys.exit(2)

REPO = Path(r"F:\Email_Marketing_Repository")
INDEX = REPO / "site" / "index.html"
URL = "https://www.banki.ru/products/deposits/"
MARKER_FILE = REPO / ".last_rate_sync"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
re_tokens = re.compile(r"до\s+(\d{1,2},\d)\s*%")


def extract_deposit_rates(text: str) -> tuple[float, float]:
    vals = []

    for m in re_tokens.finditer(text):
        try:
            n = float(m.group(1).replace(",", "."))
            if 3.0 <= n <= 20.0:
                vals.append(n)
        except ValueError:
            pass

    if len(vals) < 2:
        for m in re.finditer(r"(\d{1,2},?\d)\s*%", text):
            try:
                n = float(m.group(1).replace(",", "."))
                if 3.0 <= n <= 20.0:
                    vals.append(n)
            except ValueError:
                pass

    vals = sorted(set(vals))
    if len(vals) < 2:
        raise RuntimeError(f"Insufficient rate data extracted: {vals}")
    return round(min(vals), 1), round(max(vals), 1)


def fetch_rates() -> tuple[float, float]:
    print(f"Fetching {URL} ...")
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text(" ", strip=True)
    lo, hi = extract_deposit_rates(text)
    print(f"Extracted deposit rates: {lo}% – {hi}%")
    return lo, hi


def fmt(n: float) -> str:
    return f"{n:.1f}".replace(".", ",")


def patch_index(lo: float, hi: float, on_date: str) -> tuple[str, str]:
    html = INDEX.read_text(encoding="utf-8")
    lo_s, hi_s = fmt(lo), fmt(hi)

    # 1) заголовок
    html = re.sub(
        r'(<h3>Ставки на )\d{2}\.\d{2}\.\d{4}( \(по открытым данным\)</h3>)',
        rf"\g<1>{on_date}\g<2>",
        html,
    )

    html = re.sub(
        r'(<span>Вклады</span><span class="val">)[\d,\.]+–[\d,\.]+%(</span></div>\s*<div class="row"><span>Ипотека</span>)',
        lambda m, lo=lo_s, hi=hi_s: f"{m.group(1)}{lo}–{hi}%{m.group(2)}",
        html,
        count=1,
    )

    # 3) calc-note
    html = re.sub(
        r'(Пример: на )\d{2}\.\d{2}\.\d{4}( средняя ставка по вкладам )\d{1,2},\d%',
        rf"Пример: на {on_date} средняя ставка по вкладам {lo_s}%",
        html,
    )

    # 4) bottom caption
    html = re.sub(
        r'(Диапазоны — ориентир по открытым данным банков и ЦБ на )\d{2}\.\d{2}\.\d{4}',
        rf"\g<1>{on_date}",
        html,
    )

    INDEX.write_text(html, encoding="utf-8")
    return lo_s, hi_s


def git_commit_push(msg: str):
    for c in [
        ["git", "add", str(INDEX)],
        ["git", "commit", "-m", msg],
        ["git", "push", "origin", "master"],
    ]:
        p = subprocess.run(c, cwd=REPO, check=True, text=True, capture_output=True)
        print(" ".join(c), p.stdout.strip())


def main():
    today_str = date.today().strftime("%d.%m.%Y")
    if MARKER_FILE.exists() and MARKER_FILE.read_text(encoding="utf-8").strip() == today_str:
        print(f"Already synced today ({today_str}), skip.")
        return 0

    lo, hi = fetch_rates()
    patch_index(lo, hi, today_str)
    git_commit_push(f"chore: ставки по вкладам {fmt(lo)}–{fmt(hi)}% на {today_str} (banki.ru)")
    print(f"Done. Synced to {today_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
