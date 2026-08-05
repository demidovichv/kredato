#!/usr/bin/env python3
"""Kredato health monitor: site endpoints + rates.json."""
import requests
from pathlib import Path
from datetime import datetime

BASE = 'https://kredato.com'
CHECKS = [
    ('Главная', f'{BASE}/'),
    ('Политика', f'{BASE}/privacy.html'),
    ('Подписка', f'{BASE}/subscribe.html'),
    ('PDF-магнит', f'{BASE}/assets/pdf/magnet-3-deposits-rates.html'),
    ('rates.json', f'{BASE}/assets/data/rates.json'),
]

report = []
now = datetime.now().isoformat(timespec='seconds')
report.append(f'# Health {now}\n')

for name, url in CHECKS:
    try:
        r = requests.get(url, timeout=20, allow_redirects=True)
        status = r.status_code
        if status == 200:
            if url.endswith('rates.json'):
                import json
                data = r.json()
                report.append(f'- {name}: OK ({status})')
                report.append(f'  deposit: {data.get("deposit") or data.get("periods", {}).get("6m", {}).get("deposits")}')
                report.append(f'  mortgage: {data.get("mortgage") or data.get("periods", {}).get("6m", {}).get("mortgage")}')
                report.append(f'  loans: {data.get("loans") or data.get("periods", {}).get("6m", {}).get("loans")}')
            else:
                report.append(f'- {name}: OK ({status})')
        else:
            report.append(f'- {name}: FAIL ({status})')
    except Exception as e:
        report.append(f'- {name}: FAIL ({type(e).__name__}: {e})')

Path('reports/health').mkdir(parents=True, exist_ok=True)
out = Path('reports/health') / f'{datetime.now().strftime("%Y-%m-%d")}.md'
out.write_text('\n'.join(report), encoding='utf-8')
print('\n'.join(report))
