"""
Тесты исправления передачи параметров в MCP и сервиса приёма файлов Hot-Folder (Батч 24 / Audit A.6 - A.9).
"""

import json
from pathlib import Path
from app.mcp.server import generate_cam_metadata, generate_mdr_passport
from app.models.schemas import AutonomousMode, OrderCreate
from app.services.ingestion.watcher import ingestion_service
from app.services.order_service import order_service
import pytest


@pytest.mark.asyncio
async def test_batch24_mcp_cam_metadata_custom_params():
    """Проверка передачи реальных margin_curve_json и insertion_axis_json в generate_cam_metadata (A.6)."""
    custom_margin = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    custom_axis = [0.0, 0.707, 0.707]
    res = await generate_cam_metadata(
        crown_path="crown.stl",
        margin_curve_json=json.dumps(custom_margin),
        insertion_axis_json=json.dumps(custom_axis),
        order_id="ORD-TEST-A6",
        fdi=16,
    )
    assert res.order_id == "ORD-TEST-A6"
    assert res.margin_curve == custom_margin
    assert res.insertion_axis == custom_axis


@pytest.mark.asyncio
async def test_batch24_mcp_mdr_passport_dynamic_data():
    """Проверка извлечения данных существующего заказа в generate_mdr_passport (A.7)."""
    from datetime import datetime, timedelta, timezone
    new_order = OrderCreate(
        order_number="#ORD-DYNAMIC-A7",
        clinic_name="Stomatologia Szczecin",
        doctor_name="Dr. Kowalski",
        patient_id="PAT-PL-777",
        target_fdi=46,
        material="Zirconia KATANA YML",
        color_vita="A3",
        due_date=datetime.now(timezone.utc) + timedelta(days=2),
        mode=AutonomousMode.FULLY_AUTONOMOUS,
    )
    created = await order_service.create_order(new_order)

    pdf_str = await generate_mdr_passport(
        order_id=created.id,
        disk_lot="LOT-KATANA-2026",
        material="Zirconia KATANA YML",
    )
    assert Path(pdf_str).exists()


@pytest.mark.asyncio
async def test_batch24_ingestion_service_hot_folder(tmp_path: Path):
    """Проверка фонового приёма файлов из Hot-Folder (A.9)."""
    stl_file = tmp_path / "scan_patient_123.stl"
    stl_file.write_bytes(b"solid dummy stl header binary data test content")

    res = await ingestion_service.process_hot_folder_file(stl_file)
    assert res is not None
    assert res["status"] == "INGESTED_SUCCESS"
    assert res["order_number"] == "#SCAN_PATIENT_123"
