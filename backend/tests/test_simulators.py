"""
Тесты проверки генерации данных симуляторами оборудования и 3D сканера.
"""

from pathlib import Path
from simulations.cnc_simulator.cnc_emulator import CncTelemetry
from simulations.furnace_simulator.furnace_emulator import FurnaceTelemetry
from simulations.scanner_simulator.scan_generator import generate_synthetic_dental_arch
import trimesh


def test_cnc_simulator():
    """Проверяет корректность схемы и параметров симулятора ЧПУ."""
    telemetry = CncTelemetry.get_simulated_status()
    assert telemetry.spindle_rpm >= 40000
    assert telemetry.air_pressure_bar > 6.0
    assert telemetry.status in ["RUNNING", "IDLE", "PAUSED", "ERROR"]


def test_furnace_simulator():
    """Проверяет корректность симулятора печи синтеризации."""
    telemetry = FurnaceTelemetry.get_simulated_status()
    assert telemetry.target_temp_c == 1530.0
    assert telemetry.current_temp_c > 1000.0


def test_synthetic_scan_generation(tmp_path: Path):
    """Проверяет генерацию 3D STL сетки синтетического скана челюсти."""
    stl_path = tmp_path / "test_arch.stl"
    res_path = generate_synthetic_dental_arch(stl_path, prep_fdi=46)

    assert res_path.exists()
    assert res_path.stat().st_size > 0

    # Проверка валидности сгенерированной 3D сетки через trimesh
    mesh = trimesh.load(str(res_path))
    assert isinstance(mesh, trimesh.Trimesh)
    assert len(mesh.vertices) > 100
    assert len(mesh.faces) > 100
