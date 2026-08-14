#!/usr/bin/env python3
"""Safe mass canonical injection for kredato.com static HTML."""
import re, sys
from pathlib import Path

REPO = Path('F:/Email_Marketing_Repository')
SITE = REPO / 'site'

SKIP_FILES = {
    'subscribe.html',
    'subscribe.html/index.html',
    'subscribe/confirmed/index.html',
    'privacy.html',
    'of/soon.html',
    'google007d4faebdef875c.html',
}
SKIP_SUBSTR = ['assets/pdf/']
SKIP_DIRS = {'assets'}

CANONICAL_TEMPLATE = '<link rel="canonical" href="__URL__">'


def extract_meta(text, pattern):
    m = re.search(pattern, text, re.S)
    return m.group(1).strip() if m else ''


def classify(p: Path, rel: str, text: str):
    if 'assets/pdf/' in str(p).lower():
        return 'skip_pdf'
    if rel in SKIP_FILES:
        return 'skip_service'
    if any(substr in str(p).lower() for substr in SKIP_SUBSTR):
        return 'skip_service'
    if any(part.lower() in SKIP_DIRS for part in p.relative_to(SITE).parts):
        return 'skip_asset'
    if '<link rel="canonical"' in text:
        return 'skip_already'
    return 'inject'


def process_file(p: Path, apply=False):
    rel = p.relative_to(SITE).as_posix()
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {'file': rel, 'status': 'error', 'reason': str(e)}
    kind = classify(p, rel, text)
    if kind.startswith('skip'):
        return {'file': rel, 'status': kind}
    canonical = extract_meta(text, r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']')
    title = extract_meta(text, r'<title>(.*?)</title>')
    if p.name == 'index.html' and not canonical:
        url = f'https://kredato.com/{rel.replace("/index.html", "/")}'
    else:
        url = canonical or f'https://kredato.com/{rel}'
    injection = CANONICAL_TEMPLATE.replace('__URL__', url)
    insert_marker = '</head>'
    if insert_marker not in text:
        return {'file': rel, 'status': 'error', 'reason': 'no </head>'}
    new_text = text.replace(insert_marker, injection + '\n' + insert_marker, 1)
    if apply:
        p.write_text(new_text, encoding='utf-8')
    return {
        'file': rel,
        'status': kind,
        'title': title,
        'canonical': url,
    }


def main():
    dry_run = '--apply' not in sys.argv
    htmls = sorted(SITE.rglob('*.html'))
    results = []
    for p in htmls:
        results.append(process_file(p, apply=not dry_run))
    counts = {}
    for r in results:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print(f'=== {"DRY-RUN" if dry_run else "APPLY"} ===')
    print(f'Total files: {len(results)}')
    for k, v in sorted(counts.items()):
        print(f'{k}: {v}')
    print('\n=== SAMPLES ===')
    for r in results:
        if r['status'] == 'inject':
            print(f"INJECT: {r['file']}")
            if r.get('title'):
                print(f"  title: {r['title'][:80]}")
            print(f"  canonical: {r['canonical']}")
            print()
    errs = [r for r in results if r['status'] == 'error']
    if errs:
        print('=== ERRORS ===')
        for e in errs:
            print(e)


if __name__ == '__main__':
    main()
