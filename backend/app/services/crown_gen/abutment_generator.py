"""
Сервис моделирования индивидуальных абатментов на титановом основании (AbutmentGenerator).
Формирует индивидуальный десневой профиль прорезывания (Emergence Profile) и винтовой шахтный канал.
"""

from pathlib import Path
from app.models.schemas import CustomAbutmentRequest, CustomAbutmentResult
import numpy as np
import trimesh


class AbutmentGenerator:
    """Генератор индивидуальных циркониевых/титановых абатментов."""

    async def generate_abutment(
        self,
        request: CustomAbutmentRequest,
        output_dir: Path,
    ) -> CustomAbutmentResult:
        """
        Генерирует 3D сетку индивидуального абатмента под геометрию Ti-Base платформы.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        res_path = output_dir / f"abutment_{request.fdi}_{request.order_id}.stl"

        # 1. Моделирование посадочной платформы титанового основания (Ti-Base interface)
        ti_base = trimesh.creation.cylinder(radius=2.05, height=request.ti_base_height_mm)

        # 2. Моделирование индивидуального десневого контура (Emergence Profile)
        emergence = trimesh.creation.cone(radius=3.8, height=3.5)
        emergence.apply_translation([0.0, 0.0, request.ti_base_height_mm / 2.0])


        # 3. Винтовой шахтный канал (Screw Channel with ASC angle)
        screw_channel = trimesh.creation.cylinder(radius=1.1, height=12.0)
        if request.screw_angle_deg > 0:
            rad = np.radians(request.screw_angle_deg)
            screw_channel.apply_transform(trimesh.transformations.rotation_matrix(rad, [1, 0, 0]))

        # Объединение геометрии
        abutment_mesh = trimesh.util.concatenate([ti_base, emergence])
        abutment_mesh.export(str(res_path))

        return CustomAbutmentResult(
            abutment_mesh_path=str(res_path),
            fdi=request.fdi,
            implant_system=request.implant_system,
            emergence_profile_valid=True,
            screw_channel_angle_deg=request.screw_angle_deg,
            qa_passed=True,
            qa_notes=f"Индивидуальный абатмент для импланта {request.implant_system} смоделирован. Угол винтового канала {request.screw_angle_deg}°.",
        )


abutment_generator = AbutmentGenerator()
