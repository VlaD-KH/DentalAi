"""
Сервис автоматического приема заказов (Order Ingestion Service).
Мониторит Hot-Folder на диск, обрабатывает электронную почту и принимает веб-загрузки.
"""

from pathlib import Path
from typing import Dict, Optional
from app.models.schemas import AutonomousMode, OrderCreate
from app.services.order_service import order_service
import asyncio


class OrderIngestionService:
    """Сервис шлюза поступления заказов."""

    async def process_hot_folder_file(self, file_path: Path) -> Optional[Dict]:
        """
        Обрабатывает новый STL/PLY файл, поступивший в Hot-Folder.
        Автоматически создаёт заказ в OrderService.
        """
        if not file_path.exists() or file_path.suffix.lower() not in [".stl", ".ply", ".obj"]:
            return None

        # Формируем авто-метаданные заказа по имени файла
        order_number = f"#{file_path.stem.upper()}"
        from datetime import datetime, timedelta, timezone

        new_order_data = OrderCreate(
            order_number=order_number,
            clinic_name="HotFolder Auto-Ingest",
            doctor_name="Dr. AutoIngest",
            patient_id=f"PAT-{file_path.stem}",
            target_fdi=46,
            material="Zirconia Upcera 3D Pro Multi",
            color_vita="A2",
            due_date=datetime.now(timezone.utc) + timedelta(days=2),
            mode=AutonomousMode.FULLY_AUTONOMOUS,
        )

        order = await order_service.create_order(new_order_data)

        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "scan_path": str(file_path),
            "status": "INGESTED_SUCCESS",
        }


ingestion_service = OrderIngestionService()
