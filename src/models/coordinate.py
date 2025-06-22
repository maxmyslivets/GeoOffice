from dataclasses import dataclass

@dataclass
class Coordinate:
    """
    Модель координаты.
    :param x: Координата X
    :param y: Координата Y
    """
    x: float
    y: float

    def __str__(self):
        """
        Возвращает строковое представление координаты в формате 'X\tY'.
        :return: Строка с координатами
        """
        return f"{self.x:.3f}\t{self.y:.3f}" 