# Branch Protection — настройка четвёртого барьера

> **Этот файл — инструкция для человека, а не конфигурация.**
> Branch protection нельзя закоммитить в репозиторий: это настройка GitHub на
> стороне платформы. Именно поэтому она и является внешним по отношению к
> репозиторию enforcement — агент физически не может её изменить через PR.
>
> `CODEOWNERS` без включённого branch protection — это **декларация, а не
> enforcement** (Reviewer.md §10). Пока пункты ниже не выполнены,
> control plane считается несуществующим.

---

## Вариант A — через веб-интерфейс

`Settings → Branches → Add branch protection rule`

Branch name pattern: `main`

Включить:

| Настройка | Значение | Зачем |
|---|---|---|
| Require a pull request before merging | ✅ | Запрет прямого push в main |
| — Require approvals | ✅ (минимум 1) | Merge не может быть безмолвным |
| — Dismiss stale approvals on new commits | ✅ | Агент не дописывает код после одобрения |
| — **Require review from Code Owners** | ✅ | Активирует CODEOWNERS как enforcement |
| — Require approval of the most recent push | ✅ | **Запрет self-approval**: автор пуша не может сам одобрить |
| Require status checks to pass | ✅ | Подключает CI-барьер |
| — Required checks | `Protected paths diff check`, `Block autonomous accept` | Именно эти джобы из workflow |
| — Require branches to be up to date | ✅ | Diff считается против актуального main |
| Require conversation resolution | ✅ | Замечания ревьюера нельзя проигнорировать |
| Do not allow bypassing the above settings | ✅ | **Критично**: иначе admin/бот обходит всё |
| Restrict who can push to matching branches | ✅ → только человек-владелец | Явный allowlist |
| Allow force pushes | ❌ | Запрет перезаписи истории (важно для ledger) |
| Allow deletions | ❌ | Запрет удаления main |

---

## Вариант B — через `gh` CLI

Выполнять **человеку**, со своего аккаунта, не из CI:

```bash
gh api -X PUT repos/VlaD-KH/DentalAi/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -F "required_status_checks[strict]=true" \
  -f "required_status_checks[contexts][]=Protected paths diff check" \
  -f "required_status_checks[contexts][]=Block autonomous accept" \
  -F "enforce_admins=true" \
  -F "required_pull_request_reviews[required_approving_review_count]=1" \
  -F "required_pull_request_reviews[require_code_owner_reviews]=true" \
  -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -F "required_pull_request_reviews[require_last_push_approval]=true" \
  -F "required_conversation_resolution=true" \
  -F "allow_force_pushes=false" \
  -F "allow_deletions=false" \
  -F "restrictions=null"
```

---

## Отдельно: права GitHub Actions

`Settings → Actions → General → Workflow permissions`

- Выбрать **Read repository contents and packages permissions** (не write).
- Снять галочку **Allow GitHub Actions to create and approve pull requests**.

Причина: иначе `GITHUB_TOKEN` внутри workflow может одобрить PR, созданный
агентом, — это самоодобрение через обходной путь (Reviewer.md §9).

## Отдельно: аккаунт харнаса

Если харнас работает под отдельным аккаунтом / GitHub App:

- роль в репозитории: **Write**, но **не** Maintain и не Admin;
- аккаунт **не** должен входить в CODEOWNERS;
- аккаунт **не** должен входить в bypass-список branch protection;
- у аккаунта не должно быть прав `Allow specified actors to bypass required
  pull requests`.

---

## Проверка (Phase G из Reviewer.md §17)

Control plane считается существующим только после того, как выполнены и
**проверены на практике** следующие сценарии:

```
[ ] 1. Прямой push в main от человека → ОТКЛОНЁН
[ ] 2. Прямой push в main от аккаунта харнаса → ОТКЛОНЁН
[ ] 3. PR, меняющий backend/app/services/qa/ → CI выдал requires_human=true, merge заблокирован
[ ] 4. PR, меняющий evolution/policy/ → требует approval CODEOWNERS
[ ] 5. PR, меняющий evolution/policy/ И frontend/ одновременно → отклонён по AP-01
[ ] 6. PR от бота, одобренный самим ботом → merge недоступен
[ ] 7. PR, меняющий только frontend/components/TelemetryDock.tsx → CI зелёный, requires_human=false
[ ] 8. PR, добавляющий новый файл в backend/app/services/ → CRITICAL (fail-safe сработал)
[ ] 9. PR, меняющий тест вместе с продуктовым кодом → HIGH
[ ] 10. PR, добавляющий симлинк → отклонён по AA-01
```

Пункты 1–10 должны быть **фактически выполнены и задокументированы**, а не
отмечены по факту прочтения. Только после этого фиксируется baseline commit и
заполняются поля `baseline_commit` / `reviewed_by` / `reviewed_at` в обоих
policy-YAML.
