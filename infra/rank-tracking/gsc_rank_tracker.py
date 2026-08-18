#!/usr/bin/env python3
"""
Google Search Console (GSC) rank tracker for kredato.com.
Read-only. Fetches query-level positions, impressions, clicks, CTR via GSC API.
"""

import json
import os
import sys
import datetime
from pathlib import Path

# Google API imports — install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------- Configuration ----------
REPO = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO / "infra" / "rank-tracking" / "gsc_config.json"
OUTPUT_DIR = REPO / "reports" / "rank-tracking"
KEYWORDS_PATH = REPO / "reports" / "keywords" / "2026-08-05.json"

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL = "https://kredato.com/"  # trailing slash required by GSC

# ---------- Helpers ----------

def load_keywords():
    """Load keyword list from repo."""
    if not KEYWORDS_PATH.exists():
        print(f"ERROR: Keywords file not found: {KEYWORDS_PATH}")
        sys.exit(1)
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    queries = [q["query"] for q in data.get("queries", []) if q.get("intent") in ("commercial", "informational")]
    print(f"Loaded {len(queries)} commercial/informational queries.")
    return queries


def build_service():
    """Build GSC service using service-account credentials."""
    creds_path = os.environ.get("GSC_CREDENTIALS_FILE", "").strip()
    if not creds_path:
        print("ERROR: GSC_CREDENTIALS_FILE env var not set. Point it to your service-account JSON key.")
        sys.exit(1)
    if not Path(creds_path).exists():
        print(f"ERROR: Credentials file not found: {creds_path}")
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    service = build("webmasters", "v3", credentials=credentials)
    return service


def fetch_gsc_data(service, queries):
    """Fetch search analytics for the given queries over the last 30 days."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=30)

    results = []
    # GSC allows up to ~5 queries per request via the 'query' dimension filter.
    # We'll request the whole domain data and filter locally to avoid multi-request overhead.
    request_body = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": ["query"],
        "rowLimit": 25000,
    }

    try:
        response = service.searchanalytics().query(siteUrl=SITE_URL, body=request_body).execute()
        rows = response.get("rows", [])
    except HttpError as e:
        print(f"ERROR: GSC API error: {e}")
        sys.exit(1)

    query_map = {row["keys"][0]: row for row in rows}

    matched = 0
    for q in queries:
        row = query_map.get(q)
        if row:
            results.append({
                "query": q,
                "position": row.get("position"),
                "impressions": row.get("impressions", 0),
                "clicks": row.get("clicks", 0),
                "ctr": row.get("ctr", 0.0),
                "status": "matched",
            })
            matched += 1
        else:
            results.append({
                "query": q,
                "position": None,
                "impressions": 0,
                "clicks": 0,
                "ctr": 0.0,
                "status": "not_found_in_gsc",
            })

    print(f"GSC matched {matched}/{len(queries)} queries.")
    return {
        "site_url": SITE_URL,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "data": results,
    }


def save_results(data):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    out_path = OUTPUT_DIR / f"gsc_kredato_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved GSC results to: {out_path}")
    return out_path


def main():
    print("=== GSC Rank Tracker (read-only) ===")
    queries = load_keywords()
    service = build_service()
    data = fetch_gsc_data(service, queries)
    save_results(data)


if __name__ == "__main__":
    main()
