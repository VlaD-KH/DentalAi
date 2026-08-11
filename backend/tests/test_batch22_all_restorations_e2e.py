"""
Сквозные E2E интеграционные тесты для всех расширенных типов реставраций Фазы 2 (Bridges, Inlays, Veneers, PMMA, Abutments, Models, Guides).
"""

from pathlib import Path
from app.models.schemas import (
    BridgeDesignRequest,
    CustomAbutmentRequest,
    InlayOnlayRequest,
    InlayOnlayType,
    PmmaCrownRequest,
    PrintableModelRequest,
    SurgicalGuideRequest,
    VeneerRequest,
)
from app.services.cam.pmma_cam_service import pmma_cam_service
from app.services.crown_gen.abutment_generator import abutment_generator
from app.services.crown_gen.bridge_generator import bridge_generator
from app.services.crown_gen.inlay_generator import inlay_generator
from app.services.crown_gen.veneer_generator import veneer_generator
from app.services.geometry.guide_builder import guide_builder
from app.services.geometry.model_builder import model_builder
from app.services.margin.margin_detector import margin_detector
import pytest
import trimesh


@pytest.mark.asyncio
async def test_e2e_all_restoration_types(tmp_path: Path):
    """
    Сквозное тестирование работы генераторов всех типов стоматологических конструкций.
    """
    output_dir = tmp_path / "output_e2e"
    output_dir.mkdir()

    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    m45 = margin_detector.extract_margin_curve(cone, prep_fdi=45)
    m47 = margin_detector.extract_margin_curve(cone, prep_fdi=47)

    # 1. Мостовидный протез
    req_bridge = BridgeDesignRequest(order_id="E2E-B1", abutment_fdis=[45, 47], pontic_fdis=[46])
    res_bridge = await bridge_generator.generate_bridge(req_bridge, [m45, m47], output_dir)
    assert Path(res_bridge.bridge_mesh_path).exists()

    # 2. Вкладка Inlay
    req_inlay = InlayOnlayRequest(order_id="E2E-I1", fdi=16, restoration_type=InlayOnlayType.INLAY)
    res_inlay = await inlay_generator.generate_inlay_onlay(req_inlay, m45, output_dir)
    assert Path(res_inlay.restoration_mesh_path).exists()

    # 3. Винир Veneer
    req_veneer = VeneerRequest(order_id="E2E-V1", fdi=11, thickness_mm=0.4)
    res_veneer = await veneer_generator.generate_veneer(req_veneer, m45, output_dir)
    assert Path(res_veneer.veneer_mesh_path).exists()

    # 4. Временная коронка PMMA
    req_pmma = PmmaCrownRequest(order_id="E2E-P1", fdi=46)
    res_pmma = pmma_cam_service.compile_pmma_gcode(req_pmma, output_dir)
    assert Path(res_pmma.gcode_path).exists()

    # 5. Индивидуальный абатмент
    req_abut = CustomAbutmentRequest(order_id="E2E-A1", fdi=46, implant_system="Straumann BL", screw_angle_deg=10.0)
    res_abut = await abutment_generator.generate_abutment(req_abut, output_dir)
    assert Path(res_abut.abutment_mesh_path).exists()

    # 6. 3D-печатная модель
    req_model = PrintableModelRequest(order_id="E2E-M1", scan_path="scan.stl", base_type="hollow", geller_dies_fdi=[46])
    res_model = await model_builder.build_printable_model(req_model, output_dir)
    assert Path(res_model.model_mesh_path).exists()

    # 7. Хирургический шаблон
    req_guide = SurgicalGuideRequest(order_id="E2E-G1", target_fdis=[46, 47])
    res_guide = await guide_builder.build_surgical_guide(req_guide, output_dir)
    assert Path(res_guide.guide_mesh_path).exists()
