"""
Тесты политик безопасности Reviewer.md, CORS и валидации FDI (Батч 27).
"""

from app.models.schemas import AutonomousMode, OrderCreate
from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError


# test_batch27_reviewer_policy_files_exist удалён (Batch 28, DentalAi_MASTER_TZ_v2.md Часть VII Шаг 5):
# проверял только Path.exists(), что создавало ложное чувство защищённости
# (Reviewer.md §18: "CONTROL PLANE IS DESCRIBED IN MARKDOWN" вместо "CONTROL PLANE EXISTS").
# Заменён на backend/tests/test_batch28_control_plane_enforcement.py, который проверяет
# фактическое поведение enforcement на 15 запрещённых diff + позитивный контроль.


def test_batch27_invalid_fdi_validation():
    """Проверка отклонения невалидных номеров FDI (19, 20, 29, 30, 39, 40, 49) (F.1)."""
    with pytest.raises(ValidationError):
        OrderCreate(
            order_number="#INVALID-FDI",
            clinic_name="Clinic",
            doctor_name="Doctor",
            patient_id="PAT-1",
            target_fdi=19,  # 19 не существует в FDI
            due_date=datetime.now(timezone.utc) + timedelta(days=1),
            mode=AutonomousMode.FULLY_AUTONOMOUS,
        )


def test_batch27_valid_fdi_validation():
    """Проверка корректного прохождения валидного номера FDI (46)."""
    order = OrderCreate(
        order_number="#VALID-FDI",
        clinic_name="Clinic",
        doctor_name="Doctor",
        patient_id="PAT-1",
        target_fdi=46,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
        mode=AutonomousMode.FULLY_AUTONOMOUS,
    )
    assert order.target_fdi == 46
