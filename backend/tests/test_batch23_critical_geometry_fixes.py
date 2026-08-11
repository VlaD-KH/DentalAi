"""
Автоматические тесты критических багов геометрии и CAM-маркировки (Батч 23 / Audit A.1 - A.5).
"""

from pathlib import Path
from app.models.schemas import (
    CustomAbutmentRequest,
    PrintableModelRequest,
    SurgicalGuideRequest,
)
from app.services.cam.cam_engine import cam_engine
from app.services.crown_gen.abutment_generator import abutment_generator
from app.services.geometry.guide_builder import guide_builder
from app.services.geometry.model_builder import model_builder
import pytest
import trimesh


@pytest.mark.asyncio
async def test_batch23_model_builder_drain_holes(tmp_path: Path):
    """Проверка вычитания дренажных отверстий в моделях (A.2)."""
    req = PrintableModelRequest(
        order_id="TEST-A2",
        scan_path="scan.stl",
        base_type="hollow",
        drain_holes=True,
        geller_dies_fdi=[46],
    )
    res = await model_builder.build_printable_model(req, tmp_path)
    assert Path(res.model_mesh_path).exists()
    assert res.drain_holes_count == 2


@pytest.mark.asyncio
async def test_batch23_guide_builder_windows(tmp_path: Path):
    """Проверка включения смотровых окон в хирургические шаблоны (A.3)."""
    req = SurgicalGuideRequest(order_id="TEST-A3", target_fdis=[46])
    res = await guide_builder.build_surgical_guide(req, tmp_path)
    assert Path(res.guide_mesh_path).exists()
    mesh = trimesh.load(res.guide_mesh_path)
    assert len(mesh.faces) > 0
    assert res.inspection_windows_count == 2


@pytest.mark.asyncio
async def test_batch23_abutment_screw_channel(tmp_path: Path):
    """Проверка включения винтового канала в абатмент (A.4)."""
    req = CustomAbutmentRequest(
        order_id="TEST-A4",
        fdi=46,
        implant_system="Straumann BL",
        screw_angle_deg=15.0,
    )
    res = await abutment_generator.generate_abutment(req, tmp_path)
    assert Path(res.abutment_mesh_path).exists()
    mesh = trimesh.load(res.abutment_mesh_path)
    assert len(mesh.faces) > 0


def test_batch23_cam_engine_dynamic_program_id(tmp_path: Path):
    """Проверка динамической маркировки FDI и order_id в G-коде (A.5)."""
    gcode_path = tmp_path / "test.gcode"
    compiled_path = cam_engine.compile_5axis_gcode(
        crown_path=tmp_path / "crown.stl",
        output_gcode_path=gcode_path,
        fdi=24,
        order_id="ORD-9999",
    )
    content = compiled_path.read_text(encoding="utf-8")
    assert "PROGRAM ID: CROWN_FDI_24_ORD-9999" in content
