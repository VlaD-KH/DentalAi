"""
Модульные тесты для Батча 9: Генератора паспорта медицинского изделия MDR EU 2017/745 (MdrPassportGenerator).
"""

from pathlib import Path
from app.models.schemas import MdrPassportData
from app.services.mdr.mdr_generator import MdrPassportGenerator
import pytest


def test_mdr_pdf_passport_generation(tmp_path: Path):
    """Тестирует генерацию PDF паспорта изделия по регламенту MDR Annex XIII."""
    data = MdrPassportData(
        order_id="ORD-1042",
        passport_number="MDR-2026-1042",
        patient_id="PAT-9842",
        doctor_name="Д-р Петров В.В.",
        clinic_name="BioDent",
        fdi=46,
        material_name="Zirconia Upcera 3D Pro Multi",
        disk_lot_number="LOT-UPCERA-2026-99",
        sintering_temp_c=1530.0,
    )

    generator = MdrPassportGenerator()
    pdf_path = generator.generate_pdf_passport(data, output_dir=tmp_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000  # Валидный непустой PDF файл
    assert pdf_path.name == "MDR_Passport_ORD-1042.pdf"
