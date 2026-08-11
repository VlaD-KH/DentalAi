"""
FastAPI роутер управления заказами и приемки файлов сканирования (REST API).
"""

from pathlib import Path
from typing import List
from app.config import settings
from app.models.schemas import OrderCreate, OrderResponse
from app.services.order_service import order_service
from fastapi import APIRouter, HTTPException, UploadFile, File

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse)
async def create_new_order(order_data: OrderCreate):
    """Создание нового заказа из дашборда."""
    return await order_service.create_order(order_data)


@router.get("", response_model=List[OrderResponse])
async def list_all_orders():
    """Получение списка всех заказов."""
    return await order_service.list_orders()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: str):
    """Получение заказа по его ID."""
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return order


@router.post("/upload-scan")
async def upload_scan_file(file: UploadFile = File(...)):
    """Загрузка STL/PLY файла интраорального скана."""
    if not file.filename.endswith((".stl", ".ply", ".obj")):
        raise HTTPException(status_code=400, detail="Поддерживаются только 3D файлы STL, PLY, OBJ")

    save_path = settings.SCANS_DIR / file.filename
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "saved_path": str(save_path),
        "size_bytes": len(content),
        "status": "UPLOADED_SUCCESS",
    }
