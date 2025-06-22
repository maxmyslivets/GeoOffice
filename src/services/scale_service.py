from typing import List, Optional
from src.models.scale_calculation import ScaleCalculation
from src.utils.scale_utils import ScaleUtils


class ScaleService:
    """
    Сервис для работы с масштабами.
    Позволяет рассчитывать масштаб по расстояниям, площадям, вручную, а также получать стандартные и рекомендуемые масштабы.
    """
    
    @staticmethod
    def calculate_scale_from_distances(real_distance: float, map_distance: float) -> ScaleCalculation:
        """
        Вычисляет масштаб по реальному и картографическому расстоянию.
        :param real_distance: Реальное расстояние
        :param map_distance: Расстояние на карте
        :return: ScaleCalculation с результатом
        """
        scale = ScaleUtils.calculate_scale_from_distance(real_distance, map_distance)
        scale_text = ScaleUtils.scale_to_text(scale)
        accuracy = ScaleUtils.get_accuracy_at_scale(scale)
        
        return ScaleCalculation(
            scale=scale,
            scale_text=scale_text,
            accuracy=accuracy,
            calculation_type="distance",
            real_distance=real_distance,
            map_distance=map_distance
        )
    
    @staticmethod
    def calculate_scale_from_areas(real_area: float, map_area: float) -> ScaleCalculation:
        """
        Вычисляет масштаб по реальной и картографической площади.
        :param real_area: Реальная площадь
        :param map_area: Площадь на карте
        :return: ScaleCalculation с результатом
        """
        scale = ScaleUtils.calculate_area_scale(real_area, map_area)
        scale_text = ScaleUtils.scale_to_text(scale)
        accuracy = ScaleUtils.get_accuracy_at_scale(scale)
        
        return ScaleCalculation(
            scale=scale,
            scale_text=scale_text,
            accuracy=accuracy,
            calculation_type="area",
            real_area=real_area,
            map_area=map_area
        )
    
    @staticmethod
    def calculate_manual_scale(scale_text: str) -> ScaleCalculation:
        """
        Создаёт расчет масштаба из введённого текстового значения.
        :param scale_text: Текстовое представление масштаба (например, '1:5000')
        :return: ScaleCalculation с результатом
        """
        scale = ScaleUtils.text_to_scale(scale_text)
        accuracy = ScaleUtils.get_accuracy_at_scale(scale)
        
        return ScaleCalculation(
            scale=scale,
            scale_text=scale_text,
            accuracy=accuracy,
            calculation_type="manual"
        )
    
    @staticmethod
    def get_standard_scales() -> List[str]:
        """
        Возвращает список стандартных масштабов.
        :return: Список строк с масштабами
        """
        return list(ScaleUtils.STANDARD_SCALES.keys())
    
    @staticmethod
    def get_recommended_scale(area_size: float) -> str:
        """
        Возвращает рекомендуемый масштаб для участка по его площади.
        :param area_size: Площадь участка
        :return: Рекомендуемый масштаб (строка)
        """
        return ScaleUtils.get_recommended_scale(area_size)
    
    @staticmethod
    def calculate_map_distance_from_scale(real_distance: float, scale: float) -> float:
        """
        Вычисляет расстояние на карте по реальному расстоянию и масштабу.
        :param real_distance: Реальное расстояние
        :param scale: Масштаб
        :return: Расстояние на карте
        """
        return ScaleUtils.calculate_map_distance(real_distance, scale)
    
    @staticmethod
    def calculate_real_distance_from_scale(map_distance: float, scale: float) -> float:
        """
        Вычисляет реальное расстояние по расстоянию на карте и масштабу.
        :param map_distance: Расстояние на карте
        :param scale: Масштаб
        :return: Реальное расстояние
        """
        return ScaleUtils.calculate_real_distance(map_distance, scale) 