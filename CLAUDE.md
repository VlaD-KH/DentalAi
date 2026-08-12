# DentalAi — контекст для Claude Code

Этот файл загружается всегда. Держим его коротким — детали лежат в файлах
ниже, здесь только карта и обязательные правила.

## Что это за проект

MDR EU 2017/745-регулируемая платформа автоматизации зуботехнической
CAD/CAM-лаборатории, идущая к supervised self-evolution kernel (Phase 0 →
Phase 4+, см. `DentalAi_MASTER_TZ_v2.md`). Сейчас — **Phase 0**
(человеко-контролируемая разработка, автономная мутация ещё не включена).

## Нормативные документы (читать в этом порядке при онбординге в задачу)

1. `bible.md` — источник истины по клиническим порогам/допускам.
2. `Reviewer.md` — правила безопасности control plane (§5 — граф enforcement
   защищён от самоизменения; §6 — принадлежность к Zone E ≠ auto-accept;
   §12 — композиционная защита от серии мелких патчей).
3. `DentalAi_MASTER_TZ_v2.md` — консолидированное ТЗ. Part IV — активные
   Задачи Phase 0 (у каждой инлайн-строка `**Skills:** ...` — какие скиллы
   вызывать и в каком порядке, не полагайся на автоматический
   attention-механизм). Part VIII — роли LLM Router. Part IX — покрытие
   принципов IMMUNE. Part X — почему нормативные доки НЕ векторизуются в RAG.
   Part XI — паттерн цикла разработки (см. `dentalai-dev-cycle` skill ниже).
4. `CHANGELOG.md` — что реально сделано (перепроверяй заявления, не
   доверяй им на слово).

## Zone-модель (авторитет: `evolution/policy/protected_paths.yaml`)

- **Zone R** (Regulated Core) — клиническая логика (geometry, crown_gen,
  margin, segmentation, cam, qa, mdr, ingestion, order_service.py,
  mcp/server.py, orders_router.py, schemas.py, db/, shared/constants/,
  simulations/, bible.md). Автономная мутация запрещена всегда.
- **Zone P** (Policy Plane) — evolution/policy/*, CODEOWNERS, .github/,
  evolution/evaluator.py, evolution/mutation_api.py, evolution/ledger.jsonl.
  Агент не может редактировать то, что его ограничивает.
- **Zone I** (Infrastructure) — Dockerfile*, docker-compose*.yml,
  pyproject.toml, package*.json, scripts/, .env.example, .gitignore.
- **Zone T** (Tests) — backend/tests/. Правка теста + продуктового кода в
  одном патче поднимает риск до HIGH.
- **Zone E** (Evolvable Product) — явный allowlist. Всё не перечисленное
  считается PROTECTED (`default_policy.unmatched_path: PROTECTED`).

Авторитетный источник классификации — **`git diff --name-only`**, а не
самоотчёт модели о зоне. Локально это дублирует
`.claude/hooks/protected_paths_guard.py` (PreToolUse на Edit|Write:
deny Zone P, ask Zone R/I/T/unmatched, allow Zone E) — это ранний
человеко-ориентированный сигнал, а не замена CI
(`.github/workflows/control-plane-enforcement.yml`).

## Как подключать skills к задаче

- `dentalai-dev-cycle` — роутер: DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP,
  сопоставляет каждый этап с одним из 24 установленных `.claude/skills/*`
  (agent-skills: spec-driven-development, test-driven-development,
  code-review-and-quality, git-workflow-and-versioning и т.д.). Смотри
  первым при начале любой новой Задачи.
- `dentalai-control-plane-review` — при работе с policy-файлами
  (protected_paths.yaml, risk_classification.yaml, CODEOWNERS,
  .github/workflows/, evolution/evaluator.py, evolution/mutation_api.py)
  или при верификации control-plane изменений перед merge.

## Обязательные правила для агента

1. TDD для Zone R/T: тест, воспроизводящий дефект, пишется ДО фикса
   (пример: `test_batch25_qa_inspector_fails_on_thin_geometry`).
2. Никогда не доверяй письменному заявлению о статусе тестов
   (CHANGELOG, docstring, commit message) — перезапускай сам.
3. Не коммить сообщения с необработанными backtick/`$` через `-m` — это
   command substitution в bash. Используй `git commit -F file.txt`.
4. `git push` — только пользователь, своими credentials. Никогда не
   запрашивай и не обрабатывай API-ключи/токены.
5. Перед изменением Zone P/R файла — показать реальный diff, не
   применять вслепую.

## Известные ограничения текущей рабочей среды (обновлять по мере устранения)

- Нет Docker, root/sudo, живого Postgres в Cowork-песочнице — Задачи 0.1
  (Prisma), 0.2 (AuditLog append-only), 0.3 (JWT auth) не верифицируются
  end-to-end там; нужна либо машина пользователя, либо CI.
- `fastapi`/`prisma` не установлены по умолчанию —
  `pytest backend/tests/` не соберёт test_batch10/12/24 без
  `pip install fastapi prisma`.
