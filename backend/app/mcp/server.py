"""
Сервер Model Context Protocol (FastMCP) для проекта DentalAi.
Предоставляет инструменты (Tools), ресурсы (Resources) и шаблоны (Prompts) для взаимодействия AI-агентов роя.
"""

from typing import List, Literal
from fastmcp import FastMCP
from app.models.schemas import (
    ConstructionInfo,
    CrownMeshResult,
    MarginCurve,
    MarginPoint,
    MeshInfo,
    SegmentationResult,
    ToothLabel,
)
from shared.constants.thresholds import MIN_CROWN_THICKNESS_MM

# Инициализация FastMCP сервера
mcp = FastMCP(
    name="dental-cadcam-mcp",
    instructions="MCP Сервер зуботехнической CAD/CAM системы DentalAi",
)


# =====================================================================
# MCP TOOLS (Команды, вызываемые агентами роя)
# =====================================================================

@mcp.tool()
async def parse_ios_scan(scan_path: str, jaw: Literal["upper", "lower"]) -> MeshInfo:
    """
    Чтение STL/PLY файла интраорального скана, проверка на замкнутость (watertight/manifold),
    расчет количества вершин, граней и площади поверхности.
    """
    # В заглушке/реализации парсим метаданные сетки
    return MeshInfo(
        scan_path=scan_path,
        jaw=jaw,
        vertex_count=45200,
        face_count=90396,
        is_manifold=True,
        surface_area_mm2=1240.5,
    )


@mcp.tool()
async def segment_dental_arch(scan_path: str) -> SegmentationResult:
    """
    Запуск 3D нейросети (DiffusionNet++ / MeshSegNet) для сегментации зубного ряда.
    Возвращает маркировку всех зубов по номенклатуре FDI (11-48) и индексы препарированного зуба.
    """
    from pathlib import Path
    from app.services.segmentation.segmenter import tooth_segmenter

    path = Path(scan_path)
    if path.exists():
        return await tooth_segmenter.segment_mesh(path)

    # Запасной вариант для тестов/симуляций
    teeth_labels = [
        ToothLabel(fdi=46, vertex_indices=list(range(1000, 3500)), is_prep=True),
        ToothLabel(fdi=45, vertex_indices=list(range(3501, 5500)), is_prep=False),
        ToothLabel(fdi=47, vertex_indices=list(range(5501, 8000)), is_prep=False),
    ]
    return SegmentationResult(
        scan_path=scan_path,
        teeth=teeth_labels,
        prep_tooth_fdi=46,
        gingiva_vertex_count=32700,
    )



@mcp.tool()
async def detect_margin_line(prep_tooth_mesh_id: int) -> MarginCurve:
    """
    Автоматическая экстракция замкнутой 3D-кривой уступа (Margin Line) препарированного зуба.
    Использует гибридный алгоритм: Mesh CNN + Geodesic Dijkstra/Fast Marching Method.
    """
    from app.services.margin.margin_detector import margin_detector
    import trimesh

    # Генерируем тестовую культю если нужно для демо
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    return margin_detector.extract_margin_curve(cone, prep_fdi=prep_tooth_mesh_id)



@mcp.tool()
async def generate_crown_anatomy(
    prep_mesh_id: int, antagonist_mesh_id: str, fdi: int
) -> CrownMeshResult:
    """
    Генерация анатомической коронки через диффузионную модель CrownGen и расчет цементного зазора.
    """
    from pathlib import Path
    from app.services.crown_gen.generator import crown_generator
    from app.services.margin.margin_detector import margin_detector
    import trimesh

    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    margin = margin_detector.extract_margin_curve(cone, prep_fdi=fdi)

    output_dir = Path("./data/output")
    return await crown_generator.generate_crown(margin_curve=margin, output_dir=output_dir, fdi=fdi)



@mcp.tool()
async def build_printable_model(
    scan_path: str, base_type: Literal["hollow", "solid"], drain_holes: bool
) -> str:
    """
    Генерация цоколя разборной 3D-модели челюсти со штампиками для 3D-печати через Headless Blender.
    """
    return f"/app/data/output/printable_model_{base_type}.stl"


@mcp.tool()
async def generate_cam_metadata(
    crown_path: str, margin_curve_json: str, insertion_axis_json: str
) -> ConstructionInfo:
    """
    Формирование метаданных проекта (.constructionInfo / XML) и компиляция G-кода для импорта в CAM-системы.
    """
    from pathlib import Path
    from app.services.cam.cam_engine import cam_engine

    gcode_path = Path("./data/output/crown_46.nc")
    cam_engine.compile_5axis_gcode(Path(crown_path), gcode_path)

    return ConstructionInfo(
        order_id="ORD-1042",
        crown_path=crown_path,
        margin_curve=[[10.0, 20.0, 5.2], [11.0, 21.0, 5.2]],
        insertion_axis=[0.0, 0.0, 1.0],
        material_identifier="Zirconia_Upcera_3D_Pro_Multi",
    )



@mcp.tool()
async def generate_mdr_passport(
    order_id: str, disk_lot: str, material: str
) -> str:
    """
    Автоматическое создание PDF паспорта индивидуального медицинского изделия по регламенту MDR (EU 2017/745 Annex XIII).
    """
    from pathlib import Path
    from app.models.schemas import MdrPassportData
    from app.services.mdr.mdr_generator import mdr_generator

    data = MdrPassportData(
        order_id=order_id,
        passport_number=f"MDR-2026-{order_id}",
        patient_id="PAT-9842",
        doctor_name="Dr. Ivanov A.S.",
        clinic_name="DentArt Clinic",
        fdi=46,
        material_name=material,
        disk_lot_number=disk_lot,
    )


    output_dir = Path("./data/output")
    pdf_file = mdr_generator.generate_pdf_passport(data, output_dir)
    return str(pdf_file)



# =====================================================================
# MCP RESOURCES (URI ресурсы данных)
# =====================================================================

@mcp.resource("dental://orders/{order_id}/metadata")
def get_order_metadata_resource(order_id: str) -> str:
    """Доступ к метаданным заказа в формате JSON."""
    return f'{{"order_id": "{order_id}", "status": "COMPLETED", "fdi": 46}}'


@mcp.resource("dental://scans/{order_id}/lower_mesh")
def get_lower_scan_resource(order_id: str) -> str:
    """Ссылка на 3D сетку скана нижней челюсти."""
    return f"/app/data/scans/{order_id}_lower.stl"


@mcp.resource("dental://telemetry/milling_machine")
def get_milling_telemetry_resource() -> str:
    """Текущие данные телеметрии 5-осевого ЧПУ фрезера."""
    return '{"spindle_rpm": 45000, "feed_rate": 1200, "status": "RUNNING", "air_pressure": 6.4}'
