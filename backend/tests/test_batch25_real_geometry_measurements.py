"""
Тесты реальных геометрических замеров и динамического выделения зубов (Батч 25 / Audit B.1 - B.6).
"""

from pathlib import Path
from app.models.schemas import BridgeDesignRequest
from app.services.crown_gen.bridge_generator import bridge_generator
from app.services.margin.margin_detector import margin_detector
from app.services.qa.qa_inspector import qa_inspector
from app.services.segmentation.segmenter import tooth_segmenter
import pytest
import trimesh


@pytest.mark.asyncio
async def test_batch25_deterministic_qa_inspector(tmp_path: Path):
    """Проверка детерминированного замера толщины в qa_inspector (B.1 & F.3)."""
    crown_file = tmp_path / "test_crown.stl"
    mesh = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    mesh.export(str(crown_file))

    res1 = await qa_inspector.inspect_crown(crown_file)
    res2 = await qa_inspector.inspect_crown(crown_file)

    assert res1["min_thickness_mm"] == res2["min_thickness_mm"]
    assert res1["qa_passed"] is True


@pytest.mark.asyncio
async def test_batch25_dynamic_connector_area(tmp_path: Path):
    """Проверка динамического расчета сечения коннекторов моста (B.3)."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    m45 = margin_detector.extract_margin_curve(cone, prep_fdi=45)
    m47 = margin_detector.extract_margin_curve(cone, prep_fdi=47)

    req = BridgeDesignRequest(order_id="TEST-B3", abutment_fdis=[45, 47], pontic_fdis=[46])
    res = await bridge_generator.generate_bridge(req, [m45, m47], tmp_path)

    assert res.connector_area_mm2 >= 9.0


@pytest.mark.asyncio
async def test_batch25_dynamic_target_fdi_segmentation(tmp_path: Path):
    """Проверка динамической маркировки FDI при сегментации (B.6)."""
    scan_file = tmp_path / "scan_arch.stl"
    arch = trimesh.creation.icosphere(subdivisions=2, radius=10.0)
    arch.export(str(scan_file))

    res = await tooth_segmenter.segment_mesh(scan_file, target_prep_fdi=26)
    assert res.prep_tooth_fdi == 26
    prep_label = [t for t in res.teeth if t.is_prep][0]
    assert prep_label.fdi == 26
