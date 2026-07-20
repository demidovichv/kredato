---
tags: [infra, launch, checklist, vps, rf, dns, smtp, double-opt-in, phase7]
---

# Чек-лист запуска инфраструктуры (kredato.com)

> Дата: 2026-07-09. Статус: DRAFT (ждём выбора регистратора от агентов).
> Контекст: владелец — нерезидент РФ (РБ). Зона **.com**. VPS — **РФ** (локализация ПДн 152-ФЗ).
> Цель: от купленного домена до первой рассылки по double opt-in базе.

---

## Этап 0 — Домен (блокирует всё остальное)

- [ ] Регистратор: **Cloudflare Registrar** (~$9.15/год, at-cost, renew не растёт) — САМЫЙ ДЕШЁВЫЙ (подтверждено агентом: `registrar_cheapest.md`)
- [ ] Купить **kredato.com** (подтверждён свободен: whois `No match` от Verisign)
- [ ] DNS/SSL/Proxy → **Cloudflare** (бесплатно, прячет IP VPS, стыкуется с Resend DKIM)
- [ ] Запретить авто-renew на годы вперёд (контроль расходов)
- [ ] WHOIS-privacy бесплатно (вкл. по умолчанию у CF)
- [ ] НЕ брать .ru/.рф (Госуслуги с 1.09.2026 — нерезиденту недоступно)
- [ ] Альтернативы (дороже): Porkbun $11.08, Namecheap/Spaceship промо $5-8 но renew $11-15

## Этап 1 — VPS в РФ

- [ ] Арендовать VPS (РФ-локация: Timeweb / Selectel / Reg.ru VPS / Cloud.ru)
  - 2 vCPU / 4 GB RAM / 40-80 GB SSD / Ubuntu 22.04
  - ~₽400-700/мес
- [ ] Настроить SSH по ключу (root запрещён по паролю)
- [ ] UFW: открыть 22,80,443,25,465,587
- [ ] Таймзона Europe/Moscow
- [ ] Python venv + requests/bs4
- [ ] Syncthing/git — синхронизация vault с ПК (РБ)

> ⚠️ EU-VPS (Contabo/Hetzner) — НЕ для базы ПДн (нарушение 152-ФЗ локализации). Допустим только для не-ПДн задач.

## Этап 2 — DNS + SSL (Cloudflare)

- [ ] NS kredato.com → **Cloudflare** (Registrar + DNS в одном)
- [ ] Поддомены: `fin.kredato.com`, `strah.kredato.com` (A/СNAME → VPS, через CF Proxy)
- [ ] Let's Encrypt SSL (через Cloudflare Origin CA — бесплатно, авто-обновление)
- [ ] Resend DKIM/SPF TXT-записи (из Этапа 4)
- [ ] Проверка: `https://kredato.com` + поддомены резолвятся, IP скрыт за CF

## Этап 3 — Сайт (каркас уже в `site/`)

- [ ] Деплой `site/` на VPS (nginx: root → `site/`, поддомены → `site/fin/`, `site/strah/`)
- [ ] Проверить opt-in форму (все страницы)
- [ ] Запустить агентов контента (Дизайнер→Кейворд→Копирайтер+Верстальщик→Иллюстратор+SEO+Конкуренты)
- [ ] Double opt-in endpoint (см. Этап 5)

## Этап 4 — Отправка писем (SMTP)

> Стек: **Resend** (старт) → **Unisender Go / SendPulse** (рост, RU-доставляемость) или свой Postfix+прогрев.
> Домен + DNS уже на Cloudflare → DKIM/SPF записи Resend вставляются в пару кликов.

- [ ] **Resend.com** (старт): бесплатно до 3k писем/мес, API (HTTP из Charly Mailer), карта нерезидента ок
  - Автонастройка SPF/DKIM/DMARC (даёт TXT для Cloudflare)
  - Поддержка one-click unsubscribe (List-Unsubscribe) — требование Gmail с нояб.2025
- [ ] **Рост:** Unisender Go / SendPulse (РФ-сервера, лучше доставляемость в Яндекс/Мail.ru) ИЛИ свой Postfix на RF-VPS + `warmup_scheduler.py`
- [ ] Настроить SPF + DKIM + DMARC (на kredato.com через Cloudflare)
- [ ] PTR-запись (обратный DNS) — если свой Postfix; у Resend уже есть
- [ ] TLS обязательно
- [ ] One-click unsubscribe (List-Unsubscribe + List-Unsubscribe-Post)
- [ ] Прогрев домена (`shared/automation/warmup_scheduler.py` уже готов)

## Этап 5 — Charly Mailer (адаптация) + double opt-in

- [ ] Адаптировать Charly Mailer → headless-демон на VPS (убрать GUI, оставить core/sender/queue/proxy/smtp/stats)
- [ ] Хук `warmup_scheduler.py` в прогрев домена
- [ ] Double opt-in логика: (1) подписка → (2) письмо с подтверждением → (3) активация в БД
- [ ] База ПДн — В РФ (локализация 152-ФЗ), отдельно по вертикалям (финтех / страхование / заработок)
- [ ] Unsubscribe в каждом письме (compliance_policy.md)

## Этап 6 — Секреты (только в `secrets.local.md`, в .gitignore)

- [ ] Реальные креды Leads.su (API/постбек) — вставить в `secrets.local.md`
- [ ] Pampadu (контакт @alexeyloktionов) — после разблока (double opt-in база готова)
- [ ] SMTP-креды / API провайдера
- [ ] SSH-ключи VPS
- [ ] Формат: `[REDACTED]`, НЕ коммитить в git

## Этап 7 — Контент-план первых статей (под НЧ-ниши)

- [ ] Из `vertical_fintech.md`: вклады/РКО/ипотека/карты (финтех)
- [ ] Из `vertical_insurance.md`: ОСАГО/КАСКО (страхование, копит базу под Pampadu)
- [ ] Из `vertical_earning.md`: подработка/фриланс/нейросети (инфо-магнит)
- [ ] Лид-магниты: калькуляторы, чек-листы (opt-in)

## Этап 8 — Комплаенс (финальная проверка)

- [ ] `privacy.html` на месте ✅ (уже в каркасе)
- [ ] Double opt-in работает (тест на тестовом email)
- [ ] Unsubscribe работает
- [ ] Дисклеймер «не фин. рекомендация» на всех страницах ✅ (в каркасе)
- [ ] База ПДн в РФ ✅ (Этап 1)

---

## 💰 Оценка стартовых расходов (в мес)

| Статья | Цена |
|--------|------|
| Домен .com | ~$9/год (~₽75/мес) |
| VPS РФ | ₽400-700/мес |
| RU-прокси (резидентные) | ₽300-1000/мес (смотря объём) |
| SMTP-провайдер (старт) | ₽0-500/мес (или по объёму) |
| **ИТОГО** | **~₽800-2200/мес** |

> Без зарплат агентов (они бесплатны в рамках Hermes) и без офферов (те приносят, а не тратят).

---

## 🚫 Что НЕ делаем (решения закрыты)

- ❌ Не берём .ru/.рф/.su (Госуслуги, нерезидент)
- ❌ Не ставим VPS в EU для базы ПДн (152-ФЗ локализация)
- ❌ Не используем слитые базы/холодный спам (compliance_policy.md, Pampadu §12)
- ❌ Не копируем слитые credential'ы из видео-курса Чарли в vault
