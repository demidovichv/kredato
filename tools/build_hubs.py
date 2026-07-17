#!/usr/bin/env python3
"""
Kredato hub generator (minimal-invasive) — НЕ переписывает статьи и НЕ трогает
существующие кастомные index.html разделов (fin/, strah/, earning/, of/).
Создаёт ТОЛЬКО недостающие index.html хабов-рубрик (fin/vkldy/, strah/osago/ и т.п.)
в site/. Читает статьи, берёт <title>, генерит оглавления. Link-checker в конце
(игнорирует /go/* и ?query в CSS-линках).
Запуск: python tools/build_hubs.py   (из корня репо)
"""
import re, sys, os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Рубрики, в которых лежат статьи (генератор создаёт для них хабы)
TAXONOMY = {
    "fin":    ["vkldy", "karty", "ipoteka", "rko", "sng"],
    "strah":  ["osago", "kasko", "ipotechnoe"],
}
SECTION_TITLE = {"fin":"Финансы и банковские продукты", "strah":"Страхование",
                 "earning":"Заработок и обучение", "of":"Витрина офферов"}
RUBRIC_TITLE = {"vkldy":"Вклады и накопления", "karty":"Карты", "ipoteka":"Ипотека",
                "rko":"РКО для бизнеса", "sng":"Финансы в СНГ",
                "osago":"ОСАГО", "kasko":"КАСКО", "ipotechnoe":"Ипотечное страхование"}

LSEP = os.linesep

def title_of(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
    if m: return m.group(1).strip()
    m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S | re.I)
    if m: return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return p.parent.name

def collect():
    """Возвращает list статей в рубриках: {section, rubric, slug, title, url}."""
    cat = []
    for section, rubrics in TAXONOMY.items():
        base = SITE / section
        if not base.exists():
            continue
        for rubric in rubrics:
            rb = base / rubric
            if not rb.exists():
                continue
            for art in sorted(rb.rglob("index.html")):
                if art.parent == rb:   # сам index рубрики не считаем
                    continue
                cat.append({"section": section, "rubric": rubric,
                            "slug": art.parent.name, "title": title_of(art),
                            "url": f"/{section}/{rubric}/{art.parent.name}/"})
    return cat

def hub_html(title, section, rubric, items, depth):
    up = "../" * depth
    cards = []
    for it in sorted(items, key=lambda x: x["title"]):
        cards.append(
            '      <div class="card">\n'
            '        <div class="icon">\U0001F4C4</div>\n'
            f'        <h3><a href="{it["slug"]}/">{it["title"]}</a></h3>\n'
            f'        <p><a href="{it["slug"]}/" class="card-link" aria-label="{it["title"]}"></a></p>\n'
            '      </div>')
    crumb = (f'<nav class="crumbs"><a href="{up}">Главная</a> › '
             f'<a href="{up}{section}/">{SECTION_TITLE[section]}</a> › '
             f'<span>{RUBRIC_TITLE.get(rubric, rubric)}</span></nav>')
    lis = []
    for r in TAXONOMY.get(section, []):
        active = ' class="active"' if r == rubric else ""
        lis.append(f'      <li{active}><a href="../{r}/">{RUBRIC_TITLE.get(r, r)}</a></li>')
    sidebar = (
        '  <aside class="sidebar">\n'
        f'    <h3>{SECTION_TITLE[section]}</h3>\n'
        '    <ul class="rubrics">\n' + LSEP.join(lis) + '\n'
        '    </ul>\n  </aside>')
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{up}assets/css/style.css">
</head>
<body>
<header class="site"><div class="wrap">
  <div class="logo">Kred<span>ato</span> · {SECTION_TITLE[section].split()[0]}</div>
  <nav>
    <a href="{up}">Хаб</a>
    <a href="{up}strah/">Страхование</a>
    <a href="{up}earning/">Заработок</a>
    <a href="{up}privacy.html">ПДн</a>
  </nav>
</div></header>
<section class="hero"><div class="wrap">
  {crumb}
  <h1>{title}</h1>
  <p class="lead">Все материалы рубрики. Честные разборы, без обещаний «гарантии».</p>
</div></section>
<main class="layout"><div class="hub-list"><div class="grid cols-2">
{LSEP.join(cards)}
  </div></div>{sidebar}
</div></main>
<footer class="site"><div class="wrap">
  <div class="footer-links">
    <a href="{up}">Хаб</a> · <a href="{up}strah/">Страхование</a> · <a href="{up}earning/">Заработок</a> · <a href="{up}privacy.html">ПДн</a>
  </div>
  <div class="disclaimer"><p>© 2026 Kredato. Материалы носят информационный характер и не являются финансовой рекомендацией.</p></div>
</div></footer>
</body>
</html>'''

def check_links():
    """Битые ссылки. Игнорирует /go/* (живут в _redirects, в т.ч. в relative-форме
    ../../../go/xxx) и ?query в CSS-линках."""
    redirects = set()
    rd = SITE / "_redirects"
    if rd.exists():
        for line in rd.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and line.startswith("/"):
                redirects.add(line.split()[0].rstrip("/"))
    broken = []
    for f in SITE.rglob("*.html"):
        t = f.read_text(encoding="utf-8", errors="ignore")
        for href in re.findall(r'href="([^"#]+)"', t):
            href_clean = href.split("?")[0].split("#")[0]
            if href_clean.startswith(("http", "mailto:", "//")) or href_clean == "":
                continue
            # /go/* (absolute или relative) — редиректы
            if "/go/" in href_clean:
                continue
            if not (f.parent / href_clean).resolve().exists():
                broken.append(f"{f.relative_to(SITE)} -> {href}")
    return broken

def main():
    cat = collect()
    by_rubric = defaultdict(list)
    for it in cat:
        by_rubric[(it["section"], it["rubric"])].append(it)
    created = 0
    for (section, rubric), items in by_rubric.items():
        target = SITE / section / rubric / "index.html"
        target.write_text(
            hub_html(RUBRIC_TITLE.get(rubric, rubric), section, rubric, items, 2),
            encoding="utf-8")
        created += 1
        print(f"[build] создан хаб: {section}/{rubric}/ ({len(items)} статей)")
    print(f"[build] хабов-рубрик создано: {created}, статей в них: {len(cat)}")
    broken = check_links()
    if broken:
        print(f"[build] БИТЫЕ ССЫЛКИ ({len(broken)}):", file=sys.stderr)
        for b in broken[:30]:
            print("  -", b, file=sys.stderr)
        return 1
    print("[build] битых ссылок нет ✓")
    return 0

if __name__ == "__main__":
    sys.exit(main())
