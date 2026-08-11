"""
Модульные тесты для Батча 4: Детекция уступной линии (MarginDetector).
"""

from app.services.margin.margin_detector import MarginDetector
import trimesh


def test_margin_extraction_on_cone():
    """Тестирует детекцию уступа на культе конусообразной формы."""
    cone = trimesh.creation.cone(radius=4.5, height=7.0, sections=36)
    detector = MarginDetector()

    margin = detector.extract_margin_curve(cone, prep_fdi=46, num_sample_points=36)

    assert margin.prep_fdi == 46
    assert len(margin.points) == 36
    assert margin.accuracy_score >= 0.99
    assert margin.insertion_axis == [0.0, 0.0, 1.0]

    # Проверяем, что все точки кривой уступа содержат валидные 3D координаты
    for pt in margin.points:
        assert isinstance(pt.x, float)
        assert isinstance(pt.y, float)
        assert isinstance(pt.z, float)
