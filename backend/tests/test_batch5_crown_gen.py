"""
Модульные тесты для Батча 5: Генерация коронки (CrownGenerator).
"""

from pathlib import Path
from app.services.crown_gen.generator import CrownGenerator
from app.services.margin.margin_detector import MarginDetector
import pytest
import trimesh


@pytest.mark.asyncio
async def test_crown_generation_stl_output(tmp_path: Path):
    """Тестирует генерацию 3D коронки и создание валидного STL файла."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    detector = MarginDetector()
    margin = detector.extract_margin_curve(cone, prep_fdi=46)

    generator = CrownGenerator()
    result = await generator.generate_crown(
        margin_curve=margin,
        output_dir=tmp_path,
        fdi=46,
        target_thickness_mm=0.8,
    )

    assert Path(result.crown_path).exists()
    assert result.min_thickness_mm >= 0.6
    assert result.qa_passed is True

    # Проверяем структуру STL файла коронки
    mesh = trimesh.load(result.crown_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 20
    assert len(mesh.faces) > 20
