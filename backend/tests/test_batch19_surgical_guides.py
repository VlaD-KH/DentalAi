"""
Модульные тесты для Батча 19: Хирургические шаблоны (SurgicalGuideBuilder).
"""

from pathlib import Path
from app.models.schemas import SurgicalGuideRequest
from app.services.geometry.guide_builder import SurgicalGuideBuilder
import pytest
import trimesh


@pytest.mark.asyncio
async def test_surgical_guide_generation(tmp_path: Path):
    """Тестирует генерацию навигационного хирургического шаблона."""
    builder = SurgicalGuideBuilder()
    request = SurgicalGuideRequest(
        order_id="GUIDE-46-47-001",
        target_fdis=[46, 47],
        sleeve_diameter_mm=5.0,
        sleeve_height_mm=5.0,
    )

    result = await builder.build_surgical_guide(request, output_dir=tmp_path)

    assert Path(result.guide_mesh_path).exists()
    assert result.sleeves_count == 2
    assert result.inspection_windows_count == 2
    assert result.qa_passed is True

    mesh = trimesh.load(result.guide_mesh_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 20
