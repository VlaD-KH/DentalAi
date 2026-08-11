"""
Модуль содержит полную справочную номенклатуру зубов по международному стандарту FDI (ISO 3950).
Используется во всех сервисах сегментации, CAD-моделирования и визуализации.
"""

from enum import IntEnum
from typing import Dict, TypedDict


class ToothQuadrant(IntEnum):
    """Квадранты челюсти по FDI."""
    MAXILLARY_RIGHT = 1  # Верхняя челюсть справа
    MAXILLARY_LEFT = 2   # Верхняя челюсть слева
    MANDIBULAR_LEFT = 3  # Нижняя челюсть слева
    MANDIBULAR_RIGHT = 4 # Нижняя челюсть справа


class ToothCategory(IntEnum):
    """Категории типов зубов."""
    INCISOR = 1  # Резец
    CANINE = 2   # Клык
    PREMOLAR = 3 # Премоляр
    MOLAR = 4    # Моляр


class ToothInfo(TypedDict):
    """Структура описания зуба."""
    fdi: int
    name_ru: str
    name_en: str
    quadrant: ToothQuadrant
    category: ToothCategory
    is_upper: bool


# Полный справочник зубов по номенклатуре FDI (11–48)
FDI_TOOTH_MAP: Dict[int, ToothInfo] = {
    # Квадрант 1: Верхняя челюсть справа
    11: {"fdi": 11, "name_ru": "Верхний правый центральный резец", "name_en": "Maxillary Right Central Incisor", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.INCISOR, "is_upper": True},
    12: {"fdi": 12, "name_ru": "Верхний правый боковой резец", "name_en": "Maxillary Right Lateral Incisor", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.INCISOR, "is_upper": True},
    13: {"fdi": 13, "name_ru": "Верхний правый клык", "name_en": "Maxillary Right Canine", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.CANINE, "is_upper": True},
    14: {"fdi": 14, "name_ru": "Верхний правый первый премоляр", "name_en": "Maxillary Right 1st Premolar", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.PREMOLAR, "is_upper": True},
    15: {"fdi": 15, "name_ru": "Верхний правый второй премоляр", "name_en": "Maxillary Right 2nd Premolar", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.PREMOLAR, "is_upper": True},
    16: {"fdi": 16, "name_ru": "Верхний правый первый моляр", "name_en": "Maxillary Right 1st Molar", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.MOLAR, "is_upper": True},
    17: {"fdi": 17, "name_ru": "Верхний правый второй моляр", "name_en": "Maxillary Right 2nd Molar", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.MOLAR, "is_upper": True},
    18: {"fdi": 18, "name_ru": "Верхний правый третий моляр", "name_en": "Maxillary Right 3rd Molar", "quadrant": ToothQuadrant.MAXILLARY_RIGHT, "category": ToothCategory.MOLAR, "is_upper": True},

    # Квадрант 2: Верхняя челюсть слева
    21: {"fdi": 21, "name_ru": "Верхний левый центральный резец", "name_en": "Maxillary Left Central Incisor", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.INCISOR, "is_upper": True},
    22: {"fdi": 22, "name_ru": "Верхний левый боковой резец", "name_en": "Maxillary Left Lateral Incisor", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.INCISOR, "is_upper": True},
    23: {"fdi": 23, "name_ru": "Верхний левый клык", "name_en": "Maxillary Left Canine", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.CANINE, "is_upper": True},
    24: {"fdi": 24, "name_ru": "Верхний левый первый премоляр", "name_en": "Maxillary Left 1st Premolar", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.PREMOLAR, "is_upper": True},
    25: {"fdi": 25, "name_ru": "Верхний левый второй премоляр", "name_en": "Maxillary Left 2nd Premolar", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.PREMOLAR, "is_upper": True},
    26: {"fdi": 26, "name_ru": "Верхний левый первый моляр", "name_en": "Maxillary Left 1st Molar", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.MOLAR, "is_upper": True},
    27: {"fdi": 27, "name_ru": "Верхний левый второй моляр", "name_en": "Maxillary Left 2nd Molar", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.MOLAR, "is_upper": True},
    28: {"fdi": 28, "name_ru": "Верхний левый третий моляр", "name_en": "Maxillary Left 3rd Molar", "quadrant": ToothQuadrant.MAXILLARY_LEFT, "category": ToothCategory.MOLAR, "is_upper": True},

    # Квадрант 3: Нижняя челюсть слева
    31: {"fdi": 31, "name_ru": "Нижний левый центральный резец", "name_en": "Mandibular Left Central Incisor", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.INCISOR, "is_upper": False},
    32: {"fdi": 32, "name_ru": "Нижний левый боковой резец", "name_en": "Mandibular Left Lateral Incisor", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.INCISOR, "is_upper": False},
    33: {"fdi": 33, "name_ru": "Нижний левый клык", "name_en": "Mandibular Left Canine", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.CANINE, "is_upper": False},
    34: {"fdi": 34, "name_ru": "Нижний левый первый премоляр", "name_en": "Mandibular Left 1st Premolar", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.PREMOLAR, "is_upper": False},
    35: {"fdi": 35, "name_ru": "Нижний левый второй премоляр", "name_en": "Mandibular Left 2nd Premolar", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.PREMOLAR, "is_upper": False},
    36: {"fdi": 36, "name_ru": "Нижний левый первый моляр", "name_en": "Mandibular Left 1st Molar", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.MOLAR, "is_upper": False},
    37: {"fdi": 37, "name_ru": "Нижний левый второй моляр", "name_en": "Mandibular Left 2nd Molar", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.MOLAR, "is_upper": False},
    38: {"fdi": 38, "name_ru": "Нижний левый третий моляр", "name_en": "Mandibular Left 3rd Molar", "quadrant": ToothQuadrant.MANDIBULAR_LEFT, "category": ToothCategory.MOLAR, "is_upper": False},

    # Квадрант 4: Нижняя челюсть справа
    41: {"fdi": 41, "name_ru": "Нижний правый центральный резец", "name_en": "Mandibular Right Central Incisor", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.INCISOR, "is_upper": False},
    42: {"fdi": 42, "name_ru": "Нижний правый боковой резец", "name_en": "Mandibular Right Lateral Incisor", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.INCISOR, "is_upper": False},
    43: {"fdi": 43, "name_ru": "Нижний правый клык", "name_en": "Mandibular Right Canine", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.CANINE, "is_upper": False},
    44: {"fdi": 44, "name_ru": "Нижний правый первый премоляр", "name_en": "Mandibular Right 1st Premolar", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.PREMOLAR, "is_upper": False},
    45: {"fdi": 45, "name_ru": "Нижний правый второй премоляр", "name_en": "Mandibular Right 2nd Premolar", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.PREMOLAR, "is_upper": False},
    46: {"fdi": 46, "name_ru": "Нижний правый первый моляр", "name_en": "Mandibular Right 1st Molar", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.MOLAR, "is_upper": False},
    47: {"fdi": 47, "name_ru": "Нижний правый второй моляр", "name_en": "Mandibular Right 2nd Molar", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.MOLAR, "is_upper": False},
    48: {"fdi": 48, "name_ru": "Нижний правый третий моляр", "name_en": "Mandibular Right 3rd Molar", "quadrant": ToothQuadrant.MANDIBULAR_RIGHT, "category": ToothCategory.MOLAR, "is_upper": False},
}


def get_tooth_info(fdi: int) -> ToothInfo:
    """Возвращает информацию о зубе по его номеру FDI."""
    if fdi not in FDI_TOOTH_MAP:
        raise ValueError(f"Недопустимый номер зуба по FDI: {fdi}. Допустимы числа от 11 до 48.")
    return FDI_TOOTH_MAP[fdi]
