"""
Тесты неизменяемого аудит-лога MDR и персистентности (Батч 26 / Audit B.8, C.1 - C.3).
"""

from datetime import datetime, timedelta, timezone
from app.models.schemas import AutonomousMode, OrderCreate, OrderStatus
from app.services.order_service import order_service
import pytest


@pytest.mark.asyncio
async def test_batch26_audit_log_entry_creation():
    """Проверка записи в AuditLog при создании и смене статусов заказа (B.8)."""
    new_order = OrderCreate(
        order_number="#AUDIT-LOG-TEST",
        clinic_name="Audit Clinic",
        doctor_name="Dr. Audit",
        patient_id="PAT-AUDIT-1",
        target_fdi=11,
        due_date=datetime.now(timezone.utc) + timedelta(days=1),
        mode=AutonomousMode.FULLY_AUTONOMOUS,
    )
    created = await order_service.create_order(new_order)
    assert created.id is not None

    logs = order_service.get_audit_logs(created.id)
    assert len(logs) >= 1
    assert logs[0]["agent_name"] == "OrderIngestion"
    assert logs[0]["tool_called"] == "create_order"

    updated = await order_service.update_status(created.id, OrderStatus.CAM_NESTING)
    assert updated.status == OrderStatus.CAM_NESTING

    updated_logs = order_service.get_audit_logs(created.id)
    assert len(updated_logs) >= 2
    assert updated_logs[1]["tool_called"] == "update_status"
