#!/usr/bin/env python3
"""Safe mass SEO/GEO injection for kredato.com static HTML."""
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

ARTICLE_SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "__HEADLINE__",
  "description": "__DESCRIPTION__",
  "url": "__URL__",
  "datePublished": "2026-07-20",
  "dateModified": "2026-07-20",
  "inLanguage": "ru",
  "author": {
    "@type": "Person",
    "name": "Kredato Редакция",
    "jobTitle": "Финансовый редактор",
    "worksFor": {
      "@type": "Organization",
      "name": "Kredato"
    }
  },
  "publisher": {
    "@type": "Organization",
    "name": "Kredato",
    "url": "https://kredato.com"
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "__URL__"
  }
}
</script>'''

HUB_SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "__NAME__",
  "description": "__DESCRIPTION__",
  "url": "__URL__",
  "isPartOf": {
    "@type": "WebSite",
    "name": "Kredato",
    "url": "https://kredato.com"
  }
}
</script>'''

ORG_SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Kredato",
  "url": "https://kredato.com",
  "description": "Финансовая грамотность без «халявы»: банковские продукты, страхование и заработок для RU/СНГ.",
  "inLanguage": "ru"
}
</script>'''

OG_TWITTER = '''<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESCRIPTION__">
<meta property="og:url" content="__URL__">
<meta property="og:type" content="__OG_TYPE__">
<meta property="og:site_name" content="Kredato">
<meta property="og:locale" content="ru_RU">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__DESCRIPTION__">'''


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
    if any(part.lower() in {'assets'} for part in p.relative_to(SITE).parts):
        return 'skip_asset'
    if '<script type="application/ld+json">' in text:
        return 'skip_already'
    hub_names = {'index.html', 'fin/index.html', 'strah/index.html', 'earning/index.html', 'of/index.html', 'learn/index.html', 'jobs/index.html'}
    is_listing = 'hub-list' in text or 'grid cols-2' in text or 'grid cols-3' in text
    if p.name == 'index.html' and (rel in hub_names or is_listing):
        return 'hub'
    return 'article'


def build_injection(kind, title, description, canonical, h1):
    url = canonical or ''
    if kind == 'service':
        return ORG_SCHEMA, ''
    elif kind == 'hub':
        injection = HUB_SCHEMA.replace('__NAME__', (h1 or title)).replace('__DESCRIPTION__', description).replace('__URL__', url)
    else:
        injection = ARTICLE_SCHEMA.replace('__HEADLINE__', title).replace('__DESCRIPTION__', description).replace('__URL__', url)
    og_type = 'article' if kind == 'article' else 'website'
    og_twitter = OG_TWITTER.replace('__TITLE__', title).replace('__DESCRIPTION__', description).replace('__URL__', url).replace('__OG_TYPE__', og_type)
    return injection, og_twitter


def process_file(p: Path, apply=False):
    rel = p.relative_to(SITE).as_posix()
    try:
        text = p.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return {'file': rel, 'status': 'error', 'reason': str(e)}
    kind = classify(p, rel, text)
    if kind.startswith('skip'):
        return {'file': rel, 'status': kind}
    title = extract_meta(text, r'<title>(.*?)</title>')
    description = extract_meta(text, r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']')
    canonical = extract_meta(text, r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']')
    h1 = extract_meta(text, r'<h1>(.*?)</h1>')
    injection, og_twitter = build_injection(kind, title, description, canonical, h1)
    combined = injection + ('\n' + og_twitter if og_twitter else '')
    insert_marker = '</head>'
    if insert_marker not in text:
        return {'file': rel, 'status': 'error', 'reason': 'no </head>'}
    new_text = text.replace(insert_marker, combined + '\n' + insert_marker, 1)
    if apply:
        p.write_text(new_text, encoding='utf-8')
    return {
        'file': rel,
        'status': kind,
        'title': title,
        'canonical': canonical,
        'h1': h1,
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
        if r['status'] in ('article', 'hub', 'service'):
            print(f"{r['status'].upper()}: {r['file']}")
            if r.get('title'):
                print(f"  title: {r['title'][:80]}")
            if r.get('canonical'):
                print(f"  canonical: {r['canonical']}")
            print()
    errs = [r for r in results if r['status'] == 'error']
    if errs:
        print('=== ERRORS ===')
        for e in errs:
            print(e)


if __name__ == '__main__':
    main()
