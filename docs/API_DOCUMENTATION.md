# DentalAi — Спецификация REST API & FastMCP Tools

## 🌐 FastMCP Tools (Протокол взаимодействия ИИ-агентов)

- `segment_dental_arch(scan_mesh_id, target_prep_fdi)` — 3D Сегментация челюсти.
- `detect_margin_line(prep_tooth_mesh_id, fdi)` — Детекция B-сплайна уступа и оси посадки.
- `generate_crown_anatomy(prep_mesh_id, antagonist_mesh_id, fdi)` — Диффузионная генерация анатомии коронки.
- `generate_bridge_restoration(order_id, abutment_fdis, pontic_fdis)` — Моделирование мостовидного протеза.
- `generate_inlay_onlay(order_id, fdi, restoration_type)` — Моделирование вкладки / накладки.
- `generate_veneer(order_id, fdi, thickness_mm)` — Моделирование ультратонкого винира.
- `generate_pmma_temporary(order_id, fdi)` — Расчет фрезерования PMMA (25000 RPM).
- `generate_custom_abutment(order_id, fdi, implant_system, screw_angle)` — Индивидуальный абатмент.
- `build_printable_model(scan_path, base_type, drain_holes)` — 3D-печатная модель с дренажными отверстиями.
- `generate_surgical_guide(order_id, target_fdis, sleeve_diameter_mm)` — Хирургический шаблон.
- `generate_mdr_passport(order_id, disk_lot, material)` — Паспорт ЕС MDR 2017/745 (Annex XIII).

## 📡 REST API (FastAPI)

- `POST /api/orders` — Создание заказа.
- `GET /api/orders` — Список заказов.
- `GET /api/orders/{order_id}` — Получение заказа по ID.
- `POST /api/orders/upload-scan` — Загрузка 3D файлов STL, PLY, OBJ.
