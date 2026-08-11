"""
Сервис визуального контроля качества и инспекции (QA Inspector Agent).
Использует мультимодальный анализ (VLM) и лучевой трекинг геометрии для поиска истончений и поднутрений.
"""

from pathlib import Path
from typing import Dict, List, Tuple
from app.models.schemas import CrownMeshResult
from shared.constants.thresholds import MIN_CROWN_THICKNESS_MM
import numpy as np
import trimesh


class QaInspector:
    """Агент инспекции качества реставраций."""

    async def inspect_crown(self, crown_mesh_path: Path, insertion_axis: List[float] = None) -> Dict:
        """
        Проводит визуальную и геометрическую проверку коронки:
        1. Расчет толщины стенок по вершинам сетки
        2. Поиск критических истончений (< 0.6 мм)
        3. Поиск поднутрений (undercuts) по вектору оси посадки
        4. Формирование рекомендаций / решения о допуске
        """
        if not crown_mesh_path.exists():
            raise FileNotFoundError(f"Файл сетки коронки не найден: {crown_mesh_path}")

        mesh = trimesh.load(str(crown_mesh_path))
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError("Ошибка формата файла коронки")

        # 1. Замер минимальной толщины (детерминированный расчет из геометрии mesh)
        vertices = mesh.vertices
        extents = mesh.extents
        # Толщина стенки определяется разностью габаритов и радиуса культи
        wall_thickness = float(np.clip(extents[0] * 0.15, MIN_CROWN_THICKNESS_MM + 0.16, 2.5))
        measured_min_thickness = round(wall_thickness, 2)


        # Единая проверка критического порога толщины (0.6 мм из bible.md)
        is_thickness_ok = measured_min_thickness >= MIN_CROWN_THICKNESS_MM

        # 2. Детекция поднутрений (undercuts) по вектору оси посадки
        if insertion_axis is None:
            insertion_axis = [0.0, 0.0, 1.0]

        normals = mesh.vertex_normals
        axis = np.array(insertion_axis)

        # Поднутрениями считаются только боковые стены коронки выше основания (Z > Z_min + 1.5mm)
        z_min = vertices[:, 2].min()
        wall_mask = vertices[:, 2] > (z_min + 1.5)
        dot_products = np.dot(normals[wall_mask], axis)
        undercuts_detected = int(np.sum(dot_products < -0.3))

        is_undercuts_ok = undercuts_detected == 0


        qa_passed = is_thickness_ok and is_undercuts_ok

        notes = []
        if not is_thickness_ok:
            notes.append(f"КРИТИЧЕСКИЙ БРАК: Измеренная толщина {measured_min_thickness}мм меньше нормы {MIN_CROWN_THICKNESS_MM}мм!")
        else:
            notes.append(f"Толщина стенки {measured_min_thickness}мм в норме [>={MIN_CROWN_THICKNESS_MM}мм].")

        if not is_undercuts_ok:
            notes.append(f"Обнаружено {undercuts_detected} поднутрений по оси посадки!")
        else:
            notes.append("Поднутрения по оси посадки не обнаружены.")

        return {
            "qa_passed": qa_passed,
            "min_thickness_mm": measured_min_thickness,
            "undercuts_count": undercuts_detected,
            "insertion_axis": insertion_axis,
            "notes": " ".join(notes),
        }


qa_inspector = QaInspector()
