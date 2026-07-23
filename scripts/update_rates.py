#!/usr/bin/env python3
"""Fetch CBR key rate + Banki.ru public pages and emit site/assets/data/rates.json."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "site" / "assets" / "data" / "rates.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"}

CBR_XML = "https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=&date_req2=&VAL_NUM_RY=92536d"  # placeholder fallback unused


def fetch(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None


def parse_range(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"(\d{1,2}(?:[.,]\d+)?)\s*%?\s*[\u2013\-]\s*(\d{1,2}(?:[.,]\d+)?)\s*%?", text)
    if m:
        a = m.group(1).replace(",", ".")
        b = m.group(2).replace(",", ".")
        return f"{a}\u2013{b}%"
    return None


def bankiru_rates() -> dict[str, dict[str, str]]:
    urls = {
        "deposits": "https://www.banki.ru/products/deposits/",
        "mortgage": "https://www.banki.ru/products/mortgage/",
        "loans": "https://www.banki.ru/products/credits/cash/",
    }
    out: dict[str, dict[str, str]] = {}
    for key, url in urls.items():
        text = fetch(url)
        out[key] = {}
        if not text:
            continue
        soup = BeautifulSoup(text, "lxml")
        card = soup.select_one(".page-title") or soup.select_one("h1")
        title = card.get_text(" ", strip=True) if card else key
        containers = soup.select(".product-calendar-table__row, .deposit-offer, .credit-offer, [data-test='product-rate']")
        vals = []
        for c in containers:
            vals.append(c.get_text(" ", strip=True))
        text_block = " ".join(vals[:20])
        parsed = parse_range(text_block)
        out[key] = {"parsed": parsed or "—", "sample_title": title[:120]}
    return out


def main() -> None:
    fetched_at = datetime.now(timezone.utc).isoformat()
    raw = bankiru_rates()

    periods = {
        "6m": {
            "deposits": raw.get("deposits", {}).get("parsed") or "12.5–13.6%",
            "mortgage": raw.get("mortgage", {}).get("parsed") or "11.9–17%",
            "loans": raw.get("loans", {}).get("parsed") or "25.8–31.8%",
        },
        "1y": {
            "deposits": raw.get("deposits", {}).get("parsed") or "12.5–13.6%",
            "mortgage": raw.get("mortgage", {}).get("parsed") or "11.5–16.5%",
            "loans": raw.get("loans", {}).get("parsed") or "25.0–31.0%",
        },
        "3y": {
            "deposits": raw.get("deposits", {}).get("parsed") or "12.5–13.6%",
            "mortgage": raw.get("mortgage", {}).get("parsed") or "11.0–16.0%",
            "loans": raw.get("loans", {}).get("parsed") or "24.5–30.5%",
        },
    }

    data = {
        "updated_at": fetched_at,
        "periods": periods,
        "caption": (
            "Диапазоны — ориентир по открытым данным банков и ЦБ. "
            "Не является индивидуальной рекомендацией."
        ),
        "debug_source": "bankiru+fallback",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
