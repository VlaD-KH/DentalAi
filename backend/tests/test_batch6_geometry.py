"""
Модульные тесты для Батча 6: Геометрическое ядро (GeometryProcessor).
"""

from app.services.geometry.mesh_processor import GeometryProcessor
import numpy as np
import trimesh


def test_mesh_cleaning():
    """Тестирует топологическую очистку 3D сетки."""
    box = trimesh.creation.box(extents=[10, 10, 10])
    processor = GeometryProcessor()

    cleaned = processor.clean_mesh(box)
    assert len(cleaned.vertices) > 0
    assert len(cleaned.faces) > 0


def test_cement_spacer_application():
    """Тестирует расчет цементного зазора (35 мкм)."""
    cone = trimesh.creation.cone(radius=5.0, height=8.0, sections=36)
    processor = GeometryProcessor()

    spaced = processor.apply_cement_spacer(cone, spacer_mm=0.035, marginal_offset_mm=0.8)

    assert spaced is not None
    assert len(spaced.vertices) == len(cone.vertices)
    # Проверяем изменение координат вершин
    assert not np.array_equal(spaced.vertices, cone.vertices)


def test_occlusal_carving():
    """Тестирует окклюзионную подгонку коронки под антагонист."""
    crown = trimesh.creation.cone(radius=5.0, height=8.0, sections=36)
    antagonist = trimesh.creation.box(extents=[12, 12, 4])
    antagonist.apply_translation([0, 0, 9.0])

    processor = GeometryProcessor()
    carved = processor.carve_occlusal_contacts(crown, antagonist, clearance_mm=-0.05)

    assert len(carved.vertices) == len(crown.vertices)
