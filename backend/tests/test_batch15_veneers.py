"""
Модульные тесты для Батча 15: Моделирование виниров (VeneerGenerator).
"""

from pathlib import Path
from app.models.schemas import VeneerRequest
from app.services.crown_gen.veneer_generator import VeneerGenerator
from app.services.margin.margin_detector import MarginDetector
import pytest
import trimesh


@pytest.mark.asyncio
async def test_veneer_generation_incisor(tmp_path: Path):
    """Тестирует генерацию ультратонкого винира (0.4 мм) для зуба 11."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    detector = MarginDetector()
    margin = detector.extract_margin_curve(cone, prep_fdi=11)

    generator = VeneerGenerator()
    request = VeneerRequest(
        order_id="VENEER-11-001",
        fdi=11,
        thickness_mm=0.4,
        material="Lithium Disilicate E.max CAD",
    )

    result = await generator.generate_veneer(request, margin, output_dir=tmp_path)

    assert Path(result.veneer_mesh_path).exists()
    assert result.fdi == 11
    assert result.measured_thickness_mm == 0.4
    assert result.qa_passed is True

    mesh = trimesh.load(result.veneer_mesh_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 20
