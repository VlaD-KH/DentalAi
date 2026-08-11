"""
Генератор синтетических 3D STL сканов челюстей для автоматизированного тестирования.
Генерирует макет зубного ряда нижней челюсти с препарированным зубом 46.
"""

from pathlib import Path
import math
import trimesh
import numpy as np


def generate_synthetic_dental_arch(output_path: Path, prep_fdi: int = 46) -> Path:
    """
    Генерирует тестовую синтетическую 3D сетку челюсти в формате STL.
    Создает U-образную дугу зубов с выделенной культей под заданным номером FDI.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Базовая десна (дуга)
    t = np.linspace(-math.pi / 3, math.pi / 3, 16)
    radius = 35.0
    x_coords = radius * np.sin(t)
    y_coords = radius * np.cos(t)

    meshes = []

    # Создание каждого зуба вдоль дуги
    for idx, (x, y) in enumerate(zip(x_coords, y_coords)):
        # Вычисляем ориентацию
        angle = t[idx]

        if idx == 8:  # Место культи препарированного зуба (FDI 46)
            # Культя: усеченный конус с уступом
            tooth = trimesh.creation.cone(radius=4.5, height=7.0, sections=32)
            # Смещаем вверх для формирования уступа
            tooth.apply_translation([x, y, 3.5])
        else:
            # Обычный зуб: сфера/цилиндр
            tooth = trimesh.creation.cylinder(radius=5.0, height=8.0, sections=24)
            tooth.apply_translation([x, y, 4.0])

        meshes.append(tooth)

    # Базовое основание десны (цоколь)
    base_box = trimesh.creation.box(extents=[80.0, 60.0, 4.0])
    base_box.apply_translation([0, 25.0, -2.0])
    meshes.append(base_box)

    # Объединение всех элементов в единую 3D сетку
    combined_mesh = trimesh.util.concatenate(meshes)

    # Сохранение в STL
    combined_mesh.export(str(output_path))
    return output_path


if __name__ == "__main__":
    test_file = Path("./data/scans/test_lower_arch_46.stl")
    res_path = generate_synthetic_dental_arch(test_file)
    print(f"Сгенерирован синтетический 3D скан: {res_path.resolve()}")
