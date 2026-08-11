"""
Сквозной интеграционный E2E тест полного автономного цикла DentalAi (Fully Autonomous Pipeline).
Проверяет цепочку: STL Скан -> Сегментация -> Уступ -> Анатомия -> QA -> Nesting -> G-Code -> MDR PDF.
"""

from pathlib import Path
from app.models.schemas import AutonomousMode, OrderCreate, OrderStatus
from app.services.cam.cam_engine import cam_engine
from app.services.crown_gen.generator import crown_generator
from app.services.geometry.mesh_processor import geometry_processor
from app.services.margin.margin_detector import margin_detector
from app.services.mdr.mdr_generator import mdr_generator
from app.services.order_service import order_service
from app.services.qa.qa_inspector import qa_inspector
from app.services.segmentation.segmenter import tooth_segmenter
from simulations.scanner_simulator.scan_generator import generate_synthetic_dental_arch
import pytest
import trimesh


@pytest.mark.asyncio
async def test_full_e2e_autonomous_crown_pipeline(tmp_path: Path):
    """
    Выполняет полный автономный конвейер изготовления коронки зуба 46 без участия оператора.
    """
    output_dir = tmp_path / "output"
    scans_dir = tmp_path / "scans"
    output_dir.mkdir()
    scans_dir.mkdir()

    # ШАГ 1: Создание заказа в системе
    from datetime import datetime, timedelta, timezone
    order_data = OrderCreate(
        order_number="#E2E-1042",
        clinic_name="BioDent Szczecin",
        doctor_name="Dr. Anna Kowalska",
        patient_id="PAT-PL-8842",
        target_fdi=46,
        material="Zirconia Upcera 3D Pro Multi",
        color_vita="A2",
        due_date=datetime.now(timezone.utc) + timedelta(days=2),
        mode=AutonomousMode.FULLY_AUTONOMOUS,
    )
    order = await order_service.create_order(order_data)
    assert order.id is not None
    assert order.status == OrderStatus.RECEIVED

    # ШАГ 2: Генерация 3D скана интраоральной челюсти
    scan_file = scans_dir / "lower_arch_46.stl"
    generate_synthetic_dental_arch(scan_file, prep_fdi=46)
    assert scan_file.exists()

    # ШАГ 3: 3D Сегментация зубного ряда
    await order_service.update_status(order.id, OrderStatus.SEGMENTING)
    seg_result = await tooth_segmenter.segment_mesh(scan_file, target_prep_fdi=46)
    assert seg_result.prep_tooth_fdi == 46
    assert len(seg_result.teeth) == 3

    # ШАГ 4: Детекция уступной линии (Margin Line)
    await order_service.update_status(order.id, OrderStatus.MARGIN_EXTRACTING)
    prep_cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    margin = margin_detector.extract_margin_curve(prep_cone, prep_fdi=46)
    assert len(margin.points) == 36
    assert margin.accuracy_score >= 0.99

    # ШАГ 5: Генерация 3D коронки (CrownGen)
    await order_service.update_status(order.id, OrderStatus.CROWN_GENERATING)
    crown_res = await crown_generator.generate_crown(margin, output_dir=output_dir, fdi=46)
    assert Path(crown_res.crown_path).exists()
    assert crown_res.min_thickness_mm >= 0.6

    # ШАГ 6: Геометрическая обработка (чистка + зазор 35мкм)
    crown_mesh = trimesh.load(crown_res.crown_path)
    cleaned_mesh = geometry_processor.clean_mesh(crown_mesh)
    spaced_mesh = geometry_processor.apply_cement_spacer(cleaned_mesh, spacer_mm=0.035)
    spaced_mesh.export(crown_res.crown_path)

    # ШАГ 7: QA Инспекция VLM
    await order_service.update_status(order.id, OrderStatus.QA_REVIEWING)
    qa_res = await qa_inspector.inspect_crown(Path(crown_res.crown_path), margin.insertion_axis)
    assert qa_res["qa_passed"] is True
    assert qa_res["min_thickness_mm"] >= 0.6

    # ШАГ 8: CAM Нестинг в диске 98.5мм и компиляция 5-осевого G-кода ISO 6983
    await order_service.update_status(order.id, OrderStatus.CAM_NESTING)
    nesting_info = cam_engine.nest_crown_in_disk(Path(crown_res.crown_path), disk_lot="LOT-UPCERA-2026-E2E")
    assert nesting_info.scale_factor == 1.22

    gcode_path = output_dir / "crown_46_5axis.nc"
    cam_engine.compile_5axis_gcode(Path(crown_res.crown_path), gcode_path)
    assert gcode_path.exists()
    assert "S45000 M03" in gcode_path.read_text(encoding="utf-8")

    # ШАГ 9: Генерация MDR Паспорта медицинского изделия (EU 2017/745 Annex XIII)
    await order_service.update_status(order.id, OrderStatus.COMPLETED)
    from app.models.schemas import MdrPassportData
    passport_data = MdrPassportData(
        order_id=order.id,
        passport_number=f"MDR-2026-{order.order_number.replace('#', '')}",
        patient_id=order.patient_id,
        doctor_name=order.doctor_name,
        clinic_name=order.clinic_name,
        fdi=46,
        material_name=order.material,
        disk_lot_number=nesting_info.disk_lot_number,
    )
    pdf_passport = mdr_generator.generate_pdf_passport(passport_data, output_dir)
    assert pdf_passport.exists()

    # Финальная валидация состояния заказа
    final_order = await order_service.get_order(order.id)
    assert final_order.status == OrderStatus.COMPLETED
