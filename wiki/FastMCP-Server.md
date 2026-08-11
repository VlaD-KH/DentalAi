# 📡 Архитектура FastMCP-Сервера ИИ-Агентов

В DentalAi взаимодействие между ИИ-моделями (Gemini, Claude, локальные PyTorch сетки) и аппаратным / геометрическим обеспечением реализовано на базе протокола **Model Context Protocol (MCP)** через фреймворк **FastMCP**.

## 🛠️ Спецификация MCP Инструментов (Tools):

| Название инструмента | Назначение | Параметры |
|---|---|---|
| `segment_dental_arch` | 3D Сегментация челюсти, отделение десны от коронок | `scan_mesh_id: int`, `target_prep_fdi: int` |
| `detect_margin_line` | Построение сплайна края препарирования и оси посадки | `prep_tooth_mesh_id: int`, `fdi: int` |
| `generate_crown_anatomy` | Диффузионная генерация анатомической формы коронки | `prep_mesh_id: int`, `antagonist_mesh_id: str`, `fdi: int` |
| `generate_bridge_restoration` | Моделирование мостов с расчетом общей оси посадки | `order_id: str`, `abutment_fdis: List[int]`, `pontic_fdis: List[int]` |
| `generate_inlay_onlay` | Моделирование вкладок Inlay/Onlay/Overlay | `order_id: str`, `fdi: int`, `restoration_type: str` |
| `generate_veneer` | Моделирование виниров толщиной 0.3-0.5мм | `order_id: str`, `fdi: int`, `thickness_mm: float` |
| `generate_pmma_temporary` | Расчет CAM фрезерования временных коронок PMMA | `order_id: str`, `fdi: int` |
| `generate_custom_abutment` | Моделирование абатмента с угловой шахтой ASC | `order_id: str`, `fdi: int`, `implant_system: str`, `screw_angle: float` |
| `build_printable_model` | Подготовка печатных моделей с пинами Geller | `scan_path: str`, `base_type: str`, `drain_holes: bool` |
| `generate_surgical_guide` | Моделирование хирургических навигационных шаблонов | `order_id: str`, `target_fdis: List[int]`, `sleeve_diameter_mm: float` |
| `generate_mdr_passport` | Создание PDF паспорта соответствия MDR Annex XIII | `order_id: str`, `disk_lot: str`, `material: str` |

## 📦 MCP Ресурсы (Resources):

Сервер предоставляет доступ к текущим 3D сеткам и документам через URI-схему `dental://`:
- `dental://scans/{id}` — Файлы интраорального сканирования.
- `dental://crowns/{id}` — Сгенерированные 3D файлы коронок.
- `dental://passports/{id}` — PDF паспорта медицинских изделий.
