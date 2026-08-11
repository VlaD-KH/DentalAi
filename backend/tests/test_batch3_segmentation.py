"""
Модульные тесты для Батча 3: Проверка 3D-сегментации зубных рядов (ToothSegmenter).
"""

from pathlib import Path
from app.services.segmentation.segmenter import ToothSegmenter
from simulations.scanner_simulator.scan_generator import generate_synthetic_dental_arch
import pytest


@pytest.mark.asyncio
async def test_tooth_segmentation_on_synthetic_scan(tmp_path: Path):
    """Тестирует полный цикл 3D сегментации синтетического скана челюсти."""
    scan_file = tmp_path / "synthetic_arch.stl"
    generate_synthetic_dental_arch(scan_file, prep_fdi=46)

    segmenter = ToothSegmenter()
    result = await segmenter.segment_mesh(scan_file, target_prep_fdi=46)

    assert result.scan_path == str(scan_file)
    assert result.prep_tooth_fdi == 46
    assert len(result.teeth) == 3
    assert result.gingiva_vertex_count > 0

    # Проверяем, что препарированный зуб 46 корректно отмечен
    prep_tooth = next(t for t in result.teeth if t.fdi == 46)
    assert prep_tooth.is_prep is True
    assert len(prep_tooth.vertex_indices) > 0


@pytest.mark.asyncio
async def test_segmenter_non_existent_file():
    """Проверяет обработку ошибки при отсутствии 3D файла."""
    segmenter = ToothSegmenter()
    with pytest.raises(FileNotFoundError):
        await segmenter.segment_mesh(Path("/non/existent/path.stl"))
