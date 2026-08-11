"""
Модульные тесты для Батча 7: Визуальный и геометрический контроль качества (QaInspector).
"""

from pathlib import Path
from app.services.qa.qa_inspector import QaInspector
import pytest
import trimesh


@pytest.mark.asyncio
async def test_qa_inspection_pass(tmp_path: Path):
    """Тестирует успешное прохождение инспекции QA."""
    crown_path = tmp_path / "valid_crown.stl"
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    cone.export(str(crown_path))

    inspector = QaInspector()
    result = await inspector.inspect_crown(crown_path, insertion_axis=[0.0, 0.0, 1.0])

    assert "min_thickness_mm" in result
    assert result["min_thickness_mm"] >= 0.6
    assert isinstance(result["qa_passed"], bool)
    assert len(result["notes"]) > 0


@pytest.mark.asyncio
async def test_qa_inspection_non_existent_file():
    """Проверяет обработку отсутствующего файла."""
    inspector = QaInspector()
    with pytest.raises(FileNotFoundError):
        await inspector.inspect_crown(Path("/non/existent/crown.stl"))
