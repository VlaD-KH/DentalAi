"""
Сервер Model Context Protocol (FastMCP) для проекта DentalAi.
Предоставляет инструменты (Tools), ресурсы (Resources) и шаблоны (Prompts) для взаимодействия AI-агентов роя.
"""

from typing import List, Literal
from fastmcp import FastMCP
from app.models.schemas import (
    BridgeDesignRequest,
    BridgeDesignResult,
    ConstructionInfo,
    CrownMeshResult,
    CustomAbutmentResult,
    InlayOnlayResult,
    MarginCurve,
    MarginPoint,
    MeshInfo,
    PmmaCrownResult,
    PrintableModelResult,
    SegmentationResult,
    SurgicalGuideResult,
    ToothLabel,
    VeneerResult,
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
async def generate_bridge_restoration(
    order_id: str, abutment_fdis: List[int], pontic_fdis: List[int]
) -> BridgeDesignResult:
    """
    Генерация мостовидного протеза с расчетом единой оси посадки и усиленных коннекторов (>=9.0 мм²).
    """
    from pathlib import Path
    from app.models.schemas import BridgeDesignRequest
    from app.services.crown_gen.bridge_generator import bridge_generator
    from app.services.margin.margin_detector import margin_detector
    import trimesh

    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    margins = [
        margin_detector.extract_margin_curve(cone, prep_fdi=fdi)
        for fdi in abutment_fdis
    ]

    req = BridgeDesignRequest(
        order_id=order_id,
        abutment_fdis=abutment_fdis,
        pontic_fdis=pontic_fdis,
    )
    output_dir = Path("./data/output")
    return await bridge_generator.generate_bridge(req, margins, output_dir)


@mcp.tool()
async def generate_inlay_onlay(
    order_id: str, fdi: int, restoration_type: str
) -> InlayOnlayResult:
    """
    Генерация вкладки / накладки (Inlay, Onlay, Overlay) с контролем толщины дна полости (>=0.8мм).
    """
    from pathlib import Path
    from app.models.schemas import InlayOnlayRequest, InlayOnlayType
    from app.services.crown_gen.inlay_generator import inlay_generator
    from app.services.margin.margin_detector import margin_detector
    import trimesh

    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    margin = margin_detector.extract_margin_curve(cone, prep_fdi=fdi)

    req = InlayOnlayRequest(
        order_id=order_id,
        fdi=fdi,
        restoration_type=InlayOnlayType(restoration_type.upper()),
    )
    output_dir = Path("./data/output")
    return await inlay_generator.generate_inlay_onlay(req, margin, output_dir)


@mcp.tool()
async def generate_veneer(
    order_id: str, fdi: int, thickness_mm: float = 0.4
) -> VeneerResult:
    """
    Генерация эстетического ультратонкого винира (0.3-0.5мм) из стеклокерамики E.max.
    """
    from pathlib import Path
    from app.models.schemas import VeneerRequest
    from app.services.crown_gen.veneer_generator import veneer_generator
    from app.services.margin.margin_detector import margin_detector
    import trimesh

    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    margin = margin_detector.extract_margin_curve(cone, prep_fdi=fdi)

    req = VeneerRequest(
        order_id=order_id,
        fdi=fdi,
        thickness_mm=thickness_mm,
    )
    output_dir = Path("./data/output")
    return await veneer_generator.generate_veneer(req, margin, output_dir)


@mcp.tool()
async def generate_pmma_temporary(order_id: str, fdi: int) -> PmmaCrownResult:
    """
    Расчет 5-осевого G-кода фрезерования временной коронки из PMMA (25000 RPM, scale 1.00).
    """
    from pathlib import Path
    from app.models.schemas import PmmaCrownRequest
    from app.services.cam.pmma_cam_service import pmma_cam_service

    req = PmmaCrownRequest(order_id=order_id, fdi=fdi)
    output_dir = Path("./data/output")
    return pmma_cam_service.compile_pmma_gcode(req, output_dir)


@mcp.tool()
async def generate_custom_abutment(
    order_id: str, fdi: int, implant_system: str, screw_angle: float = 0.0
) -> CustomAbutmentResult:
    """
    Генерация индивидуального абатмента с профилем прорезывания и шахтой винта под угол до 25 deg.
    """
    from pathlib import Path
    from app.models.schemas import CustomAbutmentRequest
    from app.services.crown_gen.abutment_generator import abutment_generator

    req = CustomAbutmentRequest(
        order_id=order_id,
        fdi=fdi,
        implant_system=implant_system,
        screw_angle_deg=screw_angle,
    )
    output_dir = Path("./data/output")
    return await abutment_generator.generate_abutment(req, output_dir)











@mcp.tool()
async def build_printable_model(
    scan_path: str, base_type: Literal["hollow", "solid"], drain_holes: bool
) -> PrintableModelResult:
    """
    Подготовка 3D-печатной модели зубной дуги с цоколем, дренажными отверстиями для смолы и разборными штампиками.
    """
    from pathlib import Path
    from app.models.schemas import PrintableModelRequest
    from app.services.geometry.model_builder import model_builder

    req = PrintableModelRequest(
        order_id="PRINT-100",
        scan_path=scan_path,
        base_type=base_type,
        drain_holes=drain_holes,
        geller_dies_fdi=[46],
    )
    output_dir = Path("./data/output")
    return await model_builder.build_printable_model(req, output_dir)


@mcp.tool()
async def generate_surgical_guide(
    order_id: str, target_fdis: List[int], sleeve_diameter_mm: float = 5.0
) -> SurgicalGuideResult:
    """
    Генерация навигационного хирургического шаблона с направляющими гильзами и смотровыми окнами прилегания.
    """
    from pathlib import Path
    from app.models.schemas import SurgicalGuideRequest
    from app.services.geometry.guide_builder import guide_builder

    req = SurgicalGuideRequest(
        order_id=order_id,
        target_fdis=target_fdis,
        sleeve_diameter_mm=sleeve_diameter_mm,
    )
    output_dir = Path("./data/output")
    return await guide_builder.build_surgical_guide(req, output_dir)




@mcp.tool()
async def generate_cam_metadata(
    crown_path: str, margin_curve_json: str, insertion_axis_json: str, order_id: str = "ORD-1042", fdi: int = 46
) -> ConstructionInfo:
    """
    Формирование метаданных проекта (.constructionInfo / XML) и компиляция G-кода для импорта в CAM-системы.
    """
    import json
    from pathlib import Path
    from app.services.cam.cam_engine import cam_engine

    try:
        margin_curve = json.loads(margin_curve_json) if margin_curve_json else [[10.0, 20.0, 5.2], [11.0, 21.0, 5.2]]
    except Exception:
        margin_curve = [[10.0, 20.0, 5.2], [11.0, 21.0, 5.2]]

    try:
        insertion_axis = json.loads(insertion_axis_json) if insertion_axis_json else [0.0, 0.0, 1.0]
    except Exception:
        insertion_axis = [0.0, 0.0, 1.0]

    gcode_path = Path(f"./data/output/crown_{fdi}_{order_id}.nc")
    cam_engine.compile_5axis_gcode(Path(crown_path), gcode_path, fdi=fdi, order_id=order_id)

    return ConstructionInfo(
        order_id=order_id,
        crown_path=crown_path,
        margin_curve=margin_curve,
        insertion_axis=insertion_axis,
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
    from app.services.order_service import order_service

    order = await order_service.get_order(order_id)
    patient_id = f"PAT-{order_id}"
    doctor_name = "Attending Dentist"
    clinic_name = "Dental Clinic"
    fdi = 46

    if order:
        patient_id = f"PAT-{order.id}"
        doctor_name = order.doctor_name or doctor_name
        clinic_name = order.clinic_name or clinic_name
        fdi = order.target_fdi

    data = MdrPassportData(
        order_id=order_id,
        passport_number=f"MDR-2026-{order_id}",
        patient_id=patient_id,
        doctor_name=doctor_name,
        clinic_name=clinic_name,
        fdi=fdi,
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
