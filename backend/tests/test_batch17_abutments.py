"""
Модульные тесты для Батча 17: Индивидуальные абатменты (AbutmentGenerator).
"""

from pathlib import Path
from app.models.schemas import CustomAbutmentRequest
from app.services.crown_gen.abutment_generator import AbutmentGenerator
import pytest
import trimesh


@pytest.mark.asyncio
async def test_custom_abutment_generation(tmp_path: Path):
    """Тестирует генерацию индивидуального абатмента с ASC шахтой 15°."""
    generator = AbutmentGenerator()
    request = CustomAbutmentRequest(
        order_id="ABUTMENT-46-001",
        fdi=46,
        implant_system="Straumann Bone Level 4.1 NC",
        ti_base_height_mm=4.0,
        screw_angle_deg=15.0,
    )

    result = await generator.generate_abutment(request, output_dir=tmp_path)

    assert Path(result.abutment_mesh_path).exists()
    assert result.fdi == 46
    assert result.implant_system == "Straumann Bone Level 4.1 NC"
    assert result.screw_channel_angle_deg == 15.0
    assert result.emergence_profile_valid is True
    assert result.qa_passed is True

    mesh = trimesh.load(result.abutment_mesh_path)
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 20
