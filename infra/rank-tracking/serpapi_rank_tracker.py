#!/usr/bin/env python3
"""
SerpApi rank tracker for kredato.com.
Read-only. Fetches real SERP positions for Yandex/Google via SerpApi.
"""

import json
import os
import sys
import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = REPO / "reports" / "rank-tracking"
KEYWORDS_PATH = REPO / "reports" / "keywords" / "2026-08-05.json"


def load_keywords():
    if not KEYWORDS_PATH.exists():
        print(f"ERROR: Keywords file not found: {KEYWORDS_PATH}")
        sys.exit(1)
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    queries = [q["query"] for q in data.get("queries", []) if q.get("intent") in ("commercial", "informational")]
    print(f"Loaded {len(queries)} commercial/informational queries.")
    return queries


def get_api_key():
    api_key = os.environ.get("SERPAPI_API_KEY", "").strip()
    if not api_key:
        # fallback to config file
        config_path = REPO / "infra" / "rank-tracking" / "serpapi_config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            api_key = (cfg.get("serpapi_api_key") or "").strip()
    if not api_key:
        print("ERROR: SERPAPI_API_KEY env var not set and serpapi_config.json is empty.")
        sys.exit(1)
    return api_key


def fetch_yandex(api_key, query):
    params = {
        "engine": "yandex",
        "q": query,
        "region": "ru",
        "device": "desktop",
        "api_key": api_key,
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    organic = data.get("organic_results", [])
    position = None
    url = None
    for item in organic:
        if "kredato.com" in (item.get("link") or ""):
            position = item.get("position")
            url = item.get("link")
            break
    return {"query": query, "position": position, "url": url, "engine": "yandex"}


def fetch_google(api_key, query):
    params = {
        "engine": "google",
        "q": query,
        "gl": "ru",
        "hl": "ru",
        "device": "desktop",
        "api_key": api_key,
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    organic = data.get("organic_results", [])
    position = None
    url = None
    for item in organic:
        if "kredato.com" in (item.get("link") or ""):
            position = item.get("position")
            url = item.get("link")
            break
    return {"query": query, "position": position, "url": url, "engine": "google"}


def save_results(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    out_path = OUTPUT_DIR / f"serpapi_kredato_{ts}.json"
    payload = {
        "site": "kredato.com",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "data": records,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved SerpApi results to: {out_path}")
    return out_path


def main():
    print("=== SerpApi Rank Tracker (read-only) ===")
    api_key = get_api_key()
    queries = load_keywords()
    records = []
    for q in queries:
        try:
            y = fetch_yandex(api_key, q)
            g = fetch_google(api_key, q)
            records.append({
                "query": q,
                "yandex": {"position": y["position"], "url": y["url"]},
                "google": {"position": g["position"], "url": g["url"]},
            })
        except Exception as e:
            records.append({"query": q, "error": str(e)})
    save_results(records)


if __name__ == "__main__":
    main()
