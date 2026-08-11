"""
Модульные тесты проверки справочников FDI и пороговых констант.
"""

from shared.constants.fdi import FDI_TOOTH_MAP, ToothCategory, ToothQuadrant, get_tooth_info
from shared.constants.thresholds import (
    CEMENT_SPACER_MICRONS,
    MIN_CROWN_THICKNESS_MM,
    OCCLUSAL_INTERFERENCE_LIMIT_MM,
    ZIRCONIA_DISK_DIAMETER_MM,
)
import pytest


def test_fdi_map_coverage():
    """Проверяет, что справочник FDI покрывает все 32 зуба (11-18, 21-28, 31-38, 41-48)."""
    assert len(FDI_TOOTH_MAP) == 32
    assert 11 in FDI_TOOTH_MAP
    assert 48 in FDI_TOOTH_MAP
    assert 0 not in FDI_TOOTH_MAP  # Метка 0 зарезервирована под десну


def test_tooth_46_info():
    """Проверяет корректность параметров ключевого тестового зуба 46 (первый моляр)."""
    info = get_tooth_info(46)
    assert info["fdi"] == 46
    assert info["quadrant"] == ToothQuadrant.MANDIBULAR_RIGHT
    assert info["category"] == ToothCategory.MOLAR
    assert info["is_upper"] is False
    assert "моляр" in info["name_ru"].lower()


def test_invalid_fdi_raises():
    """Проверяет выброс исключения при недопустимом номере FDI."""
    with pytest.raises(ValueError):
        get_tooth_info(99)


def test_critical_thresholds_values():
    """Проверяет соответствие ключевых пороговых значений спецификации bible.md."""
    assert MIN_CROWN_THICKNESS_MM == 0.6
    assert CEMENT_SPACER_MICRONS == 35.0
    assert OCCLUSAL_INTERFERENCE_LIMIT_MM == -0.05
    assert ZIRCONIA_DISK_DIAMETER_MM == 98.5
