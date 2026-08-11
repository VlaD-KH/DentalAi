"""
Строго типизированные Pydantic v2 схемы данных для API и MCP инструментов DentalAi.
Все модели включают полную документацию и валидацию согласно bible.md.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from shared.constants.thresholds import MIN_CROWN_THICKNESS_MM


class OrderStatus(str, Enum):
    """Статусы жизненного цикла заказа."""
    RECEIVED = "RECEIVED"
    SEGMENTING = "SEGMENTING"
    MARGIN_EXTRACTING = "MARGIN_EXTRACTING"
    CROWN_GENERATING = "CROWN_GENERATING"
    QA_REVIEWING = "QA_REVIEWING"
    CAM_NESTING = "CAM_NESTING"
    GCODE_READY = "GCODE_READY"
    MILLING = "MILLING"
    SINTERING = "SINTERING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class AutonomousMode(str, Enum):
    """Режимы автономности."""
    FULLY_AUTONOMOUS = "FULLY_AUTONOMOUS"
    SUPERVISED = "SUPERVISED"


class OrderCreate(BaseModel):
    """Схема создания нового заказа."""
    order_number: str = Field(..., json_schema_extra={"example": "#1042"}, description="Уникальный номер заказа")
    clinic_name: str = Field(..., json_schema_extra={"example": "DentArt"}, description="Название клиники")
    doctor_name: str = Field(..., json_schema_extra={"example": "Д-р Иванов А.С."}, description="ФИО врача")
    patient_id: str = Field(..., json_schema_extra={"example": "PAT-9842"}, description="Идентификатор или ФИО пациента")
    target_fdi: int = Field(..., ge=11, le=48, description="Номер зуба по номенклатуре FDI (11-48)")
    material: str = Field(default="Zirconia Upcera 3D Pro Multi", description="Материал реставрации")
    color_vita: str = Field(default="A2", description="Цвет по шкале VITA")
    due_date: datetime = Field(..., description="Срок сдачи работы")
    mode: AutonomousMode = Field(default=AutonomousMode.FULLY_AUTONOMOUS, description="Режим выполнения")


class OrderResponse(OrderCreate):
    """Схема ответа с полной информацией о заказе."""
    id: str
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class MeshInfo(BaseModel):
    """Результат парсинга 3D сетки интраорального скана."""
    scan_path: str
    jaw: str  # "upper" | "lower"
    vertex_count: int = Field(..., ge=3, description="Количество вершин")
    face_count: int = Field(..., ge=1, description="Количество полигонов")
    is_manifold: bool = Field(..., description="Замкнутость сетки (watertight)")
    surface_area_mm2: float = Field(..., ge=0.0, description="Площадь поверхности в мм²")


class ToothLabel(BaseModel):
    """Маркировка отдельного зуба в результате сегментации."""
    fdi: int = Field(..., ge=0, le=48)
    vertex_indices: List[int] = Field(..., description="Индексы вершин в исходном скане")
    is_prep: bool = Field(default=False, description="Признак препарированного зуба")


class SegmentationResult(BaseModel):
    """Результат полной сегментации зубного ряда (MeshSegNet / DiffusionNet++)."""
    scan_path: str
    teeth: List[ToothLabel]
    prep_tooth_fdi: Optional[int] = None
    gingiva_vertex_count: int = 0


class MarginPoint(BaseModel):
    """Точка уступной линии (Margin Line) в 3D пространстве."""
    x: float
    y: float
    z: float


class MarginCurve(BaseModel):
    """Замкнутая 3D кривая границы препарирования (уступа)."""
    prep_fdi: int
    points: List[MarginPoint] = Field(..., min_length=10, description="Точки замкнутого сплайна")
    insertion_axis: List[float] = Field(default=[0.0, 0.0, 1.0], min_length=3, max_length=3)
    accuracy_score: float = Field(default=0.99, ge=0.0, le=1.0)


class CrownMeshResult(BaseModel):
    """Результат генерации и инспекции коронки."""
    crown_path: str
    min_thickness_mm: float = Field(..., description="Измеренная минимальная толщина стенки")
    cement_spacer_microns: float = Field(default=35.0)
    marginal_offset_mm: float = Field(default=0.8)
    qa_passed: bool = Field(default=False)
    qa_notes: Optional[str] = None

    @field_validator("min_thickness_mm")
    def validate_thickness(cls, v):
        if v < MIN_CROWN_THICKNESS_MM:
            raise ValueError(f"Толщина стенки коронки {v}мм меньше критического минимума {MIN_CROWN_THICKNESS_MM}мм!")
        return v


class ConstructionInfo(BaseModel):
    """Метаданные проекции для импорта в CAM-системы (.constructionInfo)."""
    order_id: str
    crown_path: str
    margin_curve: List[List[float]]
    insertion_axis: List[float]
    material_identifier: str


class CamNestingData(BaseModel):
    """Данные раскроя коронки в заготовке диска."""
    disk_lot_number: str
    disk_diameter_mm: float = 98.5
    disk_slot: int = 4
    scale_factor: float = 1.22
    sprue_count: int = 2
    sprue_diameter_mm: float = 2.5
    sprue_margin_safety_offset_mm: float = 1.0
    status: str = "NESTED_SUCCESS"



class MdrPassportData(BaseModel):
    """Данные для паспорта медицинского изделия MDR EU 2017/745."""
    order_id: str
    passport_number: str
    patient_id: str
    doctor_name: str
    clinic_name: str
    fdi: int
    material_name: str
    disk_lot_number: str
    sintering_temp_c: float = 1530.0
    declaration_text: str = "Данное медицинское изделие изготовлено исключительно по индивидуальному заказу."
