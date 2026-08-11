"""
Модульные тесты для Батча 13: Моделирование мостовидных протезов (BridgeGenerator).
"""

from pathlib import Path
from app.models.schemas import BridgeDesignRequest
from app.services.crown_gen.bridge_generator import BridgeGenerator
from app.services.margin.margin_detector import MarginDetector
import pytest
import trimesh


@pytest.mark.asyncio
async def test_bridge_generation_3_units(tmp_path: Path):
    """Тестирует генерацию 3-единичного мостовидного протеза (зубы 45-46-47)."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    detector = MarginDetector()

    margin45 = detector.extract_margin_curve(cone, prep_fdi=45)
    margin47 = detector.extract_margin_curve(cone, prep_fdi=47)

    generator = BridgeGenerator()
    request = BridgeDesignRequest(
        order_id="BRIDGE-100",
        abutment_fdis=[45, 47],
        pontic_fdis=[46],
        material="Zirconia Upcera 3D Pro Multi",
    )

    result = await generator.generate_bridge(request, [margin45, margin47], output_dir=tmp_path)

    assert Path(result.bridge_mesh_path).exists()
    assert result.unit_count == 3
    assert result.connector_area_mm2 >= 9.0
    assert result.qa_passed is True

    # Проверяем структуру сгенерированного монолитного STL файла моста
    mesh = trimesh.load(result.bridge_mesh_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 100
    assert len(mesh.faces) > 100


def test_common_insertion_axis():
    """Тестирует расчёт единого вектора оси посадки для всех опор моста."""
    detector = MarginDetector()
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)

    m1 = detector.extract_margin_curve(cone, prep_fdi=45)
    m2 = detector.extract_margin_curve(cone, prep_fdi=47)

    generator = BridgeGenerator()
    axis = generator.compute_common_insertion_axis([m1, m2])

    assert len(axis) == 3
    assert axis == [0.0, 0.0, 1.0]
