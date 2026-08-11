"""
Эмулятор 5-осевого фрезерного станка ЧПУ для стоматологических дисков.
Используется для авто-тестов и визуализации телеметрии на дашборде.
"""

from pydantic import BaseModel, Field
import random
import time


class CncTelemetry(BaseModel):
    """Схема данных телеметрии 5-осевого фрезера."""
    machine_id: str = "Dental-CNC-5X-01"
    status: str = "RUNNING"  # "IDLE" | "RUNNING" | "PAUSED" | "ERROR"
    spindle_rpm: int = Field(default=45000, description="Обороты шпинделя (RPM)")
    feed_rate_mm_min: float = Field(default=1200.0, description="Скорость подачи (мм/мин)")
    current_bur_mm: float = Field(default=0.6, description="Диаметр активной фрезы (мм)")
    bur_wear_percent: float = Field(default=18.5, description="Износ фрезы (%)")
    active_gcode_line: int = Field(default=1420, description="Текущая строка G-кода")
    air_pressure_bar: float = Field(default=6.4, description="Давление воздуха (Бар)")

    @classmethod
    def get_simulated_status(cls) -> "CncTelemetry":
        """Генерирует симулированный снимок телеметрии с небольшими флуктуациями."""
        return cls(
            spindle_rpm=random.randint(44800, 45200),
            feed_rate_mm_min=round(random.uniform(1180.0, 1220.0), 1),
            bur_wear_percent=round(random.uniform(18.0, 19.0), 1),
            active_gcode_line=random.randint(1000, 5000),
            air_pressure_bar=round(random.uniform(6.3, 6.5), 1),
        )


if __name__ == "__main__":
    telemetry = CncTelemetry.get_simulated_status()
    print("Эмулятор ЧПУ Фрезера:")
    print(telemetry.model_dump_json(indent=2))
