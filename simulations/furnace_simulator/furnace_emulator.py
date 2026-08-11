"""
Эмулятор печи высокого температурного спекания (синтеризации) циркония.
Используется для телеметрии и аудита MDR EU 2017/745.
"""

from pydantic import BaseModel, Field
import random


class FurnaceTelemetry(BaseModel):
    """Схема данных телеметрии печи спекания."""
    furnace_id: str = "Dental-Sinter-01"
    status: str = "HEATING"  # "IDLE" | "HEATING" | "HOLDING" | "COOLING" | "FINISHED"
    current_temp_c: float = Field(default=1380.0, description="Текущая температура (°C)")
    target_temp_c: float = Field(default=1530.0, description="Целевая пиковая температура (°C)")
    profile_name: str = "Zirconia High-Speed"
    remaining_time_min: int = Field(default=100, description="Оставшееся время до конца (мин)")

    @classmethod
    def get_simulated_status(cls) -> "FurnaceTelemetry":
        """Генерирует симулированные данные печи."""
        return cls(
            current_temp_c=round(random.uniform(1375.0, 1385.0), 1),
            remaining_time_min=random.randint(95, 105),
        )


if __name__ == "__main__":
    telemetry = FurnaceTelemetry.get_simulated_status()
    print("Эмулятор Печи Синтеризации:")
    print(telemetry.model_dump_json(indent=2))
