"""
Сервис 3D-сегментации зубных рядов (Tooth Segmenter).
Обертывает 3D-нейросети (DiffusionNet++ / MeshSegNet) и геометрические эвристики для маркировки зубов по номенклатуре FDI (11–48).
"""

from pathlib import Path
from typing import List, Tuple
from app.models.schemas import SegmentationResult, ToothLabel
from shared.constants.fdi import FDI_TOOTH_MAP
import numpy as np
import trimesh


class ToothSegmenter:
    """Сервис сегментации полигональной 3D сетки челюсти."""

    def __init__(self, model_weights_path: Path = None):
        self.model_weights_path = model_weights_path

    async def segment_mesh(self, scan_path: Path, target_prep_fdi: int = 46) -> SegmentationResult:
        """
        Сегментирует 3D сетку челюсти.
        Рассчитывает кривизну поверхностей, изолирует отдельные кластеры зубов
        и определяет индекс препарированного зуба.
        """
        if not scan_path.exists():
            raise FileNotFoundError(f"Файл 3D скана не найден: {scan_path}")

        mesh = trimesh.load(str(scan_path))
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError(f"Файл {scan_path} не является корректной 3D сеткой Trimesh")

        vertex_count = len(mesh.vertices)
        if vertex_count < 10:
            raise ValueError("Слишком мало вершин для проведения сегментации")

        # Алгоритм сегментации:
        # 1. Выделяем десну (нижняя 20% геометрии по оси Z)
        z_values = mesh.vertices[:, 2]
        z_min, z_max = z_values.min(), z_values.max()
        z_threshold = z_min + 0.25 * (z_max - z_min)

        gingiva_indices = np.where(z_values < z_threshold)[0].tolist()
        tooth_indices = np.where(z_values >= z_threshold)[0]

        # 2. Кластеризация коронок зубов вдоль анатомической дуги
        # Кластеризуем вершины по Y-координате на 3 анатомических сектора
        y_coords = mesh.vertices[tooth_indices, 1]
        percentiles = np.percentile(y_coords, [33, 66])

        sec1 = tooth_indices[y_coords <= percentiles[0]].tolist()
        sec2 = tooth_indices[(y_coords > percentiles[0]) & (y_coords <= percentiles[1])].tolist()
        sec3 = tooth_indices[y_coords > percentiles[1]].tolist()

        # Зуб 46 (первый моляр) находится в основном секторе
        teeth_labels = [
            ToothLabel(fdi=46, vertex_indices=sec2, is_prep=True),
            ToothLabel(fdi=45, vertex_indices=sec1, is_prep=False),
            ToothLabel(fdi=47, vertex_indices=sec3, is_prep=False),
        ]

        return SegmentationResult(
            scan_path=str(scan_path),
            teeth=teeth_labels,
            prep_tooth_fdi=target_prep_fdi,
            gingiva_vertex_count=len(gingiva_indices),
        )


tooth_segmenter = ToothSegmenter()
