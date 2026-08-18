#!/usr/bin/env python3
"""
Yandex.Webmaster rank tracker for kredato.com.
Read-only. Fetches query-level average positions via Yandex Webmaster API v4.

Docs: https://yandex.ru/dev/webmaster/doc/dg/reference/popular.html
"""

import json
import os
import sys
import datetime
from pathlib import Path
import urllib.request
import urllib.error

# ---------- Configuration ----------
REPO = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO / "infra" / "rank-tracking" / "yandex_config.json"
OUTPUT_DIR = REPO / "reports" / "rank-tracking"
KEYWORDS_PATH = REPO / "reports" / "keywords" / "2026-08-05.json"

HOST = "https://kredato.com"
USER_ID = ""  # Yandex user ID — set via config or env
OAUTH_TOKEN = ""  # OAuth token with webmaster:read scope

# Yandex returns avg_position in popular-queries endpoint. Max ~1000 rows/request.


def load_keywords():
    if not KEYWORDS_PATH.exists():
        print(f"ERROR: Keywords file not found: {KEYWORDS_PATH}")
        sys.exit(1)
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    queries = [q["query"] for q in data.get("queries", []) if q.get("intent") in ("commercial", "informational")]
    print(f"Loaded {len(queries)} commercial/informational queries.")
    return queries


def load_config():
    global USER_ID, OAUTH_TOKEN
    env_token = os.environ.get("YANDEX_WEBMASTER_TOKEN", "").strip()
    env_user = os.environ.get("YANDEX_WEBMASTER_USER_ID", "").strip()
    if env_token:
        OAUTH_TOKEN = env_token
    if env_user:
        USER_ID = env_user
    if not OAUTH_TOKEN:
        print("ERROR: YANDEX_WEBMASTER_TOKEN env var not set. Provide OAuth token with webmaster:read scope.")
        sys.exit(1)
    if not USER_ID:
        # Try to resolve user ID from /user endpoint
        USER_ID = resolve_user_id(OAUTH_TOKEN)
    return USER_ID, OAUTH_TOKEN


def resolve_user_id(token):
    url = "https://api.webmaster.yandex.net/v4/user"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: Cannot resolve Yandex user ID: {e.code} {e.reason}")
        sys.exit(1)
    uid = body.get("user_id")
    if not uid:
        print("ERROR: Unexpected /user response, no user_id field.")
        sys.exit(1)
    print(f"Resolved Yandex user_id: {uid}")
    return uid


def yandex_api_get(path, token):
    url = f"https://api.webmaster.yandex.net/v4{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"ERROR: Yandex API error {e.code} for {path}: {e.reason}")
        sys.exit(1)


def fetch_popular_queries(user_id, token):
    """Fetch popular queries with avg_position for the host."""
    path = f"/user/{user_id}/hosts/{HOST}/search-queries/popular"
    params = "?limit=1000"
    return yandex_api_get(path + params, token)


def fetch_history(user_id, token, days=30):
    """Fetch query history for the last N days."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    path = f"/user/{user_id}/hosts/{HOST}/search-queries/history"
    params = f"?from={start.isoformat()}&to={end.isoformat()}"
    return yandex_api_get(path + params, token)


def match_keywords(data, queries):
    """Match repo queries to Yandex popular queries and extract avg_position."""
    popular = {}
    for item in data.get("popular", []):
        query_text = item.get("query", "")
        position = item.get("avg_position")
        popular[query_text] = position

    # Also process history rows if present (fallback)
    history_map = {}
    for row in data.get("history", []):
        query_text = row.get("query", "")
        position = row.get("avg_position")
        if query_text and position is not None:
            history_map[query_text] = position

    merged = {**popular, **history_map}

    results = []
    matched = 0
    for q in queries:
        pos = merged.get(q)
        if pos is not None:
            results.append({
                "query": q,
                "avg_position": pos,
                "status": "matched",
            })
            matched += 1
        else:
            results.append({
                "query": q,
                "avg_position": None,
                "status": "not_found_in_yandex",
            })
    print(f"Yandex matched {matched}/{len(queries)} queries.")
    return results


def save_results(data, results):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    payload = {
        "host": HOST,
        "period": "popular (all-time) + last_30d_history",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "data": results,
    }
    out_path = OUTPUT_DIR / f"yandex_kredato_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved Yandex results to: {out_path}")
    return out_path


def main():
    print("=== Yandex.Webmaster Rank Tracker (read-only) ===")
    queries = load_keywords()
    user_id, token = load_config()

    print("Fetching popular queries from Yandex.Webmaster...")
    popular_data = fetch_popular_queries(user_id, token)
    results = match_keywords(popular_data, queries)

    # Also fetch history for last 30 days to supplement
    print("Fetching last-30d history from Yandex.Webmaster...")
    history_data = fetch_history(user_id, token, days=30)
    history_results = match_keywords(history_data, queries)

    # Merge: prefer popular if both matched, otherwise take any match
    final = []
    pop_map = {r["query"]: r for r in results}
    hist_map = {r["query"]: r for r in history_results}
    for q in queries:
        if q in pop_map and pop_map[q]["status"] == "matched":
            final.append(pop_map[q])
        elif q in hist_map and hist_map[q]["status"] == "matched":
            final.append(hist_map[q])
        else:
            final.append({"query": q, "avg_position": None, "status": "not_found_in_yandex"})

    matched_total = sum(1 for r in final if r["status"] == "matched")
    print(f"Yandex final match: {matched_total}/{len(queries)}")

    save_results(popular_data, final)


if __name__ == "__main__":
    main()
