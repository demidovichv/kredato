---
tags: [00_project, process, definition-of-done, quality-gate]
---

# Definition of Done (DoD) — наш email-проект

> Версия: 1.0 · Статус: ACTIVE · Обновлён: 2026-07-08
> Адаптировано из `AI_FINANCE_FACTORY/00_Project/05_DEFINITION_OF_DONE.md` (только чтение, исходник не изменён).
> Назначение: задача (или прогон cron-агента) считается завершённой только при выполнении ВСЕХ применимых критериев.

---

## ✅ Критерии завершения

Задача закрывается только при выполнении **ВСЕХ** применимых пунктов:

### 1. Acceptance Criteria выполнены
Все критерии приёмки задачи выполнены (или прогон агента дал ожидаемый артефакт).

### 2. Compliance PASS
Если затрагивает закон/платформу/спам — проверка по [[compliance_policy]] дала PASS.
- Рассылка: opt-in + маркировка + нет спама.
- Оффер: соответствие правилам Leads.su / Pampadu.

### 3. Security PASS (если применимо)
Если затрагивает секреты/инфраструктуру — проверка по [[security_policy]].
- Нет секретов в vault/логах.
- Доступы корректны.

### 4. Tests / Validation PASS (если применимо)
- Скрипт отработал без ошибок (`exit 0`).
- Выхлоп проверен (не пустой, не обрезан).
- Для мониторов: запись добавлена в `reports/`.

### 5. Documentation Updated
Затронутая документация обновлена (README, планы, карта vault).

### 6. Knowledge Updated
Новые знания/решения зафиксированы (память, `reports/`, решения).

### 7. Repository / Vault Clean
- Нет временных файлов.
- Нет дублей на `C:\Users\User\` (проверка всех локаций!).
- Vault синхронизирован.

### 8. No Regression
Изменения не сломали существующий функционал (мониторы работают, ссылки не битые).

### 9. Deliverables Verified
Ожидаемые результаты созданы и проверены (отчёт, файл, запись).

### 10. Artifact Integrity
Артефакты открываются без ошибок, ссылки корректны, нет битых зависимостей.

### 11. Logging Complete
Действия зафиксированы (лог агента, изменения, ошибки).

### 12. Decision Recorded (если применимо)
Изменение стратегии/архитектуры → решение в `reports/decisions.md`.

### 13. Rollback Readiness (если применимо)
Для инфры/данных — есть процедура отката (бэкап, RTO < 15 мин).
- См. [[vps_setup]] (бэкап/Syncthing).

---

## ☑️ DoD Checklist (перед закрытием)

☐ Acceptance Criteria выполнены
☐ Compliance PASS (если нужно)
☐ Security PASS (если нужно)
☐ Validation PASS
☐ Documentation Updated
☐ Knowledge Updated
☐ Vault Clean (нет дублей на C:)
☐ No Regression
☐ Deliverables Verified
☐ Artifact Integrity
☐ Logging Complete
☐ Decision Recorded (если нужно)
☐ Rollback Readiness (если нужно)

Если хотя бы один пункт отсутствует — задача остаётся в Review.

---

## 🚨 Нарушение DoD

Если задача закрыта без DoD:
- возврат в Review;
- фиксация в логах;
- анализ причины.

Эскалация: 1 нарушение → возврат; 2 → предупреждение; 3 → Owner.

---

*См. также: [[compliance_policy]], [[security_policy]], [[automation_agents]] (роли крон-агентов)*
