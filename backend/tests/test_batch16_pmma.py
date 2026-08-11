"""
Модульные тесты для Батча 16: Фрезерование временных коронок из PMMA (PmmaCamService).
"""

from pathlib import Path
from app.models.schemas import PmmaCrownRequest
from app.services.cam.pmma_cam_service import PmmaCamService
import pytest


def test_pmma_gcode_compilation(tmp_path: Path):
    """Тестирует компиляцию 5-осевого G-кода для фрезерования PMMA."""
    service = PmmaCamService()
    request = PmmaCrownRequest(order_id="PMMA-46-TEST", fdi=46, material="PMMA Multilayer Temp")

    result = service.compile_pmma_gcode(request, output_dir=tmp_path)

    assert Path(result.gcode_path).exists()
    assert result.fdi == 46
    assert result.spindle_rpm == 25000
    assert result.feed_rate_mm_min == 2200.0
    assert result.shrinkage_factor == 1.00
    assert result.qa_passed is True

    gcode_text = Path(result.gcode_path).read_text(encoding="utf-8")
    assert "S25000 M03" in gcode_text
    assert "F2200.0" in gcode_text
