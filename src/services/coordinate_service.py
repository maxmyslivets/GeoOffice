from typing import List
from src.models.coordinate import Coordinate
from src.utils.coordinate_utils import CoordinateUtils


class CoordinateService:
    """
    Сервис для работы с координатами.
    Позволяет парсить текст в объекты Coordinate и форматировать их обратно в текст.
    """
    @staticmethod
    def parse(text: str) -> List[Coordinate]:
        """
        Парсит текст в список объектов Coordinate.
        :param text: Строка с координатами (например, '100.1 200.2\n101.3 201.4')
        :return: Список Coordinate
        """
        raw_coords = CoordinateUtils.parse_coordinates(text)
        return [Coordinate(x, y) for x, y in raw_coords]

    @staticmethod
    def format(coords: List[Coordinate], sep: str = '\t') -> str:
        """
        Форматирует список объектов Coordinate в текст.
        :param coords: Список Coordinate
        :param sep: Разделитель между X и Y (по умолчанию табуляция)
        :return: Строка с координатами
        """
        return '\n'.join([str(c).replace('\t', sep) for c in coords]) 