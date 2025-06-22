from dataclasses import dataclass
from typing import List, Tuple, Optional
from shapely.geometry import MultiPolygon

@dataclass
class GridCell:
    """
    Модель ячейки сетки.
    :param bounds: Границы ячейки (minx, miny, maxx, maxy)
    :param center: Центр ячейки (center_x, center_y)
    :param nomenclature: Номенклатура ячейки
    """
    bounds: Tuple[float, float, float, float]  # (minx, miny, maxx, maxy)
    center: Tuple[float, float]  # (center_x, center_y)
    nomenclature: str  # номенклатура ячейки

@dataclass
class NomenclatureInfo:
    """
    Модель информации о номенклатуре.
    :param base: Базовая часть номенклатуры (YY+XX)
    :param numbers: Список номеров квадратов
    :param full_nomenclature: Полная номенклатура
    """
    base: str  # базовая часть номенклатуры (YY+XX)
    numbers: List[str]  # список номеров квадратов
    full_nomenclature: str  # полная номенклатура

@dataclass
class CartogramData:
    """
    Модель данных картограммы.
    :param multi_polygon: Геометрия картограммы (MultiPolygon)
    :param grid_cells: Список ячеек сетки
    :param nomenclature_list: Список информации о номенклатуре
    :param coordinate_system: Система координат
    :param grid_size: Размер сетки (по умолчанию 250)
    """
    multi_polygon: MultiPolygon
    grid_cells: List[GridCell]
    nomenclature_list: List[NomenclatureInfo]
    coordinate_system: str
    grid_size: int = 250
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        Получение границ картограммы.
        :return: Кортеж (minx, miny, maxx, maxy)
        """
        return self.multi_polygon.bounds
    
    def get_cell_count(self) -> int:
        """
        Получение количества ячеек в картограмме.
        :return: Количество ячеек
        """
        return len(self.grid_cells)
    
    def get_nomenclature_count(self) -> int:
        """
        Получение количества уникальных номенклатур.
        :return: Количество уникальных номенклатур
        """
        return len(self.nomenclature_list) 