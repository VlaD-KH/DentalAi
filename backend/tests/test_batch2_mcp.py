"""
Модульные тесты для Батча 2: Проверка работы FastMCP сервера, инструментов и ресурсов.
"""

from app.mcp.server import (
    detect_margin_line,
    generate_cam_metadata,
    generate_crown_anatomy,
    generate_mdr_passport,
    get_milling_telemetry_resource,
    get_order_metadata_resource,
    mcp,
    parse_ios_scan,
    segment_dental_arch,
)
import pytest


def test_mcp_server_initialization():
    """Проверяет корректность имя и метаданные FastMCP сервера."""
    assert mcp.name == "dental-cadcam-mcp"


@pytest.mark.asyncio
async def test_mcp_tool_parse_ios_scan():
    """Тестирует MCP инструмент parse_ios_scan."""
    info = await parse_ios_scan(scan_path="/app/data/scans/test.stl", jaw="lower")
    assert info.scan_path == "/app/data/scans/test.stl"
    assert info.jaw == "lower"
    assert info.vertex_count > 0
    assert info.is_manifold is True


@pytest.mark.asyncio
async def test_mcp_tool_segment_arch():
    """Тестирует MCP инструмент segment_dental_arch."""
    result = await segment_dental_arch(scan_path="/app/data/scans/test.stl")
    assert result.prep_tooth_fdi == 46
    assert len(result.teeth) == 3


@pytest.mark.asyncio
async def test_mcp_tool_margin_detection():
    """Тестирует MCP инструмент detect_margin_line."""
    margin = await detect_margin_line(prep_tooth_mesh_id=46)
    assert margin.prep_fdi == 46
    assert len(margin.points) >= 24
    assert margin.accuracy_score >= 0.99



@pytest.mark.asyncio
async def test_mcp_tool_generate_crown():
    """Тестирует MCP инструмент generate_crown_anatomy."""
    crown = await generate_crown_anatomy(prep_mesh_id=46, antagonist_mesh_id="upper_mesh", fdi=46)
    assert "crown_fdi_46.stl" in crown.crown_path
    assert crown.min_thickness_mm >= 0.6
    assert crown.qa_passed is True



@pytest.mark.asyncio
async def test_mcp_tool_generate_mdr():
    """Тестирует MCP инструмент generate_mdr_passport."""
    pdf_path = await generate_mdr_passport(order_id="ORD-1042", disk_lot="LOT-8842", material="Zirconia")
    assert "MDR_Passport_ORD-1042.pdf" in pdf_path


def test_mcp_resources():
    """Тестирует вызов MCP ресурсов."""
    meta = get_order_metadata_resource("ORD-1042")
    assert "ORD-1042" in meta

    telemetry = get_milling_telemetry_resource()
    assert "spindle_rpm" in telemetry
