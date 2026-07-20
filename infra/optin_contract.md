---
tags: [optin, double-opt-in, api, contract, charly-mailer, site]
---

# Контракт double opt-in (стык сайт ↔ движок)

> Общий интерфейс между opt-in формой на сайте (kredato.com) и Charly Mailer (движок рассылки).
> Фиксируем ДО вёрстки формы и ДО сборки движка — чтобы не переделывать.
> Дата: 2026-07-09. Статус: DRAFT (ждём VPS РФ для бэкенда).

---

## 1. Поля формы (frontend → backend)

| Поле | Тип | Обязат. | Примечание |
|------|-----|---------|------------|
| `email` | email | ✅ | валидация на клиенте + сервере |
| `vertical` | enum | ✅ | `fintech` \| `insurance` \| `earning` (куда писать) |
| `source` | string | 🔘 | UTM/страница (для атрибуции) |
| `consent` | bool | ✅ | галочка «согласен на рассылку + 152-ФЗ» |
| `token` | string | 🔘 | honeypot (скрытое поле, должно быть пустым) |

## 2. Endpoint (backend на RF-VPS)

```
POST /api/subscribe
Content-Type: application/json
```

**Запрос:**
```json
{
  "email": "user@example.com",
  "vertical": "fintech",
  "source": "hub_hero",
  "consent": true,
  "token": ""
}
```

**Ответы:**
- `201 Created` → подписка принята, письмо подтверждения отправлено
- `200 AlreadySubscribed` → email уже есть (не дубль)
- `400 BadRequest` → нет email/consent/honeypot заполнен
- `422 InvalidEmail` → email не прошёл валидацию

## 3. Double opt-in поток

1. **Подписка** (форма → `/api/subscribe`) → сохраняем email со статусом `pending`, генерим `confirm_token` (random 32 байта, hex)
2. **Письмо** (Charly Mailer через Resend) → ссылка `https://kredato.com/confirm?t=<token>`
3. **Подтверждение** (GET `/confirm?t=...`) → статус `active`, редирект на `subscribe.html` (успех)
4. **Рассылка** только по `active` в соответствующем `vertical`

## 4. База ПДн (РФ-локация, 152-ФЗ)

Таблица `subscribers`:
```sql
id, email, vertical, source, status(pending|active|unsubscribed),
confirm_token, created_at, confirmed_at, unsubscribed_at
```
- Хранить ТОЛЬКО на RF-VPS (локализация ПДн граждан РФ)
- Удаление по запросу (права субъекта 152-ФЗ)
- Unsubscribe → `status=unsubscribed`, письма не шлём

## 5. Unsubscribe (в каждом письме)

- `List-Unsubscribe` header + одноразовая ссылка `https://kredato.com/unsubscribe?t=<token>`
- GET без подтверждения (требование почтовиков) → `status=unsubscribed`

## 6. Compliance (обязательно в форме)

- Текст согласия: «Я согласен(а) на получение рассылки и обработку ПДн по 152-ФЗ. Отписаться можно в любой момент.»
- Ссылка на `privacy.html` (уже в каркасе)
- Дисклеймер «не фин. рекомендация» — на всех страницах (в каркасе)

---

## Стык для агентов

- **Верстальщик (сайт):** форма шлёт JSON по схеме §1→§2 на `/api/subscribe` (заглушка пока на `subscribe.html`)
- **Charly Mailer (движок):** реализует §2 endpoint + §3 поток + §4 БД + §5 unsubscribe
- **Общее:** `confirm_token` формат одинаковый (hex 64 символа)
