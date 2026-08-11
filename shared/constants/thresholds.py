"""
Константы, пороги качества и технологические ограничения проекта DentalAi.
Определены в bible.md и обязательны для валидации на всех этапах CAD/CAM конвейера.
"""

# Геометрические допуски и пороги реставрации (в мм)
MIN_CROWN_THICKNESS_MM: float = 0.6       # Критический минимум толщины стенки циркония (мм)
MIN_VENEER_THICKNESS_MM: float = 0.3      # Критический минимум толщины винира из стеклокерамики/E.max (мм)
RECOMMENDED_THICKNESS_MIN_MM: float = 0.8  # Рекомендуемый минимум толщины (мм)
RECOMMENDED_THICKNESS_MAX_MM: float = 1.2  # Рекомендуемый максимум толщины (мм)


# Параметры мостовидных протезов (Bridges)
BRIDGE_CONNECTOR_MIN_AREA_3UNIT_MM2: float = 9.0   # Мин. площадь сечения коннектора для 3-ед. моста (мм²)
BRIDGE_CONNECTOR_MIN_AREA_LONG_MM2: float = 12.0   # Мин. площадь сечения коннектора для протяженных мостов (мм²)
PONTIC_TISSUE_GAP_MM: float = 0.02                 # Зазор промывной части понтика до десны (мм)

# Клинические параметры цементного зазора (в мм и мкм)
CEMENT_SPACER_MICRONS: float = 35.0        # Стандартный радиальный цементный зазор (мкм)
CEMENT_SPACER_MM: float = 0.035            # Зазор в миллиметрах (0.035 мм = 35 мкм)
MARGINAL_OFFSET_ZONE_MM: float = 0.8       # Ширина краевой зоны уступа (зазор = 0 мкм)
MAX_MARGINAL_GAP_MICRONS: float = 70.0     # Максимально допустимый краевой зазор (мкм)
CRITICAL_MARGINAL_GAP_MICRONS: float = 120.0 # Порог брака краевого прилегания (мкм)

# Окклюзионные контакты
OCCLUSAL_INTERFERENCE_LIMIT_MM: float = -0.05 # Допустимый предел внедрения в антагонист (мм)
OCCLUSAL_REDUCTION_MIN_MM: float = 1.0       # Минимальное пространство окклюзионной редукции (мм)

# Параметры диоксида циркония и CAM раскроя
ZIRCONIA_DISK_DIAMETER_MM: float = 98.5    # Стандартный диаметр диска (мм)
ZIRCONIA_SHRINKAGE_FACTOR_MIN: float = 1.20 # Мин. коэффициент усадки при спекании
ZIRCONIA_SHRINKAGE_FACTOR_MAX: float = 1.25 # Макс. коэффициент усадки при спекании

# Параметры литников (sprues)
SPRUE_DIAMETER_MM: float = 2.5             # Диаметр удерживающего литника (мм)
SPRUE_MARGIN_SAFETY_OFFSET_MM: float = 1.0 # Минимальный отступ литника от линии уступа (мм)

# Параметры инструмента ЧПУ фрезера (диаметры фрез в мм)
CNC_BUR_ROUGHING_MM: float = 2.0           # Черновая фреза
CNC_BUR_SEMI_FINISHING_MM: float = 1.0     # Получистовая фреза
CNC_BUR_FINISHING_MM: float = 0.6          # Чистовая фреза
CNC_BUR_FISSURE_MM: float = 0.3            # Фиссурная микрофреза

# Профиль синтеризации (температуры в °C)
SINTERING_PEAK_TEMP_STANDARD_C: float = 1500.0  # Стандартная пиковая T
SINTERING_PEAK_TEMP_SPEED_C: float = 1550.0     # Скоростная пиковая T
