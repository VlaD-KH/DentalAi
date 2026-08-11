# 🦷 DentalAi — Аудит кодовой базы (для доработки агентами)

> Дата аудита: 2026-08-11
> Формат: чек-лист задач по категориям, отсортирован по критичности внутри каждой категории.
> Каждый пункт содержит: файл → проблему → рекомендацию. Готово для скармливания в Antigravity 2.0 / Claude Code как backlog задач ("Батч N+1").

## 📊 Сводка

| Категория | Кол-во проблем | Критичность |
|---|---:|---|
| A. Критические баги (ломают функциональность) | 9 | 🔴 |
| B. Фейковые/заглушечные данные (риск для MDR) | 8 | 🔴 |
| C. Архитектурные расхождения с bible.md | 9 | 🟠 |
| D. Безопасность | 5 | 🟠 |
| E. Frontend-баги | 7 | 🟡 |
| F. Backend логические баги | 6 | 🟡 |
| G. Инфраструктура / Docker / Deploy | 6 | 🟡 |
| H. Тесты | 4 | 🟢 |
| I. Документация / несоответствия | 5 | 🟢 |
| J. Мелкие недоработки | 6 | 🟢 |

---

## A. 🔴 Критические баги (ломают функциональность)

1. **`frontend/components/AgentSwarmLogger.tsx`** — в интерфейсе `LogEntry` поле объявлено как `action: str;` — `str` не является типом TypeScript (это Python-тип). Приведёт к ошибке компиляции `next build`. **Исправить на `action: string;`**.

2. **`backend/app/services/geometry/model_builder.py`** — `hole1`/`hole2` (дренажные отверстия Ø3мм) создаются, но никогда не вычитаются из `base_box` через boolean-операцию (`trimesh.boolean.difference`). Модель экспортируется без реальных отверстий, хотя `drain_holes_count=2` возвращается как будто отверстия есть — **несоответствие данных и геометрии**.

3. **`backend/app/services/geometry/guide_builder.py`** — переменная `win` (смотровое окно) создаётся в цикле, но никогда не добавляется в `guide_parts` — окна контроля прилегания не попадают в итоговый STL, хотя `inspection_windows_count=2` возвращается.

4. **`backend/app/services/crown_gen/abutment_generator.py`** — `screw_channel` (винтовой канал с углом ASC) создаётся и трансформируется, но не включается в `trimesh.util.concatenate([ti_base, emergence])`. Ключевая деталь абатмента (винтовой канал) отсутствует в готовой модели.

5. **`backend/app/services/cam/cam_engine.py::compile_5axis_gcode`** — сигнатура метода не принимает `fdi`/`order_id`, поэтому в каждом G-коде жёстко прописано `PROGRAM ID: CROWN_FDI_46`, независимо от реального заказа/зуба. При производстве других зубов (11–45, 47, 48…) в файле G-кода будет неверная маркировка — **критично для прослеживаемости MDR**.

6. **`backend/app/mcp/server.py::generate_cam_metadata`** — параметры `margin_curve_json` и `insertion_axis_json` принимаются в сигнатуре, но полностью игнорируются: возвращается хардкод `margin_curve=[[10.0, 20.0, 5.2], [11.0, 21.0, 5.2]]`, `order_id="ORD-1042"`. Реальные данные, переданные агентом, теряются.

7. **`backend/app/mcp/server.py::generate_mdr_passport`** — `patient_id="PAT-9842"`, `doctor_name="Dr. Ivanov A.S."`, `clinic_name="DentArt Clinic"` — жёстко прописаны и не берутся из реального заказа по `order_id`. Любой сгенерированный MDR-паспорт будет содержать одинаковые (фейковые) данные пациента независимо от заказа — **прямое нарушение MDR Annex XIII (идентификация конкретного пациента/изделия)**.

8. **`backend/app/main.py`** — `ConnectionManager.broadcast_log()` определён, но нигде не вызывается. Живой поток логов агентов через `/ws/logs`, заявленный в архитектуре и на дашборде — **не реализован / мёртвый код**.

9. **`backend/app/services/ingestion/watcher.py`** — `OrderIngestionService.process_hot_folder_file()` не подключён ни к какому планировщику/`watchdog.Observer` в `main.py`, несмотря на то, что `watchdog` есть в зависимостях, а `USER_GUIDE.md` заявляет автоматический приём файлов из `data/orders/hot_folder/`. Функция вызывается только вручную/в тестах.

---

## B. 🔴 Фейковые/заглушечные данные (риск для соответствия MDR EU 2017/745)

1. **`backend/app/services/qa/qa_inspector.py`** — `measured_min_thickness` вычисляется через `np.random.randn()` (случайное число!), а не через реальный анализ геометрии сетки. QA-инспекция толщины стенки — **ключевой критерий безопасности изделия** (bible.md §4.1) — фактически ничего не измеряет.

2. **`backend/app/services/crown_gen/generator.py`** — `measured_min_thickness = max(target_thickness_mm, MIN_CROWN_THICKNESS_MM + 0.15)` — формула, а не замер по mesh. Толщина стенки коронки не рассчитывается из реальной геометрии.

3. **`backend/app/services/crown_gen/bridge_generator.py`** — `measured_connector_area = 10.17` — захардкожено, не вычисляется из фактического сечения `conn1`/`conn2`.

4. **`backend/app/services/crown_gen/inlay_generator.py`** — `measured_thickness = 0.95` — захардкожено, не связано с реальной геометрией полости.

5. **`backend/app/mcp/server.py`** — `generate_crown_anatomy`, `generate_bridge_restoration`, `generate_inlay_onlay`, `generate_veneer` — во всех инструментах вместо реального меша культи (переданного `prep_mesh_id`) используется один и тот же хардкод `trimesh.creation.cone(radius=4.5, height=7.0, sections=36)`. Входные идентификаторы мешей фактически игнорируются во всех генеративных MCP-инструментах.

6. **`backend/app/services/segmentation/segmenter.py`** и **fallback в `mcp/server.py::segment_dental_arch`** — сегментация всегда возвращает ровно 3 зуба (46/45/47) независимо от `target_prep_fdi`; реального сопоставления с запрошенным номером зуба нет.

7. **Отсутствует реализация Headless Blender / AI-моделей**, заявленных в bible.md (§2.3, §3.1) и в _deepresearch_-документах: нет `app/services/blender/`, нет `bpy`-скриптов, нет интеграции DiffusionNet++/MeshSegNet/CrownGen/VLM. Вся "AI-генерация" — геометрические заглушки на trimesh (`convex_hull`, примитивы).

8. **`backend/app/db/schema.prisma::AuditLog`** — таблица неизменяемого аудит-лога агентов (обязательна по bible.md для 10-летнего хранения MDR-документации) **никогда не заполняется** ни одним сервисом — нет ни одной записи `AuditLog.create(...)` в коде.

---

## C. 🟠 Архитектурные расхождения с bible.md / deepresearch

1. **Нет персистентности заказов**: `backend/app/services/order_service.py` хранит заказы в `self._orders_db: Dict[...]` **в памяти процесса**. При перезапуске backend все заказы теряются — притом что развёрнуты PostgreSQL + Prisma-схема, которые нигде не используются.
2. **Prisma-клиент нигде не импортируется/не вызывается** в приложении (`prisma generate` выполняется в Dockerfile, но `from prisma import ...` отсутствует по всему `backend/app`). Схема `db/schema.prisma` — фактически мёртвый артефакт.
3. **`DiskInventory`** (склад циркониевых дисков) определён в Prisma-схеме, но не используется — данные "Склад дисков: 12 шт." на дашборде захардкожены в JSX.
4. Директории, заявленные в структуре bible.md (`app/mcp/tools/`, `app/mcp/resources/`, `app/mcp/prompts/`, `app/services/blender/`), **отсутствуют** — весь MCP-функционал свален в один `app/mcp/server.py`.
5. `backend/app/agents/__init__.py` — пустой, реальных определений агентов (Orchestrator/CAD Specialist/QA/CAM) как модулей Python не существует, хотя роль каждого агента подробно описана в bible.md §3.3.
6. i18n: в bible.md заявлен `next-intl` (RU/EN/PL), в `frontend/package.json` **нет зависимости `next-intl`**; `frontend/messages/{ru,en,pl}.json` не импортируются нигде в коде — переключатель языка в `page.tsx` — чисто визуальный, не переключает контент.
7. Дашборд (`frontend/app/page.tsx`) не делает ни одного вызова к REST API (`/api/orders`) или WebSocket (`/ws/logs`) — все заказы, статусы, телеметрия — статичная вёрстка, не связанная с backend.
8. `backend/pyproject.toml` содержит неиспользуемые тяжёлые зависимости: `open3d`, `celery` — нигде не импортируются в текущем коде (нет ни одного `import open3d`/`import celery`).
9. `CamEngine.compile_5axis_gcode` не использует константы `ZIRCONIA_SHRINKAGE_FACTOR_MIN/MAX` из `shared/constants/thresholds.py` — коэффициент усадки `1.22` захардкожен и в `cam_engine.py`, и в `nest_crown_in_disk`, а не выводится/валидируется через диапазон 1.20–1.25.

---

## D. 🟠 Безопасность

1. **`backend/app/main.py`** — `CORSMiddleware(allow_origins=["*"], allow_credentials=True)` — недопустимая комбинация: браузеры блокируют credentialed-запросы при wildcard origin. Указать конкретные origins.
2. **`backend/app/config.py`** — дефолтные креды БД захардкожены в исходном коде (`dental_user:dental_secret_pass`), и такие же значения продублированы в `docker-compose.yml`. Даже как дефолт для dev — плохая практика, нет `.env.example` с инструкцией их сменить.
3. **Нет аутентификации/авторизации** ни на REST API (`orders_router.py`), ни на MCP-сервере, ни на WebSocket `/ws/logs` — при этом система обрабатывает персональные медицинские данные пациентов (MDR-контекст).
4. `docker-compose.yml` пробрасывает порты БД и Redis наружу (`5432:5432`, `6379:6379`) без необходимости для frontend/backend, увеличивая поверхность атаки в проде.
5. Загрузка файлов (`orders_router.py::upload_scan_file`) не валидирует размер файла и не проверяет реальное содержимое (magic bytes) — только расширение `.stl/.ply/.obj` по имени — возможность загрузки произвольного контента под нужным расширением.

---

## E. 🟡 Frontend-баги

1. `AgentSwarmLogger.tsx` — `action: str` (см. A.1) — блокирует сборку.
2. `Viewport3D.tsx` — надпись `"3D VIEW HettiRent"` — похоже на опечатку/мусорный текст (осталось от промпт-инъекции/автогенерации). Проверить и заменить на осмысленный лейбл.
3. `Viewport3D.tsx` — 3D-сцена рендерит статичный конус/цилиндр с фиксированными параметрами, не подключена ни к какому реальному mesh/API — по факту декоративная заглушка.
4. `TelemetryDock.tsx` — SVG-дуги (`strokeDasharray="85, 100"`, `"90, 100"`, `"100, 100"`) захардкожены и не связаны с реальными числовыми значениями рядом (45 000 RPM, 1380/1530°C, 100 Bar) — при изменении данных визуализация не обновится.
5. `frontend/app/page.tsx` — переключатель `autonomousMode` и `activeLang` — чисто локальный `useState`, ничего не персистит и не влияет на backend/бэкенд-режим.
6. Дублирование `index.html` в корне репозитория и `docs/index.html` — идентичный контент, риск рассинхронизации при правках одного без другого.
7. `frontend/package.json` — отсутствует `next-intl`, при этом заявлен как часть стека в bible.md (см. C.6) — либо добавить зависимость и подключить, либо убрать i18n-файлы как orphaned.

---

## F. 🟡 Backend логические баги

1. `shared/constants/fdi.py` + `backend/app/models/schemas.py` — валидация `target_fdi`/`fdi` только через `ge=11, le=48` (или `ge=0, le=48` для `ToothLabel`), но не проверяется принадлежность номера реальному множеству FDI (например, `19`, `20`, `29`, `30`, `39`, `40`, `49` и т.п. — невалидные номера — проходят валидацию Pydantic). Нужно валидировать через `FDI_TOOTH_MAP`/`get_tooth_info`.
2. `backend/app/services/mdr/mdr_generator.py` — модель `MdrPassportData` не содержит полей `zirconiaLot`, `stainingLot`, `signedBy`, которые обязательны в Prisma-модели `MdrPassport` — рассинхронизация схем при (будущей) интеграции с БД.
3. `qa_inspector.py::inspect_crown` — недетерминированный результат (`np.random.randn()` без seed) — при повторном запуске одного и того же e2e-теста результат может отличаться; для медицинского ПО тесты должны быть детерминированы.
4. `backend/app/services/order_service.py` — синглтон `order_service` — общее состояние между тестами (см. H.1) и между запросами без какой-либо блокировки/потокобезопасности (не критично для asyncio, но стоит документировать).
5. `backend/app/mcp/server.py::generate_pmma_temporary` вызывает `pmma_cam_service.compile_pmma_gcode`, но по всей кодовой базе не проверяется валидность угла/материала перед фрезеровкой PMMA (нет валидации, хотя допуски заданы в bible.md).
6. `mesh_processor.py::apply_cement_spacer` — комментарий содержит слипшийся текст `"Смещаем только внутренние вершинывыше краевой зоны"` (опечатка, нет пробела) — не критично, но указывает на неаккуратность при генерации кода.

---

## G. 🟡 Инфраструктура / Docker / Deploy

1. `backend/Dockerfile` — устанавливает полный пакет `blender` через apt в `python:3.11-slim`, при этом **в коде нет ни одного `import bpy`** — зависимость мертвым грузом раздувает образ (сотни МБ) без пользы.
2. `backend/Dockerfile` — `RUN python -m prisma generate || true` — ошибки генерации Prisma-клиента молча проглатываются (`|| true`), что может скрыть реальную проблему сборки.
3. `frontend/Dockerfile` — `CMD ["npm", "run", "dev"]` — используется **dev-сервер Next.js в docker-compose**, а не `npm run build && npm run start` — не production-ready конфигурация.
4. `docker-compose.yml` — нет `healthcheck` для `backend`/`frontend` сервисов (только для `db`/`redis`), что усложняет orchestration/restart-policy.
5. `scripts/deploy_local.ps1` — предполагает наличие `backend/tests/` доступных из хостовой директории через `python -m pytest backend/tests/`, но не проверяет наличие Python-окружения/зависимостей на хосте перед запуском (только Docker проверяется).
6. Нет `.env.example` — новому агенту/разработчику негде посмотреть перечень требуемых переменных окружения без чтения `config.py`.

---

## H. 🟢 Тесты

1. `backend/tests/test_batch10_ingestion.py::test_rest_api_create_and_list_orders` использует глобальный `order_service`, разделяемый со всеми остальными тестами (нет фикстуры для очистки `_orders_db` между тестами) — потенциальная нестабильность порядка выполнения тестов.
2. `test_batch2_mcp.py::test_mcp_tool_margin_detection` — ассерт `len(margin.points) >= 24`, при этом `detect_margin_line` всегда возвращает ровно 36 точек (фиксированный `num_sample_points` от cone) — тест слабый, не проверяет граничные случаи.
3. Тесты, зависящие от `qa_inspector.inspect_crown` (например, `test_batch12_e2e_pipeline.py`), недетерминированы из-за `np.random` без seed — см. F.3.
4. Нет тестов на негативные сценарии для MCP-инструментов, которые сейчас игнорируют входные параметры (B.5, A.6, A.7) — то есть баги подмены хардкод-данных не покрыты тестами и не будут отловлены при регрессии.

---

## I. 🟢 Документация / несоответствия

1. `wiki/FastMCP-Server.md`, `docs/API_DOCUMENTATION.md`, `docs/index.html` — упоминают "14 Tools Registered", но фактически в `backend/app/mcp/server.py` зарегистрировано 11 `@mcp.tool()` — расхождение числа инструментов в документации и коде.
2. `docs/index.html` и корневой `index.html` — полностью дублируют друг друга (см. E.6) — обновлять нужно синхронно вручную.
3. `bible.md` §0 указывает дату создания `2026-08-11`, совпадающую с "текущей датой" аудита — стоит подтвердить, что это не путаница дат в шаблоне документа.
4. `docs/USER_GUIDE.md` заявляет автономный приём заказов из hot-folder, что не реализовано (см. A.9) — документация опережает код.
5. `wiki/CAD-CAM-Engine.md` описывает подробный алгоритм детекции уступа через "Mesh CNN + Geodesic Dijkstra/FMM" — реальный `margin_detector.py` использует простую эвристику (сортировка вершин по Z-уровню и азимутальному углу), без CNN/Dijkstra — документация не соответствует реализации.

---

## J. 🟢 Мелкие недоработки

1. `backend/app/mcp/server.py` — большие блоки пустых строк (следы удалённого кода) между секциями инструментов — стоит почистить перед код-ревью.
2. `backend/app/models/schemas.py` — большой блок пустых строк перед `MdrPassportData` — аналогично, следы удалённого кода/незакоммиченных правок.
3. `AgentSwarmLogger.tsx` — кнопки "Quick Intervention Controls" (`Подправить границу`, `Добавить 0.1 мм окклюзии`, `Перенести в CAM`) не имеют `onClick`-обработчиков — чисто декоративные.
4. `frontend/components/TelemetryDock.tsx` — иконки/цвета не имеют доступных aria-label — минимальная accessibility-доработка.
5. `PmmaCamService.compile_pmma_gcode` — использует f-string с русским текстом внутри `qa_notes`, но сам G-код — латиница/ISO, что нормально, но стоит унифицировать язык логов согласно правилу bible.md §7.1 (комментарии — русский, код — английский; в целом соблюдается, но `qa_notes` местами смешивает регистр терминов).
6. Нет `CHANGELOG.md` / версионирования релизов, несмотря на `VERSION: str = "0.1.0"` в `config.py` — нет процесса обновления версии.

---

## ✅ Рекомендуемый порядок работ для агентов

1. **Батч исправления критических багов (A)** — включая TS-ошибку, boolean-операции геометрии, игнорируемые параметры MCP-инструментов.
2. **Батч устранения фейковых данных (B)** — подключить реальный расчёт толщины стенки (raycasting/nearest-surface distance вместо random), связать MCP-инструменты с реальными сохранёнными мешами по `mesh_id`/`order_id`.
3. **Батч персистентности (C.1–C.3)** — перевести `order_service` на Prisma + PostgreSQL, реализовать запись `AuditLog`.
4. **Батч безопасности (D)** — CORS, auth (JWT/OAuth), убрать хардкод-креды в `.env.example`.
5. **Батч Frontend↔Backend интеграции (E, C.7)** — подключить `page.tsx` к REST API и WebSocket, оживить `AgentSwarmLogger` через реальные логи.
6. **Батч чистки инфраструктуры (G)** — убрать неиспользуемые зависимости (`blender` apt, `open3d`, `celery`), production Dockerfile для frontend.
7. **Батч документации (I)** — синхронизировать `wiki/*`, `docs/*` с фактическим количеством инструментов и реализованными алгоритмами.
