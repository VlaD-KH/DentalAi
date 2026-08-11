"""
Строго типизированные Pydantic v2 схемы данных для API и MCP инструментов DentalAi.
Все модели включают полную документацию и валидацию согласно bible.md.
"""

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional
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


class BridgeDesignRequest(BaseModel):
    """Запрос на моделирование мостовидного протеза."""
    order_id: str
    abutment_fdis: List[int] = Field(..., min_length=2, description="Номера опорных зубов (например, [45, 47])")
    pontic_fdis: List[int] = Field(..., min_length=1, description="Номера промежуточных коронок/понтиков (например, [46])")
    material: str = Field(default="Zirconia Upcera 3D Pro Multi")


class BridgeDesignResult(BaseModel):
    """Результат моделирования мостовидного протеза."""
    bridge_mesh_path: str
    unit_count: int
    common_insertion_axis: List[float] = Field(default=[0.0, 0.0, 1.0], min_length=3, max_length=3)
    connector_area_mm2: float = Field(..., ge=9.0, description="Измеренная площадь сечения коннекторов (мм²)")
    qa_passed: bool = Field(default=True)
    qa_notes: str


class InlayOnlayType(str, Enum):
    """Типы реставраций полостей."""
    INLAY = "INLAY"
    ONLAY = "ONLAY"
    OVERLAY = "OVERLAY"


class InlayOnlayRequest(BaseModel):
    """Запрос на моделирование вкладки или накладки."""
    order_id: str
    fdi: int
    restoration_type: InlayOnlayType = InlayOnlayType.INLAY
    material: str = Field(default="Zirconia Upcera 3D Pro Multi")


class InlayOnlayResult(BaseModel):
    """Результат моделирования вкладки / накладки."""
    restoration_mesh_path: str
    fdi: int
    restoration_type: InlayOnlayType
    min_cavity_thickness_mm: float = Field(..., ge=0.8)
    qa_passed: bool = Field(default=True)
    qa_notes: str


class VeneerRequest(BaseModel):
    """Запрос на моделирование эстетического винира."""
    order_id: str
    fdi: int
    thickness_mm: float = Field(default=0.4, ge=0.3, le=0.7)
    material: str = Field(default="Lithium Disilicate E.max CAD")


class VeneerResult(BaseModel):
    """Результат моделирования ультратонкого винира."""
    veneer_mesh_path: str
    fdi: int
    measured_thickness_mm: float = Field(..., ge=0.3)
    qa_passed: bool = Field(default=True)
    qa_notes: str


class PmmaCrownRequest(BaseModel):
    """Запрос на изготовление временной коронки из PMMA."""
    order_id: str
    fdi: int
    material: str = Field(default="PMMA Multilayer Temp")


class PmmaCrownResult(BaseModel):
    """Результат расчета CAM фрезерования PMMA."""
    gcode_path: str
    fdi: int
    spindle_rpm: int = Field(default=25000)
    feed_rate_mm_min: float = Field(default=2200.0)
    shrinkage_factor: float = Field(default=1.00)
    qa_passed: bool = Field(default=True)
    qa_notes: str


class CustomAbutmentRequest(BaseModel):
    """Запрос на моделирование индивидуального абатмента на импланте."""
    order_id: str
    fdi: int
    implant_system: str = Field(default="Straumann Bone Level 4.1 Regular CrossFit")
    ti_base_height_mm: float = Field(default=4.0)
    screw_angle_deg: float = Field(default=0.0, ge=0.0, le=25.0)


class CustomAbutmentResult(BaseModel):
    """Результат моделирования индивидуального абатмента."""
    abutment_mesh_path: str
    fdi: int
    implant_system: str
    emergence_profile_valid: bool = Field(default=True)
    screw_channel_angle_deg: float
    qa_passed: bool = Field(default=True)
    qa_notes: str


class PrintableModelRequest(BaseModel):
    """Запрос на подготовку 3D-печатной модели зубной дуги."""
    order_id: str
    scan_path: str
    base_type: Literal["hollow", "solid"] = "hollow"
    drain_holes: bool = True
    geller_dies_fdi: List[int] = Field(default_factory=list)


class PrintableModelResult(BaseModel):
    """Результат подготовки 3D-печатной модели."""
    model_mesh_path: str
    base_type: str
    drain_holes_count: int
    removable_dies_count: int
    qa_passed: bool = Field(default=True)
    qa_notes: str


class SurgicalGuideRequest(BaseModel):
    """Запрос на моделирование навигационного хирургического шаблона."""
    order_id: str
    target_fdis: List[int] = Field(..., min_length=1)
    sleeve_diameter_mm: float = Field(default=5.0)
    sleeve_height_mm: float = Field(default=5.0)


class SurgicalGuideResult(BaseModel):
    """Результат моделирования хирургического шаблона."""
    guide_mesh_path: str
    sleeves_count: int
    inspection_windows_count: int
    qa_passed: bool = Field(default=True)
    qa_notes: str

















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
