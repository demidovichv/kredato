#!/usr/bin/env python3
"""Обновляет открытые ставки в site/assets/data/rates.json
и актуализирует дату в site/index.html.

Запуск: python scripts/update-deposit-rate.py
"""
import json
import re
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


def fetch_page(url: str, label: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  -> fetch failed {label}: {e}")
        return None


def extract_deposit_range(text: str) -> tuple[float, float] | None:
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
        return None
    return round(min(vals), 1), round(max(vals), 1)


def extract_mortgage_range(text: str) -> tuple[float, float] | None:
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
        return None
    return round(min(vals), 1), round(max(vals), 1)


def extract_loan_range(text: str) -> tuple[float, float] | None:
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
        return None
    return round(min(vals), 1), round(max(vals), 1)


def fmt(n: float) -> str:
    return f"{n:.1f}".replace(".", ",")


def safe_range(rng: tuple[float, float] | None, fallback: tuple[float, float], label: str) -> tuple[float, float]:
    if rng:
        print(f"  -> {label}: {fmt(rng[0])}% – {fmt(rng[1])}%")
        return rng
    print(f"  -> {label}: fallback {fmt(fallback[0])}% – {fmt(fallback[1])}%")
    return fallback


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
        "caption": f"Диапазоны — ориентир по открытым данным ЦБ и банков на {today_str}. Не является индивидуальной рекомендацией.",
        "debug_source": "bankiru_fallback",
    }
    RATES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {RATES}")


def patch_index(on_date: str):
    html = INDEX.read_text(encoding="utf-8")
    html = re.sub(
        r'(<h3>Ставки на )\d{2}\.\d{2}\.\d{4}( \(по открытым данным\)</h3>)',
        rf"\g<1>{on_date}\g<2>",
        html,
    )
    INDEX.write_text(html, encoding="utf-8")
    print(f"Patched {INDEX}")


def main() -> int:
    today_str = date.today().strftime("%d.%m.%Y")

    deposits_html = fetch_page(URL_DEPOSITS, "deposits")
    mortgage_html = fetch_page(URL_MORTGAGE, "mortgage")
    loans_html = fetch_page(URL_LOANS, "loans")

    deposits = safe_range(
        extract_deposit_range(BeautifulSoup(deposits_html, "lxml").get_text(" ", strip=True)) if deposits_html else None,
        (12.8, 14.5),
        "deposits",
    )
    mortgage = safe_range(
        extract_mortgage_range(BeautifulSoup(mortgage_html, "lxml").get_text(" ", strip=True)) if mortgage_html else None,
        (13.0, 17.0),
        "mortgage",
    )
    loans = safe_range(
        extract_loan_range(BeautifulSoup(loans_html, "lxml").get_text(" ", strip=True)) if loans_html else None,
        (15.0, 25.0),
        "loans",
    )

    write_rates_json(deposits, mortgage, loans)
    patch_index(today_str)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
