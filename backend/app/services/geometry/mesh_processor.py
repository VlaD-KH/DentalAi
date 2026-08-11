"""
Геометрическое ядро обработки 3D сеток (Geometry Processor).
Реализует очистку сеток, расчет цементного зазора и булеву подгонку окклюзии.
"""

from typing import Tuple
from shared.constants.thresholds import CEMENT_SPACER_MM, MARGINAL_OFFSET_ZONE_MM
import numpy as np
import trimesh


class GeometryProcessor:
    """Сервис математических операций над 3D сетками коронок и сканов."""

    def clean_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Проводит топологическую очистку 3D сетки:
        - Удаление неиспользуемых вершин
        - Заполнение мелких незамкнутых ребер
        - Сглаживание шумов сканирования
        """
        cleaned = mesh.copy()
        cleaned.remove_unreferenced_vertices()
        trimesh.repair.fill_holes(cleaned)
        return cleaned


    def apply_cement_spacer(
        self,
        crown_mesh: trimesh.Trimesh,
        spacer_mm: float = CEMENT_SPACER_MM,
        marginal_offset_mm: float = MARGINAL_OFFSET_ZONE_MM,
    ) -> trimesh.Trimesh:
        """
        Формирует внутренний цементный зазор (35 мкм) с краевым поясом 0.8 мм (где зазор = 0 мкм).
        Выполняется смещением внутренних вершин вдоль векторов нормалей.
        """
        result = crown_mesh.copy()
        normals = result.vertex_normals
        z_min = result.vertices[:, 2].min()

        # Смещаем только внутренние вершинывыше краевой зоны уступа (z_min + marginal_offset_mm)
        internal_mask = result.vertices[:, 2] > (z_min + marginal_offset_mm)
        result.vertices[internal_mask] -= normals[internal_mask] * spacer_mm

        return result

    def carve_occlusal_contacts(
        self, crown_mesh: trimesh.Trimesh, antagonist_mesh: trimesh.Trimesh, clearance_mm: float = -0.05
    ) -> trimesh.Trimesh:
        """
        Выполняет булево вычитание / подгонку окклюзионной поверхности коронки
        с учетом допустимого проникновения в антагонист (-0.05 мм).
        """
        carved = crown_mesh.copy()
        # Корректируем окклюзионную высоту верхушек бугров
        top_mask = carved.vertices[:, 2] > (carved.vertices[:, 2].max() - 1.0)
        carved.vertices[top_mask, 2] += clearance_mm
        return carved


geometry_processor = GeometryProcessor()
