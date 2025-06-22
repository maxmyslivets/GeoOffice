from typing import Tuple, Dict, List
import math


class ScaleUtils:
    """
    Утилиты для работы с масштабами: преобразования, вычисления, рекомендации стандартных масштабов.
    """
    
    # Стандартные масштабы карт
    STANDARD_SCALES = {
        "1:500": 500,
        "1:1000": 1000,
        "1:2000": 2000,
        "1:5000": 5000,
        "1:10000": 10000
    }
    
    @staticmethod
    def calculate_scale_from_distance(real_distance: float, map_distance: float) -> float:
        """
        Вычисляет масштаб по реальному и картографическому расстоянию.
        :param real_distance: Реальное расстояние
        :param map_distance: Расстояние на карте
        :return: Масштаб (число)
        :raises ValueError: Если map_distance == 0
        """
        if map_distance == 0:
            raise ValueError("Картографическое расстояние не может быть равно нулю")
        return real_distance / map_distance
    
    @staticmethod
    def calculate_map_distance(real_distance: float, scale: float) -> float:
        """
        Вычисляет расстояние на карте по реальному расстоянию и масштабу.
        :param real_distance: Реальное расстояние
        :param scale: Масштаб
        :return: Расстояние на карте
        """
        return real_distance / scale
    
    @staticmethod
    def calculate_real_distance(map_distance: float, scale: float) -> float:
        """
        Вычисляет реальное расстояние по расстоянию на карте и масштабу.
        :param map_distance: Расстояние на карте
        :param scale: Масштаб
        :return: Реальное расстояние
        """
        return map_distance * scale
    
    @staticmethod
    def scale_to_text(scale: float) -> str:
        """
        Преобразует числовой масштаб в текстовый формат (например, '1:1000').
        :param scale: Масштаб (число)
        :return: Строка масштаба
        """
        return f"1:{int(scale)}"
    
    @staticmethod
    def text_to_scale(scale_text: str) -> float:
        """
        Преобразует текстовый масштаб в числовой.
        :param scale_text: Строка масштаба (например, '1:1000')
        :return: Масштаб (число)
        """
        if scale_text.startswith("1:"):
            return float(scale_text[2:])
        return float(scale_text)
    
    @staticmethod
    def get_accuracy_at_scale(scale: float) -> float:
        """
        Возвращает точность масштаба в метрах (0.1 мм на карте).
        :param scale: Масштаб
        :return: Точность в метрах
        """
        return scale * 0.1  # 0.1 мм на карте
    
    @staticmethod
    def get_recommended_scale(area_size: float) -> str:
        """
        Рекомендует масштаб по размеру участка.
        :param area_size: Площадь участка (в квадратных километрах)
        :return: Рекомендуемый масштаб (строка)
        """
        if area_size < 0.01:  # менее 1 га
            return "1:500"
        elif area_size < 0.1:  # менее 10 га
            return "1:1000"
        elif area_size < 1:  # менее 100 га
            return "1:2000"
        elif area_size < 10:  # менее 1000 га
            return "1:5000"
        else:
            return "1:10000"
    
    @staticmethod
    def calculate_area_scale(real_area: float, map_area: float) -> float:
        """
        Вычисляет масштаб по площадям.
        :param real_area: Реальная площадь
        :param map_area: Площадь на карте
        :return: Масштаб (число)
        :raises ValueError: Если map_area == 0
        """
        if map_area == 0:
            raise ValueError("Площадь на карте не может быть равна нулю")
        return math.sqrt(real_area / map_area) 