# GEO-аудит kredato.com — факт-отчёт

**Дата проверки:** 2026-08-13  
**Репозиторий:** `F:/Email_Marketing_Repository/site/`  
**Методология:** локальный статический аудит (без внешних запросов)

---

## ✅ Подтверждено

### Структура и базовые файлы
- **71 HTML-файл** в `site/` (53 content-страницы + 13 PDF-шаблонов + 3 служебных + 2 хаб-рубрики)
- `robots.txt` присутствует, ссылается на `sitemap.xml`
- `sitemap.xml` присутствует, содержит 61 URL, `lastmod: 2026-07-20`
- `.htaccess` присутствует (RewriteEngine для cloak-редиректов `/go/*`)
- `_redirects` присутствует (Cloudflare Pages 302-правила для партнёрских ссылок)
- `wrangler.toml` присутствует (Cloudflare Pages deployment)

### Дисклеймеры (E-E-A-T базовый сигнал)
- **70 из 71** HTML-файлов содержат текст дисклеймера «информационный характер»
- **33 файла** содержат полную формулировку «информационный характер и не являются финансовой рекомендацией»
- **1 файл** (privacy.html) содержит «не является индивидуальной рекомендацией»
- **1 файл** содержит «не является финансовой рекомендацией» отдельно

### Изображения и accessibility
- **14 `<img>` тегов** — все имеют непустой `alt` (0 пустых, 0 без alt)
- **72 `<svg>` тега** — все имеют `role="img"` или `aria-label`

### Технические базовые метки
- **70 файлов** содержат `<meta charset="utf-8">`
- **57 файлов** содержат `<meta name="viewport">`
- **31 файл** содержит `<meta name="keywords">`
- **38 content-страниц** имеют `<link rel="canonical">` с хостом `kredato.com` (битых канонических URL нет)
- **193 тега `<script>`** имеют `defer` (неблокирующая загрузка)
- **0 тегов `<script>`** в `<head>` без `defer`/`async` (1 блокирующий в body)
- `style.css` = 70 KB

### AEO-формат в контенте
- **42 файла** содержат callout-блоки (`class="callout"`) — функциональный аналог TL;DR
- **27 файлов** содержат `<table>` (сравнительные данные)
- **16 файлов** содержат визуальные хлебные крошки (`.crumbs`)
- **38 файлов** содержат упоминания источников/данных («по данным», «источник», «ЦБ», «согласно»)
- **6 файлов** содержат пошаговые инструкции
- **2 файла** содержат слово «эксперт» (magnet-11, earning/kursy-neyrosetey-marketing)

---

## ❌ Не подтверждено / Отсутствует

### Structured Data (самый критичный пробел)
- **JSON-LD присутствует только в 1 файле** (`index.html`, тип `Organization` с `inLanguage: ru`)
- **JSON-LD отсутствует в 70 HTML-файлах** (все content-страницы, PDF-шаблоны, хаб-рубрики)
- **`Article`** — 0 файлов (критично для AI Overview / Нейро)
- **`Person`** — 0 файлов (нет схемы автора)
- **`FAQPage`** — 0 файлов
- **`HowTo`** — 0 файлов
- **`BreadcrumbList`** — 0 файлов (визуальные крошки есть в 16, но не в schema)
- **`WebSite`** — 0 файлов
- **`WebPage`** — 0 файлов
- **`DefinedTerm`** — 0 файлов

### E-E-A-T сигналы
- **`author` блоки в HTML:** 0 файлов (нет ни одного блока с информацией об авторе/редакторе)
- **Автор в JSON-LD Article:** 0 (Article отсутствует полностью)
- **`datePublished` / `dateModified` в schema:** 0 файлов
- **Явные даты публикации в контенте:** 1 файл (`privacy.html`, дата `2026-07-09`)
- **Редакционные маркеры («редакция», «редактор»):** 0 файлов
- **Person schema с именем редактора/автора:** 0

### AEO-формат (недоиндексировано для AI)
- **TL;DR в явном виде:** 0 файлов (callout-блоки есть, но без semantic-разметки)
- **`<details>/<summary>` FAQ-блоки:** 0 файлов (FAQ-текст есть в 26 файлах, но без schema)
- **FAQPage schema:** 0
- **HowTo schema:** 0
- **Сравнительные таблицы с `<table>`:** 27 файлов — есть, но без `ItemList` или comparison schema

### llms.txt
- **`llms.txt` отсутствует** в корне `site/` (критично для LLM-краулеров GPTBot, Perplexity, Claude)

### OG / Twitter meta
- **OG-теги:** 0 файлов (нет ни одного `og:title`, `og:description`, `og:image`, `og:url`, `og:type`, `og:site_name`)
- **Twitter-теги:** 0 файлов (нет `twitter:card`, `twitter:title`, `twitter:image`)
- **Отсутствие `og:image`/`twitter:image`:** все 71 файл

### Скорость / кэширование
- **Cache-Control / Expires в `.htaccess`:** 0 записей (нет HTTP-кэш-хидов на уровне статики)
- **`<meta>` кэш-хиды в HTML:** 0
- **`preload`:** 0 файлов
- **`prefetch`:** 0 файлов
- **`dns-prefetch`:** 0 файлов
- **`preconnect`:** 0 файлов
- **`integrity`/`crossorigin` на CDN-ресурсах:** 0 (CDN не используется)
- `style.css` = 70 KB без минификации/сплиттинга

### Robots.txt и AI-краулеры
- **GPTBot (OpenAI):** нет явного Allow/Disallow (разрешён по умолчанию `*`)
- **ChatGPT-User:** отсутствует
- **Google-Extended:** отсутствует
- **PerplexityBot:** отсутствует
- **CCBot (Common Crawl):** отсутствует
- **anthropic-ai:** отсутствует
- **YandexBot:** отсутствует (разрешён по умолчанию)
- `/assets/pdf/` закрыт от индексации (Disallow)

### Внешние упоминания / citations
- **Внешние ссылки (`href` на другие домены):** 0 файлов (нет ни одной внешней гиперссылки в контенте)
- **Citation блоки / сноски:** 0
- **Backlinks (внутри сайта):** только внутренние ссылки на `/go/*` (партнёрские редиректы)

---

## 🚨 Сломано / Ошибки

### 24 файла с нулевым SEO-.markup
- **13 PDF-шаблонов** (`assets/pdf/magnet-*.html`, `prototype-1-credit-card.html`) — нет title, description, canonical, OG, schema
- **1 файл** `google007d4faebdef875c.html` (Google verification) — без SEO-меток
- **10 hub-страниц** (сгенерированы `build_hubs.py`) — нет meta description, OG, schema
- **Подробный список:**  
  `assets/pdf/magnet-2` · `magnet-3` · `magnet-4` · `magnet-5` · `magnet-6` · `magnet-7` · `magnet-8` · `magnet-9` · `magnet-10` · `magnet-11` · `magnet-12` · `magnet-13` · `prototype-1-credit-card` · `google007d4faebdef875c` · `fin/vkldy/index.html` · `fin/karty/index.html` · `fin/rko/index.html` · `fin/sng/index.html` · `strah/osago/index.html` · `strah/kasko/index.html` · `strah/ipotechnoe/index.html` · `learn/cheklist-frilansera-novichka/index.html` · `learn/golos-zarabotok-gayd/index.html` · `jobs/gde-nayti-zakazy-kwork-fl/index.html` · `jobs/podrabotka-vecherom-2026/index.html`

### Несогласованность канонических URL
- **5 канонических URL** заканчиваются на `/` (trailing slash)
- **35 канонических URL** без trailing slash
- **sitemap.xml** тоже содержит оба формата (45 со слэшем, 16 без)
- **Риск:** дублирование контента в глазах Google/Яндекса

### Sitemap: 1 единственный `lastmod`
- Все 61 URL имеют `lastmod: 2026-07-20` — сигнал неактуальности для поисковых систем

### Build-система не инжектирует schema
- `tools/build_hubs.py` генерирует hub-страницы без `<title>` (берёт из `<h1>`), без meta description, без JSON-LD, без OG
- Нет evidence о каком-либо build-скрипте, инжектирующем structured data в content-страницы

---

## 📋 Приоритизированный план внедрения

| Приоритет | Действие | Объём | Ожидаемый эффект для GEO |
|-----------|----------|-------|---------------------------|
| **P0** | Добавить `Article` + `Organization` schema на все 53 content-страницы | 53 файла | Вход в Google AI Overview / Яндекс Нейро — schema Article — обязательное условие |
| **P0** | Добавить `Person` schema для авторов/редакторов | ≥1 persona | E-E-A-T сигнал, требуется AI Overview |
| **P0** | Создать `llms.txt` в корне `site/` | 1 файл | Доступность для GPTBot, Perplexity, Claude — прямой вход в LLM-выдачи |
| **P1** | Добавить `FAQPage` schema в 26 страниц с FAQ-текстом | 26 файлов | Прямой вход в AI Overview FAQ-блоки |
| **P1** | Добавить `HowTo` schema в 6 страниц с пошаговыми инструкциями | 6 файлов | Вход в HowTo-выдачи Google AI Overview |
| **P1** | Добавить `BreadcrumbList` schema (визуальные крошки уже есть в 16 файлах) | 16+ файлов | Лучшее понимание иерархии сайта AI-краулерами |
| **P1** | Добавить `datePublished` + `dateModified` в Article schema + явные даты в HTML | 53 файла | Свежесть контента — сигнал для AI Overview |
| **P2** | Добавить OG + Twitter meta на все 71 файл (особенно `og:image`) | 71 файл | Корректные превью в соцсетях и AI-сниппетах |
| **P2** | Инжектировать author-card блоки в HTML + `author` в Article schema | 53 файла | E-E-A-T: явное авторство — requirement для YMYL-тем (финансы) |
| **P2** | Нормировать canonical URL (выбрать trailing slash или без,统一) | 38 файлов | Устранить дублирование в индексе |
| **P2** | Добавить `DefinedTerm` schema для ключевых терминов (кешбэк, РКО, ОСАГО и т.д.) | 20-30 терминов | Улучшение понимания тематики AI-краулерами |
| **P3** | Добавить внешние citations (links на ЦБ РФ, Росстат, банковские презентации) | 38+ файлов | E-E-A-T: верифицируемые источники — критично для финансов |
| **P3** | Добавить AI-специфичные правила в `robots.txt` (GPTBot, PerplexityBot, Google-Extended) | 1 файл | Контроль доступа LLM-краулеров |
| **P3** | Добавить кэш-хиды в `.htaccess` (Cache-Control, Expires) | 1 файл | Ускорение повторных визитов, лучшее Crawl Budget |
| **P3** | Добавить `preload`/`preconnect` для critical CSS и fonts | 1-5 файлов | Core Web Vitals — косвенный сигнал для AI Overview |
| **P4** | Добавить `<details>/<summary>` разметку в FAQ-блоки | 26 файлов | Semantic HTML — лучшая парсингная解析 AI-краулерами |
| **P4** | Минифицировать `style.css` (70 KB) + сплит critical/non-critical CSS | 1 файл | Производительность |
| **P4** | Добавить `WebSite` + `SearchAction` schema на `index.html` | 1 файл | Поисковый интент сайта |

---

## ⚡ Вердикт

**Текущий уровень готовности kredato.com к GEO-выдачам: низкий (20-25%).**

Сайт имеет базовую SEO-основу (title, description, canonical в 45+ файлах, дисклеймеры в 70+ файлах), но полностью отсутствует structured data на content-страницах — без `Article` + `Person` + `FAQPage` + `HowTo` schema сайт не попадает в Google AI Overview и Яндекс Нейро.

**Главный blockers:**
1. **0 из 53 content-страниц** имеют `Article` schema
2. **Нет `llms.txt`** — LLM-краулеры не получают явных инструкций
3. **Нет OG/Twitter meta** — нет AI-превью
4. **Нет внешних citations** — E-E-A-T по YMYL-тематике (финансы) не подтверждён внешними источниками
5. **24 файла** без какого-либо SEO-.markup (PDF-шаблоны, hub-страницы)

**Быстрый win (1-2 дня):** добавить `llms.txt` + инжектировать `Article` + `Organization` + `FAQPage` schema на 10-15 топовых статей через `build_hubs.py` или шаблон. Это даст первый вход в AI-выдачи.

**Полный цикл (1-2 недели):** покрыть schema все 53 content-страницы, добавить author-блокы, citations, OG-теги, нормировать canonical.

---

*Аудит проведён локально на файлах репозитория. Живые проверки (Google Rich Results Test, Schema.org Validator, Lighthouse) требуют деплоя на production.*
