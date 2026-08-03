#!/usr/bin/env python3
"""Обновляет открытые ставки с banki.ru в site/assets/data/rates.json
и актуализирует дату/подпись в site/index.html.
Запуск: python scripts/update-deposit-rate.py
"""
import json
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing dep: {e}. Run: pip install beautifulsoup4 requests")
    sys.exit(2)

REPO = Path(__file__).resolve().parents[1]
INDEX = REPO / "site" / "index.html"
RATES = REPO / "site" / "assets" / "data" / "rates.json"
URL_DEPOSITS = "https://www.banki.ru/products/deposits/"
URL_MORTGAGE = "https://www.banki.ru/products/hypothec/"
URL_LOANS = "https://www.banki.ru/products/consumer-credit/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def extract_range(text: str) -> tuple[float, float]:
    vals = []
    for m in re.finditer(r"(\d{1,2}[,.]\d)\s*%", text):
        try:
            n = float(m.group(1).replace(",", "."))
            if 3.0 <= n <= 35.0:
                vals.append(n)
        except ValueError:
            pass
    vals = sorted(set(vals))
    if len(vals) < 2:
        raise RuntimeError(f"Insufficient rate data extracted: {vals}")
    return round(min(vals), 1), round(max(vals), 1)


def fetch_page(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text


def fetch_rates(url: str, label: str) -> tuple[float, float]:
    print(f"Fetching {label}: {url}")
    html = fetch_page(url)
    text = BeautifulSoup(html, "lxml").get_text(" ", strip=True)
    lo, hi = extract_range(text)
    print(f"  -> {lo}% – {hi}%")
    return lo, hi


def fmt(n: float) -> str:
    return f"{n:.1f}".replace(".", ",")


def write_rates_json(deposits: tuple[float, float], mortgage: tuple[float, float], loans: tuple[float, float]):
    today_str = date.today().strftime("%d.%m.%Y")
    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "periods": {
            "6m": {
                "deposits": f"{fmt(deposits[0])}–{fmt(deposits[1])}%",
                "mortgage": f"{fmt(mortgage[0])}–{fmt(mortgage[1])}%",
                "loans": f"{fmt(loans[0])}–{fmt(loans[1])}%",
            },
            "1y": {
                "deposits": f"{fmt(deposits[0])}–{fmt(deposits[1])}%",
                "mortgage": f"{fmt(mortgage[0])}–{fmt(mortgage[1])}%",
                "loans": f"{fmt(loans[0])}–{fmt(loans[1])}%",
            },
            "3y": {
                "deposits": f"{fmt(deposits[0])}–{fmt(deposits[1])}%",
                "mortgage": f"{fmt(mortgage[0])}–{fmt(mortgage[1])}%",
                "loans": f"{fmt(loans[0])}–{fmt(loans[1])}%",
            },
        },
        "caption": f"Диапазоны — ориентир по открытым данным банков и ЦБ на {today_str}. Не является индивидуальной рекомендацией.",
        "debug_source": "bankiru",
    }
    RATES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {RATES}")


def patch_index(deposits: tuple[float, float], on_date: str):
    html = INDEX.read_text(encoding="utf-8")
    html = re.sub(
        r'(<h3>Ставки на )\d{2}\.\d{2}\.\d{4}( \(по открытым данным\)</h3>)',
        rf"\g<1>{on_date}\g<2>",
        html,
    )
    # Обновляем только первый блок rates-ticker, остальные трогать не нужно
    html = re.sub(
        r'(<span>Вклады</span><span class="val">)[\d,\.]+–[\d,\.]+%(</span></div>\s*<div class="row"><span>Ипотека</span>)',
        lambda m, lo=fmt(deposits[0]), hi=fmt(deposits[1]): f"{m.group(1)}{lo}–{hi}%{m.group(2)}",
        html,
        count=1,
    )
    html = re.sub(
        r'(Пример: на )\d{2}\.\d{2}\.\d{4}( средняя ставка по вкладам )\d{1,2},\d%',
        rf"Пример: на {on_date} средняя ставка по вкладам {fmt(deposits[0])}%",
        html,
    )
    html = re.sub(
        r'(Диапазоны — ориентир по открытым данным банков и ЦБ на )\d{2}\.\d{2}\.\d{4}',
        rf"\g<1>{on_date}",
        html,
    )
    INDEX.write_text(html, encoding="utf-8")
    print(f"Patched {INDEX}")


def main():
    today_str = date.today().strftime("%d.%m.%Y")
    deposits = fetch_rates(URL_DEPOSITS, "deposits")
    mortgage = fetch_rates(URL_MORTGAGE, "mortgage")
    loans = fetch_rates(URL_LOANS, "loans")
    write_rates_json(deposits, mortgage, loans)
    patch_index(deposits, today_str)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
