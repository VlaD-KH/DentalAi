"""
Модульные тесты для Батча 1: Проверка Pydantic v2 схем, валидации толщины и сервиса заказов.
"""

from datetime import datetime, timedelta, timezone
from app.models.schemas import (
    AutonomousMode,
    CrownMeshResult,
    MarginCurve,
    MarginPoint,
    OrderCreate,
    OrderStatus,
)
from app.services.order_service import OrderService
import pytest


@pytest.mark.asyncio
async def test_order_creation_and_status_update():
    """Тестирует создание заказа и изменение его статуса в OrderService."""
    service = OrderService()

    due = datetime.now(timezone.utc) + timedelta(days=2)
    new_order = OrderCreate(
        order_number="#1042",
        clinic_name="DentArt",
        doctor_name="Д-р Петров В.В.",
        patient_id="PAT-1042",
        target_fdi=46,
        material="Zirconia Upcera 3D Pro Multi",
        color_vita="A2",
        due_date=due,
        mode=AutonomousMode.FULLY_AUTONOMOUS,
    )

    created = await service.create_order(new_order)
    assert created.id is not None
    assert created.status == OrderStatus.RECEIVED
    assert created.target_fdi == 46

    # Обновление статуса
    updated = await service.update_status(created.id, OrderStatus.SEGMENTING)
    assert updated is not None
    assert updated.status == OrderStatus.SEGMENTING


def test_crown_thickness_validation_pass():
    """Проверяет прохождение валидации, если толщина коронки >= 0.6мм."""
    result = CrownMeshResult(
        crown_path="/app/data/output/crown_46.stl",
        min_thickness_mm=0.72,  # Допустимая толщина
        cement_spacer_microns=35.0,
        marginal_offset_mm=0.8,
        qa_passed=True,
    )
    assert result.min_thickness_mm == 0.72
    assert result.qa_passed is True


def test_crown_thickness_validation_fail():
    """Проверяет выброс исключения валидации, если толщина < 0.6мм (порог брака из bible.md)."""
    with pytest.raises(ValueError) as exc_info:
        CrownMeshResult(
            crown_path="/app/data/output/crown_46.stl",
            min_thickness_mm=0.45,  # НЕДОПУСТИМАЯ толщина (меньше 0.6мм)
            cement_spacer_microns=35.0,
            marginal_offset_mm=0.8,
            qa_passed=False,
        )
    assert "меньше критического минимума 0.6мм" in str(exc_info.value)


def test_margin_curve_schema():
    """Проверяет корректность генерации и валидации кривой уступа (MarginCurve)."""
    points = [MarginPoint(x=float(i), y=float(i * 2), z=5.0) for i in range(12)]
    curve = MarginCurve(
        prep_fdi=46,
        points=points,
        insertion_axis=[0.0, 0.0, 1.0],
        accuracy_score=0.99,
    )
    assert curve.prep_fdi == 46
    assert len(curve.points) == 12
    assert curve.accuracy_score == 0.99
