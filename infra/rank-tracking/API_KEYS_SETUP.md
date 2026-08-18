# Подключение API-ключей для rank-tracking kredato.com

## Обзор

Инфраструктура точного замера позиций kredato.com использует два официальных API:
- **Google Search Console API** (read-only) — позиции в Google за последние 30 дней.
- **Yandex.Webmaster API v4** (read-only) — средняя позиция и история в Яндексе.

Ниже — пошаговая инструкция по получению и подключению ключей.

---

## 1. Google Search Console API

### 1.1. Создание проекта в Google Cloud

1. Открой https://console.cloud.google.com/ → создайте новый проект (например `kredato-seo`).
2. В меню **APIs & Services → Library** найдите и включите:
   - `Google Search Console API`

### 1.2. Service Account

GSC API требует Service Account (OAuth client для браузера неудобен для headless-скриптов).

1. **IAM & Admin → Service Accounts** → **Create Service Account**.
2. Имя: `kredato-gsc-reader`.
3. Роль: `Viewer` (или `Search Console Reader`, если доступен).
4. Нажмите **Done**.
5. Откройте созданный SA → вкладка **Keys → Add Key → Create new key** → тип **JSON**.
6. Скачайте файл (например `gsc-key.json`). **Никому не передавайте**.

### 1.3. Доступ к сайту в GSC

1. Открой https://search.google.com/search-console
2. Добавьте ресурс `https://kredato.com/` (если ещё не добавлен).
3. В разделе **Settings → Users & permissions** добавьте email созданного Service Account как **Read-only** (или **Full**).
   - Email имеет вид `kredato-gsc-reader@<project-id>.iam.gserviceaccount.com`.

### 1.4. Подключение в скрипт

Способ A (рекомендуемый): переменная окружения.

```bash
export GSC_CREDENTIALS_FILE="F:/Email_Marketing_Repository/infra/rank-tracking/keys/gsc-key.json"
```

Способ B: разместите файл по пути, указанному в скрипте (см. `CONFIG_PATH`).

```powershell
# PowerShell (если запускаете скрипт из Windows)
$env:GSC_CREDENTIALS_FILE="F:\Email_Marketing_Repository\infra\rank-tracking\keys\gsc-key.json"
python F:\Email_Marketing_Repository\infra\rank-tracking\gsc_rank_tracker.py
```

> **Важно:** не коммитьте JSON-ключ в git. Убедитесь, что путь прописан в `.gitignore`.

---

## 2. Yandex.Webmaster API v4

### 2.1. OAuth-приложение

1. Открой https://oauth.yandex.ru/
2. Создайте приложение.
3. В настройках приложения добавьте права (scope): `webmaster:read`.
4. Получите `client_id` и `client_secret`.

### 2.2. Получение OAuth-токена

Способ A (ручной, для тестов):

1. Откройте в браузере:
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=<CLIENT_ID>&scope=webmaster:read
   ```
2. Авторизуйтесь под аккаунтом, владеющим kredato.com в Вебмастере.
3. После редиректа URL будет содержать `access_token=...`. Скопируйте токен.

Способ B (серверный, для CI/CD):

```bash
curl -X POST https://oauth.yandex.ru/token \
  -d "grant_type=authorization_code" \
  -d "code=<AUTH_CODE_FROM_STEP_1>" \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>"
```

### 2.3. Подключение в скрипт

Способ A (переменные окружения):

```bash
export YANDEX_WEBMASTER_TOKEN="<OAuth токен с webmaster:read>"
export YANDEX_WEBMASTER_USER_ID="<user_id из ответа /user endpoint>"
```

Если `YANDEX_WEBMASTER_USER_ID` не задан, скрипт сам его определит по `/user`.

Способ B (PowerShell):

```powershell
$env:YANDEX_WEBMASTER_TOKEN="<token>"
$env:YANDEX_WEBMASTER_USER_ID="<user_id>"
python F:\Email_Marketing_Repository\infra\rank-tracking\yandex_rank_tracker.py
```

---

## 3. Быстрый старт (шпаргалка)

### Установка зависимостей

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Запуск обоих скриптов

```bash
# Linux / Git Bash
export GSC_CREDENTIALS_FILE="F:/Email_Marketing_Repository/infra/rank-tracking/keys/gsc-key.json"
export YANDEX_WEBMASTER_TOKEN="<token>"
python F:/Email_Marketing_Repository/infra/rank-tracking/gsc_rank_tracker.py
python F:/Email_Marketing_Repository/infra/rank-tracking/yandex_rank_tracker.py
```

Результат: JSON-файлы в `F:/Email_Marketing_Repository/reports/rank-tracking/`.

---

## 4. Частые ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `403 forbidden` в GSC | SA не добавлен в GSC как Reader | Добавьте email SA в Search Console → Users |
| `invalid_grant` у Yandex | Токен истёк или был отозван | Повторите OAuth-flow |
| `siteUrl does not match` | Неправильный `SITE_URL` в скрипте | Убедитесь, что `https://kredato.com/` точное совпадение с ресурсом в GSC |
| Пустой результат | Ключевые слова не индексированы / нет трафика | Убедитесь, что в reports/keywords корректный список |

---

## 5. Резервное копирование ключей

Храните JSON-ключи **вне репозитория** (например в `C:\Users\User\.secrets\`). В скриптах указывайте абсолютный путь через env var. Никогда не добавляйте ключи в git.
