# 📚 Email Marketing Vault — Obsidian

> **Этот репозиторий = Obsidian vault.** Открой папку `F:\Email_Marketing_Repository` в Obsidian через `File → Open vault` (выбери эту папку). Все заметки — Markdown, связи через `[[вики-ссылки]]`, фильтрация через теги `#charly` `#statister` `#leadmagnet` `#monitoring`.

## 🗺️ Карта vault (куда что смотреть)

### 📊 Отчёты (аналитика) → `reports/`
| Заметка | Платформа | Содержание |
|---------|-----------|------------|
| [[charly_cash_final_report]] | Charly.Cash | Сводный анализ + практика |
| [[charly_cash_analysis]] | Charly.Cash | Сырой разбор агента (разделы сайта) |
| [[leadmagnet_analysis]] | LeadMagnet.ru | 4 раздела: новости/статьи/кейсы/база знаний |
| [[statister_analysis]] | Statister-Mail.ru | Сравнение с Charly.Cash + тех. фичи |
| [[unified_report]] | Все | Единый отчёт по 3 платформам |
| [[dashboard]] | Все | Текущий статус проекта |
| [[final_status]] | Все | Итоговый статус репозитория |
| [[offers_sources]] | Офферы | Каталог 5 источников офферов (incl. ЛК) |
| [[top_offers_ru_sng]] | Офферы | 🎯 Сводный гид выбора офферов для агентов (RU/СНГ) |
| [[leads_su_analysis]] | Leads.su | CPA-сеть: топ офферов, EPC, гео (email разрешён) |
| [[pampadu_analysis]] | Pampadu | Партнёрские продажи: высокие чеки, спам запрещён (⏸️ паркован) |
| `offers/data/leads_*.json` | Leads.su | Сырые данные API (каталог, email RU/СНГ, страховок НЕТ) |
| [[insurance_market_analysis]] | Рынок | Глубокий анализ страхования RU/СНГ + архитектура сайта/контент-план |
| [[automation_agents]] | Команда | 4 автономных cron-агента (Charly/Leads.su/Statister/Дайджест) |

### 🖥️ Инфраструктура → `infra/`
| Заметка | Содержание |
|---------|-----------|
| [[vps_setup]] | Развёртывание VPS (EU) + SSH через прокси, изоляция |
| [[proxies]] | Матрица прокси/аккаунтов (антрифрод) |
| [[secrets_template]] | Шаблон секретов (без реальных ключей) |
| [[charly_course_syllabus]] | Каркас курса Чарли → 8 исслед. блоков (актуал через агентов) |
| course_research/ | Актуальные исследования блоков (Блоки 1/3/4/7 готовы) |
| [[compliance_policy]] | Политика легальности: 152-ФЗ, спам, маркировка, правила Leads.su/Pampadu |
| [[security_policy]] | Политика безопасности: секреты, классификация данных, ротация, бэкап |

### 📈 Метрики → `reports/`
| Заметка | Содержание |
|---------|-----------|
| [[metrics]] | Единый дашборд KPI (бизнес/база/SEO/инфра/агенты) |

### 🎯 Вертикали (Фаза 7, глубокий анализ) → `reports/verticals/`
| Заметка | Содержание |
|---------|-----------|
| [[verticals_synthesis]] | **Синтез + архитектура сайта (гибрид: хаб + поддомены)** — РЕКОМЕНДАЦИЯ |
| [[vertical_fintech]] | Вертикаль «Банк. продукты/финтех»: рынок, ЦА, SEO-ниши, Leads.su |
| [[vertical_insurance]] | Вертикаль «Страхование»: рынок 4 трлн₽, ЦА, Pampadu (double opt-in) |
| [[vertical_earning]] | Вертикаль «Заработок/Обучение/HR»: инфо-магнит хаба, Leads.su HR |
| [[insurance_market_analysis]] | Рынок страхования RU/СНГ + архитектура (до вертикалей) |
### 🏛️ Процессы → `00_Project/`
| Заметка | Содержание |
|---------|-----------|
| [[DEFINITION_OF_DONE]] | Критерии завершения задач (DoD) для агентов |
| [[automation_agents]] | Команда из 4 cron-агентов + роли/эскалация |

### 🛠️ Скрипты и мониторинг
- `charly_cash/` — скрипты мониторинга Charly.Cash (`monitor_simple.py`, `monitor_full.py`, `charly-monitor*.py`)
- `statister_mail/` — скрипт мониторинга (`monitoring.py`)
- `leadmagnet_blog/` — скрипт мониторинга (`monitoring.py`)
- `shared/monitoring/` — **универсальный** монитор `monitor_all.py` + по одному на каждый сайт
- `shared/automation/` — **планировщик прогрева** `warmup_scheduler.py` (+ конфиг/README), считает дневные квоты отправки по кривой warm-up

## 🎯 Быстрый старт
```bash
# Обновить все источники (3 блога + 2 партнёрки ЛК) за один запуск
cd F:\\Email_Marketing_Repository\\shared\\monitoring
python monitor_all.py
```

## 💰 Офферы для агентов (старт RU/СНГ)
- **Гид выбора:** [[top_offers_ru_sng]] — топ офферов Leads.su + Pampadu с метриками
- **Leads.su** 🟢 — email-рассылки официально разрешены, EPC до 189₽ (Вебзайм)
- **Pampadu** 🔴 — спам запрещён, только opt-in база, чеки до 85k₽ (ипотека)
- Обе сети: **только RU/СНГ**, EU/US не покрывается (там — [[charly_cash_analysis]] + западные сети)

## 🏷️ Теги для навигации в Obsidian
- `#charly` — всё про Charly.Cash
- `#statister` — Statister-Mail.ru (SaaS-мониторинг)
- `#leadmagnet` — LeadMagnet.ru (арбитраж/кейсы)
- `#monitoring` — скрипты и состояние проверок
- `#infrastructure` — домены, SMTP, прогрев, deliverability
- `#monetization` — схемы заработка, офферы, ROI

## 📌 Ключевые выводы (см. [[unified_report]])
- **Charly.Cash** = учебник (теория + инструменты, бесплатно) → новичкам
- **LeadMagnet.ru** = практика (кейсы, ROI до 2513%) → опытным
- **Statister-Mail.ru** = защита (автостоп, мониторинг спама 30с) → при масштабировании
- Оптимально: Charly (обучение) + Statister (защита/автоматизация) + LeadMagnet (схемы)

---
*Обновлено: 2026-07-07 · Hermes Agent · v1.0*
