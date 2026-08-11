"""
Модульные тесты для Батча 14: Моделирование вкладок и накладок (InlayOnlayGenerator).
"""

from pathlib import Path
from app.models.schemas import InlayOnlayRequest, InlayOnlayType
from app.services.crown_gen.inlay_generator import InlayOnlayGenerator
from app.services.margin.margin_detector import MarginDetector
import pytest
import trimesh


@pytest.mark.asyncio
async def test_inlay_generation(tmp_path: Path):
    """Тестирует генерацию вкладки (Inlay) полостей."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    detector = MarginDetector()
    margin = detector.extract_margin_curve(cone, prep_fdi=16)

    generator = InlayOnlayGenerator()
    request = InlayOnlayRequest(
        order_id="INLAY-101",
        fdi=16,
        restoration_type=InlayOnlayType.INLAY,
    )

    result = await generator.generate_inlay_onlay(request, margin, output_dir=tmp_path)

    assert Path(result.restoration_mesh_path).exists()
    assert result.fdi == 16
    assert result.restoration_type == InlayOnlayType.INLAY
    assert result.min_cavity_thickness_mm >= 0.8
    assert result.qa_passed is True

    mesh = trimesh.load(result.restoration_mesh_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 20


@pytest.mark.asyncio
async def test_onlay_generation(tmp_path: Path):
    """Тестирует генерацию накладки (Onlay)."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    detector = MarginDetector()
    margin = detector.extract_margin_curve(cone, prep_fdi=26)

    generator = InlayOnlayGenerator()
    request = InlayOnlayRequest(
        order_id="ONLAY-202",
        fdi=26,
        restoration_type=InlayOnlayType.ONLAY,
    )

    result = await generator.generate_inlay_onlay(request, margin, output_dir=tmp_path)

    assert Path(result.restoration_mesh_path).exists()
    assert result.restoration_type == InlayOnlayType.ONLAY
    assert result.min_cavity_thickness_mm >= 0.8
