"""
Модульные тесты для Батча 10: Автоматический прием заказов (OrderIngestion & REST API).
"""

from pathlib import Path
from app.main import app
from app.services.ingestion.watcher import OrderIngestionService
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)


@pytest.mark.asyncio
async def test_hot_folder_file_ingestion(tmp_path: Path):
    """Тестирует автоматическое создание заказа при появлении файла в Hot-Folder."""
    scan_file = tmp_path / "scan_patient_99.stl"
    scan_file.write_bytes(b"solid synthetic_stl_content endsolid")

    service = OrderIngestionService()
    result = await service.process_hot_folder_file(scan_file)

    assert result is not None
    assert result["status"] == "INGESTED_SUCCESS"
    assert "SCAN_PATIENT_99" in result["order_number"]



def test_rest_api_create_and_list_orders():
    """Тестирует REST API ручки POST /api/orders и GET /api/orders."""
    payload = {
        "order_number": "#TEST-REST-100",
        "clinic_name": "API Test Clinic",
        "doctor_name": "Dr. REST",
        "patient_id": "PAT-REST",
        "target_fdi": 46,
        "material": "Zirconia Upcera",
        "color_vita": "A2",
        "due_date": "2026-08-15T12:00:00Z",
        "mode": "FULLY_AUTONOMOUS",
    }

    # 1. Создание
    response = client.post("/api/orders", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == "#TEST-REST-100"
    assert data["id"] is not None

    # 2. Получение списка
    list_resp = client.get("/api/orders")
    assert list_resp.status_code == 200
    orders = list_resp.json()
    assert len(orders) > 0


def test_rest_api_upload_scan():
    """Тестирует загрузку файла 3D скана через REST API."""
    files = {"file": ("test_mesh.stl", b"synthetic 3d stl bytes", "application/octet-stream")}
    response = client.post("/api/orders/upload-scan", files=files)

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "UPLOADED_SUCCESS"
    assert res_data["filename"] == "test_mesh.stl"
