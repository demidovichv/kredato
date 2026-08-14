#!/usr/bin/env python3
"""Dry-run: classify HTML files and show planned SEO/GEO injections for kredato.com."""
import re
from pathlib import Path

REPO = Path('F:/Email_Marketing_Repository')
SITE = REPO / 'site'

# 1. collect html files
htmls = sorted(SITE.rglob('*.html'))
print(f'TOTAL_HTML {len(htmls)}')

# 2. classify
articles = []
hubs = []
service = []
pdfs = []
already_done = []

for p in htmls:
    rel = p.relative_to(SITE).as_posix()
    text = p.read_text(encoding='utf-8', errors='ignore')
    has_jsonld = '<script type="application/ld+json">' in text
    has_og = 'og:title' in text
    if 'assets/pdf/' in str(p).lower():
        pdfs.append(rel)
        continue
    if rel in {'privacy.html', 'subscribe.html', 'subscribe.html/index.html', 'of/soon.html', 'google007d4faebdef875c.html'}:
        service.append(rel)
        if has_jsonld:
            already_done.append(rel)
        continue
    # hub detection: index.html inside category folder or obvious hub paths
    if p.name == 'index.html' and ('/fin/' in str(p) or '/strah/' in str(p) or '/earning/' in str(p) or '/of/' in str(p) or '/learn/' in str(p) or '/jobs/' in str(p)):
        hubs.append(rel)
        if has_jsonld:
            already_done.append(rel)
        continue
    # default: article
    articles.append(rel)
    if has_jsonld:
        already_done.append(rel)

print(f'ARTICLES {len(articles)}')
print(f'HUBS {len(hubs)}')
print(f'SERVICE {len(service)}')
print(f'PDFS {len(pdfs)}')
print(f'ALREADY_HAS_JSONLD {len(already_done)}')

# 3. show planned injections for first 3 of each type
for rel in articles[:3]:
    p = SITE / rel
    text = p.read_text(encoding='utf-8')
    title = re.search(r'<title>(.*?)</title>', text, re.S)
    h1 = re.search(r'<h1>(.*?)</h1>', text, re.S)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    print('---')
    print('TYPE article')
    print('FILE', rel)
    print('TITLE', title.group(1).strip() if title else '')
    print('H1', h1.group(1).strip() if h1 else '')
    print('CANONICAL', canonical.group(1) if canonical else '')
    print('PLAN: Article + Organization + BreadcrumbList + OG/Twitter')

for rel in hubs[:3]:
    p = SITE / rel
    text = p.read_text(encoding='utf-8')
    title = re.search(r'<title>(.*?)</title>', text, re.S)
    h1 = re.search(r'<h1>(.*?)</h1>', text, re.S)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    print('---')
    print('TYPE hub')
    print('FILE', rel)
    print('TITLE', title.group(1).strip() if title else '')
    print('H1', h1.group(1).strip() if h1 else '')
    print('CANONICAL', canonical.group(1) if canonical else '')
    print('PLAN: CollectionPage + Organization + BreadcrumbList + OG/Twitter')

for rel in service[:3]:
    print('---')
    print('TYPE service')
    print('FILE', rel)
    print('PLAN: only Organization JSON-LD, no OG/Twitter')

for rel in pdfs[:3]:
    print('---')
    print('TYPE pdf')
    print('FILE', rel)
    print('PLAN: skip')

# 4. summary counts
print('---')
print('SUMMARY')
print('to_inject_articles', len(articles))
print('to_inject_hubs', len(hubs))
print('to_inject_service', len(service))
print('skip_pdfs', len(pdfs))
print('already_has_jsonld', len(already_done))
