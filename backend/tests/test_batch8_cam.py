"""
Модульные тесты для Батча 8: CAM процессора и генерации 5-осевого G-кода (CamEngine).
"""

from pathlib import Path
from app.services.cam.cam_engine import CamEngine
import pytest


def test_nesting_in_disk():
    """Тестирует параметры раскроя в циркониевом диске."""
    engine = CamEngine()
    result = engine.nest_crown_in_disk(Path("crown.stl"), disk_lot="LOT-2026-TEST", disk_slot=4)

    assert result.disk_lot_number == "LOT-2026-TEST"
    assert result.disk_diameter_mm == 98.5
    assert result.scale_factor == 1.22
    assert result.sprue_count == 2
    assert result.sprue_diameter_mm == 2.5



def test_5axis_gcode_compilation(tmp_path: Path):
    """Тестирует компиляцию 5-осевого G-кода ISO 6983."""
    crown_path = tmp_path / "crown.stl"
    gcode_path = tmp_path / "output_5axis.nc"

    engine = CamEngine()
    res_path = engine.compile_5axis_gcode(crown_path, gcode_path)

    assert res_path.exists()
    assert res_path.stat().st_size > 100

    content = res_path.read_text(encoding="utf-8")
    assert "DENTALAI AUTONOMOUS 5-AXIS CNC G-CODE" in content
    assert "S45000 M03" in content
    assert "G21" in content
    assert "M30" in content
    assert "T1 M06" in content  # Черновая
    assert "T4 M06" in content  # Фиссурная
