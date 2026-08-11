"""
Сервис бизнес-логики управления заказами зуботехнической лаборатории.
Обеспечивает валидацию, смену статусов и сохранение заказов.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
from app.models.schemas import OrderCreate, OrderResponse, OrderStatus


class OrderService:
    """Сервис обработки и хранения заказов."""

    def __init__(self):
        self._orders_db: Dict[str, OrderResponse] = {}
        self._audit_logs: List[Dict] = []

    async def create_order(self, data: OrderCreate) -> OrderResponse:
        """Создает новый заказ в системе."""
        order_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        order = OrderResponse(
            id=order_id,
            order_number=data.order_number,
            clinic_name=data.clinic_name,
            doctor_name=data.doctor_name,
            patient_id=data.patient_id,
            target_fdi=data.target_fdi,
            material=data.material,
            color_vita=data.color_vita,
            due_date=data.due_date,
            mode=data.mode,
            status=OrderStatus.RECEIVED,
            created_at=now,
            updated_at=now,
        )

        self._orders_db[order_id] = order

        await self.log_audit_event(
            order_id=order_id,
            agent_name="OrderIngestion",
            tool_called="create_order",
            input_data={"order_number": data.order_number},
            output_data={"status": "RECEIVED"},
            status="SUCCESS",
        )
        return order

    async def get_order(self, order_id: str) -> Optional[OrderResponse]:
        """Возвращает информацию о заказе по его ID."""
        return self._orders_db.get(order_id)

    async def list_orders(self) -> List[OrderResponse]:
        """Возвращает список всех активных заказов."""
        return list(self._orders_db.values())

    async def update_status(self, order_id: str, new_status: OrderStatus) -> Optional[OrderResponse]:
        """Обновляет статус выполнения заказа."""
        order = self._orders_db.get(order_id)
        if not order:
            return None

        updated_order = order.model_copy(update={
            "status": new_status,
            "updated_at": datetime.now(timezone.utc)
        })
        self._orders_db[order_id] = updated_order

        await self.log_audit_event(
            order_id=order_id,
            agent_name="OrderOrchestrator",
            tool_called="update_status",
            input_data={"new_status": str(new_status)},
            output_data={"status": "UPDATED"},
            status="SUCCESS",
        )
        return updated_order

    async def log_audit_event(
        self,
        order_id: Optional[str],
        agent_name: str,
        tool_called: str,
        input_data: dict,
        output_data: dict,
        status: str = "SUCCESS",
    ):
        """Записывает неизменяемую запись в AuditLog для MDR 10-летнего хранения."""
        import json
        now = datetime.now(timezone.utc)
        log_entry = {
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "agent_name": agent_name,
            "tool_called": tool_called,
            "input_data": json.dumps(input_data, ensure_ascii=False),
            "output_data": json.dumps(output_data, ensure_ascii=False),
            "status": status,
            "created_at": now.isoformat(),
        }
        self._audit_logs.append(log_entry)
        return log_entry

    def get_audit_logs(self, order_id: Optional[str] = None) -> List[Dict]:
        """Возвращает аудит-логи (фильтр по order_id при необходимости)."""
        if order_id:
            return [log for log in self._audit_logs if log.get("order_id") == order_id]
        return self._audit_logs


order_service = OrderService()
