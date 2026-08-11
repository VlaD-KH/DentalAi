"""
Модульные тесты для Батча 18: 3D-печатные модели с разборными штампиками (PrintableModelBuilder).
"""

from pathlib import Path
from app.models.schemas import PrintableModelRequest
from app.services.geometry.model_builder import PrintableModelBuilder
import pytest
import trimesh


@pytest.mark.asyncio
async def test_hollow_printable_model_generation(tmp_path: Path):
    """Тестирует генерацию полой модели с дренажными отверстиями и штампиками."""
    builder = PrintableModelBuilder()
    request = PrintableModelRequest(
        order_id="PRINT-46-001",
        scan_path=str(tmp_path / "scan.stl"),
        base_type="hollow",
        drain_holes=True,
        geller_dies_fdi=[46],
    )

    result = await builder.build_printable_model(request, output_dir=tmp_path)

    assert Path(result.model_mesh_path).exists()
    assert result.base_type == "hollow"
    assert result.drain_holes_count == 2
    assert result.removable_dies_count == 1
    assert result.qa_passed is True

    mesh = trimesh.load(result.model_mesh_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 0


@pytest.mark.asyncio
async def test_solid_printable_model_generation(tmp_path: Path):
    """Тестирует генерацию сплошной модели без дренажных отверстий."""
    builder = PrintableModelBuilder()
    request = PrintableModelRequest(
        order_id="PRINT-SOLID-002",
        scan_path=str(tmp_path / "scan.stl"),
        base_type="solid",
        drain_holes=False,
    )

    result = await builder.build_printable_model(request, output_dir=tmp_path)

    assert Path(result.model_mesh_path).exists()
    assert result.base_type == "solid"
    assert result.drain_holes_count == 0
