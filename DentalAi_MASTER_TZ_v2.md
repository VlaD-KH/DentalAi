# DentalAi — Мастер-ТЗ: от текущего состояния до первого self-evolution цикла в собственной оболочке

**Версия:** 2.0 (консолидированная)
**Дата:** 2026-08-11
**Роль автора:** Independent Control-Plane Reviewer
**Заменяет:** `DentalAi_Self_Evolution_Kernel_TZ.md` v1 (черновик), объединяет `DentalAi_AUDIT_REPORT.md`, `Reviewer.md`, `Синтез финального пайплайна и архитектуры Solo-лаб.md`

> **Для кого этот документ:** для AI-агентов (Claude Code / Antigravity 2.0), которые будут реализовывать задачи, и для человека-владельца, который выполняет шаги, недоступные агентам.
>
> **Ключевое ограничение всего документа:** агент реализует Phase 0–3, но **не создаёт и не изменяет** файлы control plane. Они уже созданы человеком до подключения агента.

---

## Часть I. Фактическое состояние проекта (не нормативное, а измеренное)

Репозиторий `VlaD-KH/DentalAi` был склонирован и проверен. Ниже — что реально есть, а не что описано в документации.

### I.1. Что уже исправлено из аудита ✅

| Пункт | Статус | Проверка |
|---|---|---|
| A.1 `action: str` в TSX | ✅ исправлено | `action: string;` |
| B.1 `np.random.randn()` в QA | ✅ убран | нет вхождений `random` в `qa_inspector.py` |
| A.8 `broadcast_log()` мёртвый | ✅ вызывается | `main.py:65` |
| D.1 CORS wildcard | ✅ исправлено | явные origins localhost:3000 |
| F.1 валидация FDI | ✅ есть тест | `test_batch27_invalid_fdi_validation` |
| — `.env.example`, `CHANGELOG.md` | ✅ созданы | |

### I.2. Что НЕ исправлено — блокеры Phase 0 ❌

| Пункт | Факт | Последствие |
|---|---|---|
| **C.1** персистентность заказов | `order_service.py:16` — `self._orders_db: Dict[str, OrderResponse] = {}` | Заказы теряются при рестарте |
| **B.8** AuditLog | `order_service.py:17` — `self._audit_logs: List[Dict] = []` | **Нарушение MDR: 10-летнее хранение не обеспечено.** Лог в оперативной памяти |
| **C.2** Prisma | Нет ни одного `from prisma import` во всём `backend/app` | Схема БД — мёртвый артефакт |
| **D.3** аутентификация | Нет `Depends`/`HTTPBearer`/JWT ни в одном роутере | Медданные пациентов доступны без авторизации |

> ⚠️ Тест `test_batch26_prisma_persistence_and_audit.py` **проходит**, но проверяет запись в Python-список, а не в PostgreSQL. Зелёный тест здесь не означает выполненное требование MDR.

### I.3. Состояние control plane — критический разрыв ❌

| Слой | Наличие | Оценка |
|---|---|---|
| 1. `protected_paths.yaml` | ✅ есть (v1.0) | **недостаточен** — см. II.1 |
| 2. `risk_classification.yaml` | ✅ есть (v1.0) | **недостаточен** — см. II.2 |
| 3. `CODEOWNERS` | ✅ есть (v1.0) | **недостаточен** — нет catch-all |
| 4. **CI enforcement** | ❌ **директории `.github/` не существует** | **Слоя нет вообще** |
| 5. **Branch protection** | ❓ невозможно проверить извне | Требует подтверждения человеком |

Это ровно то состояние, которое `Reviewer.md` §18 описывает как:

> `CONTROL PLANE IS DESCRIBED IN MARKDOWN`, а не `CONTROL PLANE EXISTS`

Причём `test_batch27_reviewer_policy_files_exist` проверяет только `Path(...).exists()` — то есть тест зелёный, а барьера нет.

### I.4. Пути из ТЗ v1, которых не существует

`backend/app/mcp/orchestration/` · `prompts/agents/*` · `evolution/metrics/` · `evolution/experience/` · `evolution/mutation_api.py` · `evolution/evaluator.py`

Они создаются в Phase 1–2 (см. Часть IV).

---

## Часть II. Ревью и рефакторинг control plane (выполнено)

### II.1. Дефекты `protected_paths.yaml` v1.0 и их устранение в v2.0

| # | Дефект v1.0 | Риск | Исправлено в v2.0 |
|---|---|---|---|
| 1 | `backend/app/mcp/server.py` **не защищён** | 🔴 Файл вызывает geometry/QA/MDR и генерирует MDR-паспорт | Добавлен в Zone R |
| 2 | `evolution/mutation_api.py` и `evaluator.py` **не защищены** | 🔴 Агент удаляет проверку — вся политика обходится (Reviewer.md §5) | Добавлена секция `enforcement_dependency_graph` |
| 3 | `.github/` **не защищён** | 🔴 Агент добавляет workflow с write-правами = privilege escalation | Добавлен в Zone P |
| 4 | `segmentation/`, `margin/`, `ingestion/` отсутствуют | 🔴 Клинические модули без защиты | Добавлены в Zone R |
| 5 | `bible.md` отсутствует (хотя есть в ТЗ §2.1) | 🟠 Нормативный источник изменяем | Добавлен |
| 6 | Защищён только `db/schema.prisma`, не `db/` | 🟠 Новый файл в `db/` обходит защиту | Расширено до директории |
| 7 | Zone E = `frontend/` и `backend/app/api/` **целиком** | 🔴 Даёт агенту `orders_router.py` — файлы скана и данные пациента | Заменено явным allowlist |
| 8 | Нет `pyproject.toml`/`package.json`/Dockerfile | 🔴 Supply chain: новая зависимость = произвольный код | Новая **Zone I** |
| 9 | Нет `backend/tests/` | 🟠 Агент правит тесты вместе с кодом → обход verification | Новая **Zone T** с эскалацией |
| 10 | Не определено поведение для неперечисленных путей | 🔴 Undefined = потенциально разрешено | `default_policy.unmatched_path: PROTECTED` |
| 11 | Нет защиты от path aliasing и симлинков | 🟠 Обход через переименование | Секция `anti_aliasing_rules` (AA-01…AA-04) |
| 12 | Нет композиционной защиты | 🟠 Серия мелких патчей ослабляет политику (Reviewer.md §12) | Секция `compositional_rules` (CR-01…CR-03) |

### II.2. Дефекты `risk_classification.yaml` v1.0

| # | Дефект | Исправление |
|---|---|---|
| 1 | `autonomous_mutation: true` **и** `human_approval_required: true` одновременно у `backend/app/agents/` — неопределённое поведение | Введена секция `risk_levels` с явной семантикой каждого уровня |
| 2 | Отсутствуют `qa_agent.md` / `cam_agent.md` (HIGH-кейс из ТЗ §6) | Добавлены с `zone: E, risk: HIGH` |
| 3 | Не определён порядок разрешения конфликтов правил | `MOST_SPECIFIC_PATH_WINS` |
| 4 | Не определён риск для неперечисленного пути | `default_risk_for_unmatched: CRITICAL` |
| 5 | Не определено поведение смешанного diff | `mixed_diff_strategy: MAX_RISK_WINS` |
| 6 | Не указано, что авторитетен `git diff`, а не поле `zone` в proposal | `diff_is_authoritative: true` |
| 7 | Нет anti-gaming списка метрик | `forbidden_primary_metrics` / `allowed_primary_metrics` |
| 8 | Нет абсолютных запретов | `absolute_prohibitions` AP-01…AP-06 |

### II.3. Дефекты `CODEOWNERS` v1.0

Главный: **отсутствует catch-all `*`**. В синтаксисе CODEOWNERS побеждает *последнее* совпавшее правило, поэтому catch-all должен стоять **первым**. Без него любой файл, не перечисленный явно (`main.py`, `config.py`, `docker-compose.yml`, весь `frontend/`), не имеет владельца и может быть смержен без ревью.

Также отсутствовали: `mcp/server.py`, `.github/`, `evolution/evaluator.py`, `evolution/mutation_api.py`, инфраструктура, тесты.

### II.4. Верификация нового control plane

Enforcement-скрипт протестирован на реальной копии репозитория — **24/24 теста проходят**:

```
✅ zone_r_qa · zone_r_mdr · zone_r_cam · zone_r_thresholds · zone_r_mcp_server · zone_r_prisma
✅ zone_p_self · zone_p_evaluator · zone_p_mutation_api · zone_p_codeowners · zone_p_ci
✅ zone_i_supply_chain · zone_i_npm
✅ unmatched_failsafe (новый файл в services/ → CRITICAL)
✅ zone_e_but_high (qa_agent.md → HIGH, не LOW)
✅ mixed_diff → CRITICAL · test_co_modification → HIGH
✅ позитивный контроль: TelemetryDock.tsx → LOW, requires_human=false
```

---

## Часть III. Артефакты, создаваемые ЧЕЛОВЕКОМ до подключения агента

> 🔒 **Ни один из этих файлов не должен создаваться или изменяться AI-агентом.**
> Это граница роли Reviewer (`Reviewer.md` §19).

| Файл | Назначение | Статус |
|---|---|---|
| `evolution/policy/protected_paths.yaml` | Границы зон R/P/I/T/E | ✅ подготовлен (v2.0) |
| `evolution/policy/risk_classification.yaml` | Уровни автономии | ✅ подготовлен (v2.0) |
| `evolution/policy/BRANCH_PROTECTION.md` | Инструкция настройки платформы | ✅ подготовлен |
| `CODEOWNERS` | Человеческое владение | ✅ подготовлен (v2.0) |
| `.github/workflows/control-plane-enforcement.yml` | CI-барьер | ✅ подготовлен |
| `.github/scripts/enforce_control_plane.py` | Классификатор фактического diff | ✅ подготовлен, протестирован |
| `backend/tests/test_batch28_control_plane_enforcement.py` | Тест реального enforcement | ✅ подготовлен, 24/24 |
| **Branch protection на `main`** | Четвёртый барьер | ⬜ **выполняет человек в GitHub UI** |

---

## Часть IV. ТЗ для AI-агентов (Claude Code / Antigravity 2.0)

### Общие правила для агента (действуют во всех фазах)

```
1. Агент НИКОГДА не изменяет: evolution/policy/, CODEOWNERS, .github/,
   evolution/evaluator.py, evolution/mutation_api.py, evolution/metrics/.
2. Агент НИКОГДА не изменяет Zone R без явной задачи от человека в рамках
   Phase 0 (Phase 0 — это обычная разработка человеком-с-агентом, НЕ self-evolution).
3. Агент не имеет merge-прав. Только `open_pull_request`.
4. Один PR = одна фаза = одна задача. Не смешивать Zone R и Zone E в одном PR.
5. Не изменять тесты вместе с продуктовым кодом в одном PR.
6. Перед началом фазы прочитать evolution/policy/*.yaml и убедиться,
   что задача не выходит за границы.
```

---

### PHASE 0 — Устранение блокеров (обычная разработка, не self-evolution)

> Phase 0 выполняется агентом **под контролем человека через PR**, потому что затрагивает Zone R. Self-evolution kernel здесь ещё не работает.

#### Задача 0.1 — Персистентность заказов (аудит C.1, C.2)
- Подключить Prisma-клиент: `from prisma import Prisma` в `backend/app/db/client.py`.
- Переписать `OrderService` с `self._orders_db: Dict` на асинхронные запросы к PostgreSQL.
- Сохранить существующий публичный интерфейс (`create_order`, `get_order`, `list_orders`, `update_status`), чтобы тесты batch10/26 не сломались по контракту.
- Добавить фикстуру очистки БД между тестами (аудит H.1).
- **Критерий приёмки:** заказ, созданный до `docker compose restart backend`, доступен после рестарта.

#### Задача 0.2 — Реальный AuditLog (аудит B.8) 🔴 MDR-критично
- Заменить `self._audit_logs: List[Dict]` на запись в таблицу `AuditLog` через Prisma.
- Реализовать **append-only** на уровне БД: отозвать UPDATE/DELETE у роли приложения, оставить только INSERT/SELECT.
- Писать запись при каждом: создании заказа, смене статуса, вызове MCP-инструмента, результате QA, генерации MDR-паспорта.
- **Критерий приёмки:** попытка `UPDATE audit_log` из-под роли приложения завершается ошибкой прав БД, а не только отсутствием кода.

#### Задача 0.3 — Аутентификация (аудит D.3)
- JWT/OAuth на `orders_router.py`, MCP-сервере и WebSocket `/ws/logs`.
- Убрать дефолтные креды из `config.py` (аудит D.2), только через `.env`.
- Не пробрасывать порты `5432`/`6379` наружу в `docker-compose.yml` (D.4).
- Валидация загружаемых файлов по magic bytes + лимит размера (D.5).

#### Задача 0.4 — Реальные измерения геометрии (аудит B.1–B.4)
> Если ещё не сделано полностью: `measured_min_thickness` через raycasting/nearest-surface distance, `measured_connector_area` из фактического сечения, а не константа `10.17`.
- **Критерий приёмки:** тест детерминирован (нет `np.random` без seed) и падает при подсовывании заведомо тонкой геометрии.

#### Задача 0.5 — Живая связь MCP ↔ реальные данные (аудит A.5–A.7, B.5)
- `compile_5axis_gcode` принимает `fdi`/`order_id`, PROGRAM ID формируется из них.
- `generate_mdr_passport` берёт `patient_id`/`doctor_name`/`clinic_name` из БД по `order_id`, **не хардкод**.
- Генеративные MCP-инструменты используют реальный меш по `prep_mesh_id`, а не `trimesh.creation.cone(...)`.
- Использовать `ZIRCONIA_SHRINKAGE_FACTOR_MIN/MAX` из `thresholds.py` вместо хардкода `1.22` (аудит C.9).

**Definition of Done Phase 0:**
```
[ ] Заказ переживает рестарт контейнера
[ ] AuditLog пишется в PostgreSQL и защищён от UPDATE/DELETE на уровне прав БД
[ ] Ни один эндпоинт не отвечает без валидного токена
[ ] MDR-паспорт содержит данные конкретного заказа
[ ] G-код содержит реальный FDI и order_id
[ ] Все тесты детерминированы
```

---

### PHASE 1 — Инфраструктура эволюции (Zone E скелет)

> Control plane к этому моменту уже зафиксирован человеком. Агент строит внутри коридора.

#### Задача 1.1 — Каркас `evolution/`
Создать (файлы в Zone P создаёт человек, агент создаёт только рабочие директории):
```
evolution/
├── experience/.gitkeep
├── backlog/.gitkeep
├── proposals/.gitkeep
├── checkpoints/.gitkeep
└── ledger.jsonl            (пустой, append-only)
```

#### Задача 1.2 — Разделение MCP на клинический и оркестрационный слой
> Это ключевая архитектурная задача фазы.
- Создать `backend/app/mcp/orchestration/` — маршрутизация, ретраи, порядок вызова агентов.
- **Не переносить** туда клиническую логику: `mcp/server.py` остаётся в Zone R.
- Оркестрация вызывает `server.py`, но не содержит расчётов геометрии/допусков.
- **Критерий приёмки:** `grep -rE "thickness|margin|shrinkage|trimesh" backend/app/mcp/orchestration/` пуст.

#### Задача 1.3 — Слой промптов
```
prompts/agents/
├── orchestrator.md      (MEDIUM)
├── cad_specialist.md    (MEDIUM)
├── qa_agent.md          (HIGH — human approval обязателен)
└── cam_agent.md         (HIGH — human approval обязателен)
```
Наполнить ролями из `bible.md` §3.3.

#### Задача 1.4 — Mutation API (файл в Zone P — **создаёт человек по этой спецификации**)
```python
# evolution/mutation_api.py
read_file(path)                    # только чтение
list_files(scope)
propose_patch(path, patch)         # → candidate workspace, НЕ рабочее дерево
validate_patch(patch)              # syntax + scope + protected-paths + размер diff
open_pull_request(patch, proposal) # ЕДИНСТВЕННЫЙ путь наружу; merge недоступен
create_checkpoint(objective)
rollback(checkpoint)
```
Запрещено: произвольный shell, `subprocess`, `git push` в main, `git merge`.

---

### PHASE 2 — Experience loop и телеметрия

#### Задача 2.1 — Реальная телеметрия
- Подключить `frontend/app/page.tsx` к REST `/api/orders` и WS `/ws/logs` (аудит C.7).
- Оживить `AgentSwarmLogger` реальными логами вместо статики.
- Связать SVG-дуги `TelemetryDock` с числовыми значениями (аудит E.4).
- Добавить сбор метрик из `allowed_primary_metrics`.

#### Задача 2.2 — Observation log
`evolution/experience/observations.jsonl` — append-only, с provenance:
```json
{"ts":"...","source":"ws_logs","event":"...","session":"...","raw":true}
```
Наблюдение хранится **отдельно** от вывода/интерпретации.

#### Задача 2.3 — Improvement Backlog
`evolution/backlog/improvement_backlog.jsonl` с обязательным provenance merge:
```json
{"id":"UI-001","kind":"ux_problem","summary":"...","evidence_count":14,
 "evidence_refs":["obs_id_1","obs_id_2"],"confidence":0.72,"status":"open",
 "merged_from":[],"merge_rationale":null}
```
При сомнении в дедупликации — **не сливать** (Ouroboros §7).

---

### PHASE 3 — Первый цикл эволюции, только LOW risk

#### Задача 3.1 — Evaluator (файл в Zone P — **создаёт человек по этой спецификации**)
```python
# evolution/evaluator.py — ДЕТЕРМИНИРОВАННЫЙ, БЕЗ LLM-ВЫЗОВОВ
def evaluate(baseline_metrics, candidate_metrics, metric_definition) -> Decision
```
Читает `evolution/metrics/ux_metrics_v1.yaml`, сравнивает по формуле. Никаких обращений к API моделей.

#### Задача 3.2 — Synthetic test fixtures
`data/orders/test_fixtures/` — минимум 20 синтетических заказов для прогона.
**A/B на реальных клинических заказах запрещён (MDR).**

#### Задача 3.3 — Первый цикл
Ограничить **только** `frontend/components/TelemetryDock.tsx`. Один цикл. Результат → `ledger.jsonl` с `evaluation_type: synthetic_proxy`.

---

### PHASE 4+ — Переход в собственную оболочку

После успешного цикла Phase 3 разработка переносится внутрь приложения:
- Оркестратор внутри DentalAi формирует proposal из backlog.
- LLM-вызовы — только для генерации патча, не для оценки.
- **Экономия токенов:** контекст собирается из локальных `observations.jsonl` + `backlog.jsonl` + целевого файла, а не из полного репозитория. Один цикл ≈ 1 файл + 1 proposal + diff.
- **Приватность:** данные пациентов никогда не попадают в контекст LLM — Zone R закрыта, а observations содержат только UX-телеметрию (клики, тайминги, коды ошибок), не клинические данные. Это обеспечивается тем же protected_paths, что и запрет мутации.

---

## Часть V. Полный пайплайн

```
                        ЧЕЛОВЕК (Control-Plane Owner)
                                    │
                    создаёт policy + CI + branch protection
                                    │  [ФИКСАЦИЯ BASELINE COMMIT]
                                    ▼
    ┌──────────────────── CONTROL PLANE (неизменяем агентом) ────────────────────┐
    │  protected_paths.yaml → risk_classification.yaml → CODEOWNERS → CI → BP    │
    └───────────────────────────────────┬───────────────────────────────────────┘
                                        │ коридор
    ═════════════════════════════════════▼═════════════════════════════════════
                              ПОЛЬЗОВАТЕЛЬ (Solo-техник)
                                        ↓
                          ПРИЛОЖЕНИЕ (dashboard + агенты)
                                        ↓
                   OBSERVATION  →  experience/observations.jsonl
                                        ↓
                            REFLECTION (Observer)
                                        ↓
                        backlog/improvement_backlog.jsonl
                                        ↓
                          EVOLUTION PROPOSAL (Proposer)
                            objective + scope + metric + guardrails
                                        ↓
        ┌───────────────── POLICY GATE (git diff --name-only) ─────────────────┐
        │  Zone R/P/I  → CRITICAL → BACKLOG ONLY, PR запрещён                  │
        │  HIGH        → PR + обязательный human approval                      │
        │  MEDIUM      → PR + canary + human approval                          │
        │  LOW         → PR + auto-evaluate                                    │
        └──────────────────────────────┬──────────────────────────────────────┘
                                       ↓
                            CANDIDATE PATCH (workspace)
                                       ↓
                     VERIFICATION  (syntax · types · tests · scope)
                                       ↓
             INDEPENDENT EVALUATION (evaluator.py — детерминирован, не LLM)
                       fixed metrics · guardrails · minimum_sample
                                       ↓
                   CANARY на synthetic fixtures (не на пациентах!)
                                       ↓
                    ┌──────────────────┴──────────────────┐
                 ACCEPT                                 REJECT
              (PR → человек merge)                    ROLLBACK
                    └──────────────────┬──────────────────┘
                                       ↓
                   CHECKPOINT + ledger.jsonl (append-only)
                                       ↓
                          НОВАЯ ВЕРСИЯ → новый OBSERVATION
                                       ↺
```

---

## Часть VI. Инструкция пользователю — что делать дальше

### Шаг 1. Установить control plane (только вручную, ~20 минут)

```bash
cd DentalAi
git checkout -b control-plane-baseline

# скопировать подготовленные артефакты
cp <распакованные>/CODEOWNERS .
cp <распакованные>/evolution/policy/*.yaml evolution/policy/
cp <распакованные>/evolution/policy/BRANCH_PROTECTION.md evolution/policy/
mkdir -p .github/workflows .github/scripts
cp <распакованные>/.github/workflows/*.yml .github/workflows/
cp <распакованные>/.github/scripts/*.py .github/scripts/
cp <распакованные>/backend/tests/test_batch28*.py backend/tests/

# проверить локально
python -m pytest backend/tests/test_batch28_control_plane_enforcement.py -q
```

Ожидаемо: **24 passed**.

### Шаг 2. Заполнить поля ревьюера

В обоих YAML заменить:
```yaml
baseline_commit: "<хеш коммита после merge>"
reviewed_by: "VlaD-KH"
reviewed_at: "2026-08-11"
```

### Шаг 3. Смержить и включить branch protection

```bash
git add -A && git commit -m "control-plane: baseline v2.0"
git push -u origin control-plane-baseline
# → создать PR → смержить самому (пока защита не включена)
```
Затем выполнить `evolution/policy/BRANCH_PROTECTION.md` — **это единственный шаг, который нельзя сделать кодом**.

### Шаг 4. Провести Phase G — проверку боем

Прогнать все 10 сценариев из чек-листа в `BRANCH_PROTECTION.md`. Особенно:
- PR, меняющий `backend/app/services/qa/` → CI должен упасть;
- PR, меняющий только `TelemetryDock.tsx` → CI должен быть зелёным.

Если хотя бы один сценарий ведёт себя не так — **не подключать харнас**.

### Шаг 5. Убрать слабый тест

Заменить `test_batch27_reviewer_policy_files_exist` на `test_batch28_*`. Проверка `Path.exists()` создаёт ложное чувство защищённости.

### Шаг 6. Подключить харнас

Только теперь передать агенту:
```
✅ DentalAi_MASTER_TZ_v2.md   (этот файл)
✅ DentalAi_AUDIT_REPORT.md
❌ НЕ передавать Ouroboros_Self_Evolution_Kernel_Final.md
   (generic-документ с более широким scope — риск дрейфа)
❌ НЕ передавать Reviewer.md
   (описывает роль, которую агент не должен исполнять)
```

Первая задача агенту — **Phase 0, задача 0.2 (AuditLog)**: это самый серьёзный незакрытый MDR-риск.

### Шаг 7. Порядок фаз — не нарушать

```
Phase 0 (блокеры) → Phase 1 (каркас) → Phase 2 (телеметрия) → Phase 3 (первый цикл LOW)
```

Kernel не может учиться на данных, которых нет. Пока `AuditLog` живёт в списке Python, а заказы — в памяти процесса, evolution ledger будет строиться на том же несуществующем фундаменте.

---

## Часть VII. Что осталось открытым (честно)

1. **Branch protection проверяется только человеком.** Извне репозитория подтвердить включённость нельзя. Единственная гарантия — фактический прогон сценариев из Шага 4.
2. **`enforce_control_plane.py` находится в Zone P, но исполняется в CI.** Если у аккаунта харнаса окажутся права на изменение GitHub Actions settings (вне репозитория), барьер обходится. Поэтому в `BRANCH_PROTECTION.md` отдельно указано: роль **Write**, не Maintain/Admin.
3. **`CR-01`/`CR-02` (композиционные правила) описаны, но не реализованы в CI** — для их проверки нужен ledger с историей, который появляется только в Phase 3. До этого момента защиту от серии мелких патчей обеспечивает то, что human approval требуется для всего, кроме LOW.
4. **Файл `Синтез финального пайплайна…md` добавляет требования** (S3-хранилище сканов с SHA-256, exocad `.dentalProject`, `DiskInventory` с лотами и коэффициентами усадки, параметры HSS-спекания), которые расширяют Zone R. При их реализации `protected_paths.yaml` должен быть обновлён **человеком** — новые модули `blender/`, `s3/`, `exocad/` по умолчанию попадут под fail-safe CRITICAL, что корректно, но лучше внести их явно.

---

## Часть VIII. LLM Router — распределение моделей по ролям

> Слияние `LLM_Orchestration_Pipeline_TZ.md` (несистематизированный источник, проверен на совместимость с v2.0 — противоречий с Zone R/P/E не найдено, добавлен сюда как нормативная часть; исходный файл перенесён в `docs/sources/` как первоисточник).

### VIII.1. Концепция

Гибридный (cloud-to-local) LLM Router: единый маршрутизатор, абстрагированный от конкретных названий моделей, назначающий текущий эндпоинт (frontier API / локальный vLLM / Ollama) под каждую роль агентного цикла. Стратегическая цель — постепенный переход на изолированную (air-gapped) локальную инфраструктуру по мере роста собственных мощностей.

### VIII.2. Матрица ролей

| Роль | Функция | Приоритет размещения | Требования к модели |
|---|---|---|---|
| `Observer / Memory` | сбор телеметрии, баг-репортов, скриншотов | строго локально | скорость инференса, мультимодальность (зрение), низкий reasoning |
| `Architect / Proposer` | анализ контекста, формирование ТЗ/proposal | API → локально (big LLM) | максимальный reasoning, широкое контекстное окно |
| `Coder` | генерация кода/патчей | API → локально (big LLM) | кодогенерация (TS/Python/G-code), tool-calling через FastMCP |
| `Reviewer / Gatekeeper` (LLM pre-check) | стилистическая/архитектурная проверка кандидата ДО verification | строго локально | строгое следование системному промпту, дообучается (LoRA) под правила проекта |

### VIII.3. Обязательное терминологическое разделение

**Важно:** роль `Reviewer / Gatekeeper` из VIII.2 — это LLM-модель, выполняющая **предварительный** архитектурный код-ревью кандидата. Это **не тот же компонент**, что `evolution/evaluator.py` из Части IV (Задача 3.1), который остаётся детерминированным и не делает LLM-вызовов вообще. Порядок в пайплайне:

```
CANDIDATE PATCH → LLM Gatekeeper (advisory pre-check, может отклонить рано)
                → VERIFICATION (syntax/types/tests/scope)
                → evaluator.py (детерминированная оценка метрик, НЕ LLM)
                → CANARY → ACCEPT/REJECT
```

LLM Gatekeeper не имеет права accept/reject кандидата единолично — только предварительный отсев. Финальное решение всегда за детерминированным evaluator.py + human approval согласно `risk_classification.yaml`.

### VIII.4. LLM Gatekeeper — два независимых под-слоя

> Источник: Разжигаев А., «Мой агент Ouroboros побил Codex с Claude Code…», Habr, 31.07.2026 (habr.com/ru/companies/airi/articles/1065428) — описание production-ревью Ouroboros, применённое к текущей продакшен-версии проекта, а не к тому черновику `prompts/SAFETY.md`, что разбирался в `Ouroboros_Claudexor_analysis.md`.

Однослойного LLM Gatekeeper недостаточно: ревьюер-LLM может разделять слепые зоны с моделью, которую он проверяет (тот же класс ошибок, то же обучение). В production-версии Ouroboros это решается **двумя независимыми под-слоями**, оба обязательны для HIGH/MEDIUM кандидатов (`risk_classification.yaml`):

1. **Triad review** — сам дифф читают несколько независимых моделей-ревьюеров (по возможности разных вендоров) и голосуют кворумом. Снижает риск, что одна и та же модель одобрит свою же слепую зону.
2. **Scope review** — отдельная модель с большим контекстным окном получает не дифф, а **весь связанный контекст**: затронутые файлы целиком, `bible.md`, `DentalAi_MASTER_TZ_v2.md`, соседние модули — и отвечает на другой вопрос: не ломает ли это изменение проект **как целое**, а не только строки в диффе. Любая критичная находка блокирует коммит; при сомнении — fail-closed (не проходит).

Для DentalAi это ложится в `evolution/mutation_api.py::validate_patch()` как два отдельных шага перед `evaluator.py`, а не как один общий "gatekeeper"-промпт. Zone R-патчи (если вообще когда-либо станут PR-able, что сейчас запрещено) обязаны проходить оба слоя, а не один.

---

## Часть IX. Принципы IMMUNE и их покрытие в DentalAi

> Источник: та же статья (habr.com/ru/companies/airi/articles/1065428), раздел «SOLID для самомодифицирующихся агентов: IMMUNE». Автор прямо называет это «черновиком черновика», применимым к любому проекту с автономными правками, не только к Ouroboros. Ниже — честная сверка: что из этого DentalAi уже покрывает существующим control plane, а что нет.

| Принцип | Формулировка | Покрытие в DentalAi | Вердикт |
|---|---|---|---|
| **I** — Intent before implementation | Требование важнее архитектуры важнее реализации; контрольный вопрос — «что сломается, если удалить файл и попросить агента написать его заново по докам и тестам» | Частично. `bible.md`/`DentalAi_MASTER_TZ_v2.md` — нормативный источник, но нет процедуры, которая проверяла бы регенерируемость модуля из требований | **Пробел** — стоит добавить как критерий приёмки для Zone E модулей в Phase 2+ |
| **M** — Mutations preserve coherence | Меняется не файл, а понятие с проекциями (код/схема/API/доки/тесты); изменение закончено, только когда все проекции согласованы | Не покрыто явно. `CR-01`/`CR-02` (`protected_paths.yaml`) ограничивают *объём* серии патчей, но не проверяют *согласованность* проекций одного изменения | **Пробел** |
| **M** — Meta over patch | Чинить механизм, порождающий класс ошибок, а не конкретный симптом | Не покрыто. `evolution/backlog/improvement_backlog.jsonl` (Задача 2.3) собирает наблюдения, но нет правила приоритизации «эта правка компаундится» | **Пробел**, но задел уже есть — provenance-поля в backlog-схеме подходят для дедупликации по классу проблемы |
| **U** — Unexpected states fail loud | Неожиданное состояние — стоп/явная неопределённость, не тихое угадывание | **Уже покрыто**, буквально тем же паттерном: `enforce_control_plane.py::load_yaml()` делает `sys.exit(1)` при отсутствии policy-файла вместо тихого допуска; `default_risk_for_unmatched: CRITICAL` — fail-closed по умолчанию | ✅ |
| **N** — No duplicated authority, no indispensable parts | Одна истина — один владелец; компонент может умереть, не забрав систему с собой | Частично. Владение (CODEOWNERS v2.0 с catch-all, `MOST_SPECIFIC_PATH_WINS`) покрыто хорошо. «Компонент умирает, популяция живёт» — неприменимо: в DentalAi нет модели роя одноразовых агентов, архитектура другая (один агент, один PR, человек мержит) | ✅ по SSOT, ⚠️ вторая половина принципа для текущей архитектуры не актуальна |
| **E** — Every state is explainable | Любое важное состояние восстановимо по сохранённым свидетельствам | **Уже покрыто по духу**: `evolution/ledger.jsonl` (append-only), `improvement_backlog.jsonl` с `evidence_refs`/`confidence`/`merge_rationale` — именно эта модель | ✅ |

**Итог: 2 из 6 принципов (U, E) уже реализованы в спецификации на уровне архитектуры, ещё один (N) реализован наполовину по не зависящей от решения причине (другая модель эволюции — не рой). Три (I, M-coherence, M-meta) — реальные пробелы**, которые стоит закрыть при реализации Phase 1–3, а не изобретать заново:

- **I** → добавить в Definition of Done для Zone E-модулей (Часть IV): «модуль регенерируем из своего описания в `prompts/agents/*.md` + тестов».
- **M-coherence** → в `evolution/mutation_api.py::validate_patch()` добавить проверку, что если патч меняет `backend/app/models/schemas.py` (контракт), но не трогает связанные тесты/доки той же сущности — эскалировать риск (аналогично уже существующему `TEST_CHANGE_ELEVATES_RISK`, только в обратную сторону).
- **M-meta** → при добавлении записи в `improvement_backlog.jsonl` явно спрашивать/тегировать: это симптом или класс проблемы (поле `kind: symptom | root_cause`), чтобы Proposer не чинил одно и то же место раз за разом.

## Часть X. Хранить как RAG или как нормализованный .md?

Прямой ответ из первоисточника, а не общие соображения: в собственной конституции Ouroboros (`BIBLE.md`, цитата из статьи) есть явный запрет — **«запрет подменять агентную память RAG-индексом»**. Автор формулирует это как осознанный выбор: память должна быть в контексте *до* выбора действия (always-loaded, полностью, без обрезки `[:N]`), а не доставаться реактивным поиском *после* — и отмечает, что агенты «очень настойчиво пытаются запихнуть RAG везде куда дотягиваются». На CL-Bench именно это (накопленное состояние в контексте, а не через retrieval) дало основной прирост качества.

**Рекомендация для DentalAi — то же решение, тем же обоснованием:**

- Принципы вроде IMMUNE, содержимое `bible.md`, `Reviewer.md`, `DentalAi_MASTER_TZ_v2.md` — это **нормативная, канонiчная память**, которая должна быть авторитетной и всегда полностью в контексте агента, а не результатом top-k similarity search, который может не найти нужный кусок в критичный момент. Хранить **только как нормализованный `.md`**, без векторизации.
- Этот конкретный черновик — как новую **Часть IX** внутри `DentalAi_MASTER_TZ_v2.md` (уже сделано выше), а не как отдельный висящий файл: избегаем дублирования источника истины (тот же принцип **N**).
- RAG не запрещён вообще — он уместен для другого класса данных: `evolution/experience/observations.jsonl` (Задача 2.2) — высокообъёмная сырая телеметрия (клики, тайминги, коды ошибок), где нужен semantic search по объёму, а не авторитетность каждой записи. Это архитектурно другая задача, и текущая спецификация (append-only JSONL с provenance) её не запрещает дополнить векторным индексом поверх, когда объём оправдает это — но это read-модель поверх ledger'а, не замена ему.
- Практический вывод: очистка "мусорных символов" через LLM перед сохранением — да, полезно и уже частично покрыто идеей `redactSecrets()`/нормализации из разбора Claudexor (`Ouroboros_Claudexor_analysis.md`, `packages/event-log`). Но конечный формат хранения для нормативных документов — единый `.md`, не две параллельные БД в разных форматах: два хранилища одной истины — это ровно то, что запрещает принцип **N**.

---

## Часть XI. Разбор логов проекта: паттерны цикла разработки → скиллы/хуки/тулы

> Источник данных: `git log` (16 коммитов, 49c9a93 и раньше), `CHANGELOG.md`, `DentalAi_AUDIT_REPORT.md`, `backend/tests/test_batch*.py` (27 файлов), `backend/.pytest_cache` (nodeids + lastfailed), `Reviewer.md`. Не сырые runtime-логи приложения (их нет — Phase 0 ещё не даёт персистентности, приложение по-настоящему не разворачивалось), а история разработки как таковая.

### XI.1. Найденные паттерны

**Паттерн 1 — «уверенный шип, ревью потом» (самый частый, встретился трижды).**
Коммит `2c3b5e6` и `ef512fc` заявляют «Phase 0 infrastructure... with full automated test coverage» и «100% test coverage». Спустя время (`b6060ed`) появляется `DentalAi_AUDIT_REPORT.md`, который находит: `np.random.randn()` вместо реального QA-измерения, захардкоженные MDR-данные, CORS wildcard, незащищённый `mcp/server.py` — при том что тесты всё это время были зелёными (`.pytest_cache/lastfailed` пуст). Тот же паттерн повторился на уровень выше: `protected_paths.yaml` v1.0 был «создан» (`b6060ed`), и только в этой сессии ревью v2.0 нашло в нём 12 дыр. И ещё выше: только что написанная v2.0 сама получила 3 пробела при сверке с IMMUNE (Часть IX). Верификация везде происходит **после** факта, а не как часть определения «готово».
→ Закрывается: `doubt-driven-development` (адверсариал-ревью до того, как решение зафиксировано, не после), `code-review-and-quality` (многоосевой ревью перед мержем), и уже описанный в `Reviewer.md` §7 Режим B (Adversarial Auditor) — практика спроектирована, но нигде не закреплена как обязательный шаг перед коммитом.

**Паттерн 2 — «тест зелёный ≠ требование выполнено».**
`test_batch27_reviewer_policy_files_exist` (удалён в этой сессии) проверял только `Path.exists()`. Исторически `np.random.randn()` в QA тоже проходил тесты. Зелёный CI здесь не сигнал качества.
→ Закрывается: `test-driven-development` (тест сначала должен упасть на неправильной реализации, red-green-refactor, а не просто существовать), `code-review-and-quality` явно проверяет «доказывает ли тест то, что заявлено».

**Паттерн 3 — control plane отстаёт от кода, которому он ограничивает.**
`.github/` не существовал до этой сессии, хотя `mcp/server.py` (самый чувствительный файл) уже месяц как активно менялся. Governance создаётся постфактум, а не одновременно с риском.
→ Закрывается: `ci-cd-and-automation` (гейты с первого дня, а не когда «руки дойдут»), `security-and-hardening` (threat model на этапе дизайна, не после), новая двухслойная triad/scope review из Части VIII.4.

**Паттерн 4 — документационный дрейф / нет единого источника истины.**
В корне репозитория одновременно лежат `Синтез финального пайплайна...md`, три файла `контекст - ...md`, `Reviewer.md`, `bible.md`, и теперь `DentalAi_MASTER_TZ_v2.md` — несколько версий «текущей правды», требовавших ручной сверки в этой сессии (см. Часть IX, принципы M и N — тот же диагноз, другими словами).
→ Закрывается: `documentation-and-adrs` (короткие ADR вместо расползающихся нарративных документов на каждое решение), `context-engineering` (один persistent rules-файл вместо N пересекающихся).

**Паттерн 5 — нет персистентного кросс-сессионного трекера задач.**
Прогресс живёт только в сообщениях коммитов и моём эфемерном TaskList на сессию. Прошлый раз пользователю пришлось вручную прикладывать файл с моим же прошлым анализом, чтобы вернуть мне контекст.
→ Закрывается (на человеческом слое, до Phase 1+): `productivity:task-management` (`TASKS.md`) / `productivity:memory-management` (рабочая память между сессиями Cowork) — это отдельный слой от будущего `evolution/ledger.jsonl` (тот — для автономного агента, этот — для человека+Claude прямо сейчас).

**Паттерн 6 — «batch»-нумерация уже работает как органическая система задач (это хорошо, не пробел).**
27 файлов `test_batch1...batch28`, коммиты явно ссылаются на диапазоны батчей («Batches 1-12», «Batches 23-32»). Это самодельная версия `planning-and-task-breakdown` + `incremental-implementation`, только без формального spec на входе каждого батча.
→ Не заменять, а формализовать: `spec-driven-development` перед батчем (закрывает Паттерн 1 у корня — если бы спека фиксировала критерий приёмки заранее, `np.random` не прошёл бы), `planning-and-task-breakdown` для самой нарезки.

### XI.2. Обновлённый цикл (DEFINE → PLAN → BUILD → VERIFY → REVIEW → SHIP)

Схема самого пакета `agent-skills` берётся как каркас и накладывается на уже принятую фазовую структуру DentalAi (Часть IV):

| Стадия | Что делать в DentalAi | Скилл/инструмент | Какой паттерн закрывает |
|---|---|---|---|
| **DEFINE** | Перед батчем — короткая спека с критерием приёмки (как `Definition of Done Phase 0` уже сделан для всей фазы, только теперь для каждого батча) | `spec-driven-development`, `interview-me` (если задача расплывчата) | Паттерн 1, 6 |
| **PLAN** | Нарезка батча на атомарные шаги, явная привязка к Zone (R/P/I/T/E) | `planning-and-task-breakdown` | Паттерн 6 |
| **BUILD** | Реализация небольшими слайсами, коммит на каждый | `incremental-implementation`, `git-workflow-and-versioning` | (закрепляет уже работающую практику этой сессии) |
| **VERIFY** | Тест обязан **упасть** на неправильной реализации до того, как пройдёт на правильной; для Zone R/D-категорий — threat model до кода | `test-driven-development`, `security-and-hardening` | Паттерн 2, 3 |
| **REVIEW** | Многоосевой ревью + при высоких ставках — adversarial doubt-цикл **до**, а не после мержа; для будущих Zone E автономных патчей — triad+scope review (Часть VIII.4) | `code-review-and-quality`, `doubt-driven-development` | Паттерн 1 (главный) |
| **SHIP** | CI-гейт (`control-plane-enforcement.yml`) обязателен уже сейчас, не «когда дойдут руки»; чейнджлог и ADR пишутся в момент шипа, не отдельным ретро-коммитом | `ci-cd-and-automation`, `shipping-and-launch`, `documentation-and-adrs` | Паттерн 3, 4 |

### XI.3. Что не нужно строить сейчас

- **MCP-сервер поверх `evolution/ledger.jsonl`/`observations.jsonl`** — рано: сами файлы ещё не существуют (Phase 1+). Строить MCP под несуществующие данные противоречит `incremental-implementation`. Отложено до Phase 2.
- **Кастомный хук `session-start`** — в пакете `agent-skills` он уже есть (`hooks/session-start.sh`, `hooks.json`), но его исполнение зависит от рантайма (Claude Code CLI hooks). Из этой (Cowork, non-interactive) сессии я не могу подтвердить, что hooks вообще исполняются в вашей среде — это стоит проверить в интерактивной Claude Code сессии, прежде чем полагаться на него как на единственный механизм синхронизации.
- **Новый custom-скилл через `/mcp-builder`** — не нашёл ни одного паттерна, требующего интеграции с внешним сервисом (API, БД, SaaS) — все 6 паттернов закрываются уже установленными 24 скиллами. `/mcp-builder` не нужен на этом этапе.

### XI.4. Что сделано в эту сессию

Сохранён скилл `dentalai-dev-cycle` (через `save_skill`, не файл в репозитории — персистентная память Cowork), кодирующий таблицу XI.2 как routing-таблицу для будущих сессий, аналогично `using-agent-skills`, но со ссылками на конкретные Zone/Часть IV DentalAi.

### VIII.4. Ограничения при интеграции (обязательны)

- **Zone-модель не меняется.** LLM Router и все его роли работают **только** внутри Zone E (`backend/app/mcp/orchestration/`, Задача 1.2). Ни одна роль не получает автономного доступа к Zone R/P/I.
- **Не дублировать FastMCP.** Router обязан вызывать существующий `backend/app/mcp/server.py` (Zone R, только для чтения клинических инструментов через штатный протокол), а не создавать параллельную шину вызова функций.
- **Приватность данных пациента.** Контекст, передаваемый в любую роль (включая облачные API), не может содержать данные пациента, сканы, MDR-паспорта — согласно Части IV Phase 4+ ("данные пациентов никогда не попадают в контекст LLM"). `Observer` собирает только UX-телеметрию (клики, тайминги, коды ошибок).
- **Конфигурация роутинга** (`models.yaml` или аналог, hot-swap эндпоинтов) — новый файл, физически будет создан в Zone E/Zone I (инфраструктурный характер: содержит адреса API-эндпоинтов). При реализации — явно классифицировать в `protected_paths.yaml` человеком (по аналогии с п.VII.4), а не полагаться только на fail-safe default.
- **Блокеры Phase 0 действуют и здесь.** `Observer` не может работать на реальных данных, пока заказы в памяти процесса и AuditLog не пишется в БД (Часть I.2) — цикл LLM Router технически бессмыслен до закрытия Phase 0.
