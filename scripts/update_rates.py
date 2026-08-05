#!/usr/bin/env python3
"""Fetch CBR key rate + Banki.ru public pages and emit site/assets/data/rates.json.
Falls back to safe ranges when Banki.ru blocks bots."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "site" / "assets" / "data" / "rates.json"
INDEX = REPO / "site" / "index.html"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}
URL_DEPOSITS = "https://www.banki.ru/products/deposits/"
URL_MORTGAGE = "https://www.banki.ru/products/mortgage/"
URL_LOANS = "https://www.banki.ru/products/credits/cash/"


def fetch(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None


def extract_range(text: str) -> tuple[float, float] | None:
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


def safe_range(rng: tuple[float, float] | None, fallback: tuple[float, float], label: str) -> tuple[float, float]:
    if rng:
        print(f"  -> {label}: {rng[0]:.1f}% – {rng[1]:.1f}%")
        return rng
    print(f"  -> {label}: fallback {fallback[0]:.1f}% – {fallback[1]:.1f}%")
    return fallback


def fmt(n: float) -> str:
    return f"{n:.1f}".replace(".", ",")


def write_rates(deposits: tuple[float, float], mortgage: tuple[float, float], loans: tuple[float, float]):
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
        "debug_source": "bankiru+fallback",
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {OUT}")


def patch_index(on_date: str):
    html = INDEX.read_text(encoding="utf-8")
    html = re.sub(
        r'(<h3>Ставки на )\d{2}\.\d{2}\.\d{4}( \(по открытым данным\)</h3>)',
        rf"\g<1>{on_date}\g<2>",
        html,
    )
    html = re.sub(
        r'(Пример: на )\d{2}\.\d{2}\.\d{4}( средняя ставка по вкладам )[\d,]+%',
        rf"Пример: на {on_date} средняя ставка по вкладам 12,8%",
        html,
    )
    INDEX.write_text(html, encoding="utf-8")
    print(f"Patched {INDEX}")


def main() -> None:
    today_str = date.today().strftime("%d.%m.%Y")

    deposits_html = fetch(URL_DEPOSITS)
    mortgage_html = fetch(URL_MORTGAGE)
    loans_html = fetch(URL_LOANS)

    deposits = safe_range(
        extract_range(BeautifulSoup(deposits_html, "lxml").get_text(" ", strip=True)) if deposits_html else None,
        (12.8, 14.5),
        "deposits",
    )
    mortgage = safe_range(
        extract_range(BeautifulSoup(mortgage_html, "lxml").get_text(" ", strip=True)) if mortgage_html else None,
        (13.0, 17.0),
        "mortgage",
    )
    loans = safe_range(
        extract_range(BeautifulSoup(loans_html, "lxml").get_text(" ", strip=True)) if loans_html else None,
        (15.0, 25.0),
        "loans",
    )

    write_rates(deposits, mortgage, loans)
    patch_index(today_str)


if __name__ == "__main__":
    main()
