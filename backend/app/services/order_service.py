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
        return updated_order


order_service = OrderService()
