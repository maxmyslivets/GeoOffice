from dataclasses import dataclass
from typing import Optional

@dataclass
class ScaleCalculation:
    """
    Модель для хранения результатов расчёта масштаба.
    :param scale: Числовое значение масштаба
    :param scale_text: Текстовое представление масштаба
    :param accuracy: Точность расчёта
    :param calculation_type: Тип расчёта ("distance", "area", "manual")
    :param real_distance: Реальное расстояние (если применимо)
    :param map_distance: Расстояние на карте (если применимо)
    :param real_area: Реальная площадь (если применимо)
    :param map_area: Площадь на карте (если применимо)
    """
    scale: float
    scale_text: str
    accuracy: float
    calculation_type: str  # "distance", "area", "manual"
    real_distance: Optional[float] = None
    map_distance: Optional[float] = None
    real_area: Optional[float] = None
    map_area: Optional[float] = None
    
    def __str__(self):
        """
        Возвращает строковое представление результата расчёта масштаба.
        :return: Строка с описанием масштаба и точности
        """
        return f"Масштаб: {self.scale_text}, Точность: {self.accuracy:.2f} м" 