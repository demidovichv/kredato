---
tags: [infra, secrets, template, security]
---

# Шаблон секретов (secrets) — НЕ КОММИТИТЬ РЕАЛЬНЫЕ КЛЮЧИ

> Этот файл — шаблон. Копируй в `secrets.local.md` (который в .gitignore) и заполняй реальными данными.
> Никогда не пиши реальные прокси/IP/ключи в этот файл или в vault — они попадут в Obsidian Sync / git.

## Структура (заполнить в secrets.local.md)

```markdown
# ЛОКАЛЬНЫЕ СЕКРЕТЫ — не коммитить

## VPS
- VPS_IP: ___
- VPS_USER: operator
- SSH_KEY_PATH: ~/.ssh/id_ed25519_vps

## Прокси (матрица из proxies.md)
- op-hh-01: socks5://___:___
- op-vk-01: socks5://___:___
- op-partner-01: socks5://___:___
- op-mail-01: socks5://___:___

## Аккаунты
- HH.ru: ___ / ___ (привязан к op-hh-01)
- VK (Senler): ___ / ___ (привязан к op-vk-01)
- Партнёрка #1: ___ / ___ (привязан к op-partner-01)

## SMTP / майлер
- SMTP_HOST: ___
- SMTP_USER: ___
- SMTP_PASS: ___

## Партнёрки (ЛК — нужны креды для авто-мониторинга офферов)
- leads_su_email: ___    # webmaster.leads.su (CPA-сеть)
- leads_su_pass: ___
- pampadu_email: ___     # agents.pampadu.ru (партнёрские продажи)
- pampadu_pass: ___
> Примечание: публичный анализ агентами идёт БЕЗ кредов.
> Креды нужны только для автоматического парсинга каталога офферов из ЛК.
> Пользователь предоставит при необходимости.

## Statister-Mail.ru (защита)
- API_KEY: ___
- WEBHOOK: ___
```

## 🔒 Правила безопасности

1. `secrets.local.md` — в `.gitignore` и исключён из Syncthing/Obsidian Sync
2. Реальные IP/ключи НЕ в vault (только в `secrets.local.md` локально на ПК)
3. SSH-ключи только в `~/.ssh`, права 600
4. При утечке — сменить прокси + аккаунты (см. матрицу [[proxies]])

## .gitignore (добавить в vault)
```
secrets.local.md
.env
*.key
```

---
*См. [[vps_setup]], [[proxies]]*
