#!/usr/bin/env python3
"""Проверяет текущую дату: если она больше last_synced → обновляет ставки по вкладам
с banki.ru/products/deposits/ и делает коммит+пуш в master.
"""
import subprocess
import sys
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


def last_synced() -> str | None:
    if MARKER_FILE.exists():
        return MARKER_FILE.read_text(encoding="utf-8").strip()
    return None


def mark_synced(d: str):
    MARKER_FILE.write_text(d, encoding="utf-8")


def extract_deposit_rates(text: str):
    """Извлекает диапазон ставок по вкладам из HTML text (aggressive fallback)."""
    vals = []

    # primary: "до 13,5%"
    for m in re_tokens.finditer(text):
        try:
            n = float(m.replace(",", "."))
            if 3.0 <= n <= 20.0:
                vals.append(n)
        except ValueError:
            pass

    # fallback: все числа X.Y% в диапазоне 3..20
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


# Precompile regex
re_tokens = re.compile(r"до\s+(\d{1,2},\d)\s*%")
import re  # noqa: E402


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


def patch_index(lo: float, hi: float) -> str:
    today = date.today().strftime("%d.%m.%Y")
    html = INDEX.read_text(encoding="utf-8")
    lo_s, hi_s = fmt(lo), fmt(hi)

    # 1) h3 date
    html = re.sub(
        r'(<h3>Ставки на )\d{2}\.\d{2}\.\d{4}( \(по открытым данным\)</h3>)',
        rf"\g<1>{today}\g<2>",
        html,
    )

    # 2) 6m deposits range
    def _repl_deposit(m, lo=lo_s, hi=hi_s):
        before = m.group(1)
        after = m.group(2)
        return f"{before}{lo}–{hi}%</span></div>{after}"

    html = re.sub(
        r'(<span>Вклады</span><span class="val">)[\d,\.]+–[\d,\.]+%(</span></div>\s*<div class="row"><span>Ипотека</span>)',
        _repl_deposit,
        html,
        count=1,
    )

    # 3) calc-note example
    html = re.sub(
        r'(Пример: на )\d{2}\.\d{2}\.\d{4}( средняя ставка по вкладам )\d{1,2},\d%',
        rf"Пример: на {today} средняя ставка по вкладам {lo_s}%",
        html,
    )

    # 4) bottom caption date
    html = re.sub(
        r'(Диапазоны — ориентир по открытым данным банков и ЦБ на )\d{2}\.\d{2}\.\d{4}',
        rf"\g<1>{today}",
        html,
    )

    INDEX.write_text(html, encoding="utf-8")
    mark_synced(today)
    print(f"Patched {INDEX}: {lo_s}–{hi_s}%, {today}")
    return today


def git_commit_push(msg: str):
    cmds = [
        ["git", "add", str(INDEX)],
        ["git", "commit", "-m", msg],
        ["git", "push", "origin", "master"],
    ]
    for c in cmds:
        p = subprocess.run(c, cwd=REPO, check=True, text=True, capture_output=True)
        print(" ".join(c), p.stdout.strip())


def main():
    from datetime import date
    today_str = date.today().strftime("%d.%m.%Y")
    prev = last_synced()
    if prev == today_str:
        print(f"Already synced today ({today_str}), skip.")
        return 0

    lo, hi = fetch_rates()
    patch_index(lo, hi)
    git_commit_push(f"chore: ставки по вкладам {fmt(lo)}–{fmt(hi)}% на {today_str} (banki.ru)")
    print(f"Done. Synced to {today_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
