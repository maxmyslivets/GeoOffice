from typing import List, Tuple


class CoordinateUtils:
    """
    Утилиты для парсинга и форматирования координат.
    Позволяют преобразовывать текст в список координат и обратно.
    """
    @staticmethod
    def parse_coordinates(text: str) -> List[Tuple[float, float]]:
        """
        Парсит координаты из текста.
        Ожидает строки вида 'X Y' или 'X;Y' (разделитель — пробел или точка с запятой).
        :param text: Строка с координатами
        :return: Список кортежей (X, Y)
        :raises ValueError: Если строка не соответствует формату или не удаётся преобразовать в число
        """
        coords = []
        for line in text.strip().splitlines():
            line = line.strip().replace(';', ' ')
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f"Неверный формат строки: '{line}'")
            try:
                x = float(parts[0].replace(',', '.'))
                y = float(parts[1].replace(',', '.'))
                coords.append((x, y))
            except Exception:
                raise ValueError(f"Ошибка преобразования в число: '{line}'")
        return coords

    @staticmethod
    def format_coordinates(coords: List[Tuple[float, float]], sep: str = '\t') -> str:
        """
        Форматирует список координат в текст с заданным разделителем.
        :param coords: Список кортежей (X, Y)
        :param sep: Разделитель между X и Y (по умолчанию табуляция)
        :return: Строка с координатами
        """
        return '\n'.join([f"{x:.3f}{sep}{y:.3f}" for x, y in coords]) 