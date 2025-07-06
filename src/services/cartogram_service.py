import numpy as np
from typing import List, Tuple, Dict
from shapely.geometry import box, Polygon, MultiPolygon, Point
import ezdxf
from src.models.cartogram_models import CartogramData, GridCell, NomenclatureInfo
from src.utils.logger_config import get_logger

logger = get_logger("services.cartogram_service")


class CartogramService:
    """
    Сервис для работы с картограммами.
    Позволяет рассчитывать номенклатуру, определять систему координат, парсить DXF-файлы, создавать сетку, сохранять сетку в DXF и получать список номенклатур.
    """
    
    def __init__(self):
        """
        Инициализация сервиса картограмм. По умолчанию используется система координат 'СК63'.
        """
        self.coordinate_system = "СК63"  # По умолчанию СК63
        logger.info(f"Инициализирован сервис картограмм с системой координат: {self.coordinate_system}")
        
    def set_coordinate_system(self, system: str):
        """
        Установка системы координат для расчётов.
        :param system: Название системы координат ('СК63' или 'МСК')
        :raises ValueError: Если система координат не поддерживается
        """
        if system in ["СК63", "МСК"]:
            old_system = self.coordinate_system
            self.coordinate_system = system
            logger.info(f"Изменена система координат: {old_system} -> {system}")
        else:
            error_msg = f"Неподдерживаемая система координат: {system}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_coordinate_system(self) -> str:
        """
        Получение текущей системы координат.
        :return: Название системы координат
        """
        return self.coordinate_system
    
    def calculate_nomenclature(self, x: float, y: float) -> str:
        """
        Расчёт номенклатуры для заданных координат.
        :param x: Координата X
        :param y: Координата Y
        :return: Строка с номенклатурой (например, 'YY+XX;NN')
        """
        logger.debug(f"Расчет номенклатуры для координат: X={x:.2f}, Y={y:.2f}")
        
        # Преобразуем координаты в зависимости от системы координат
        if self.coordinate_system == "СК63":
            # Отбрасываем первые 2 цифры для СК63
            x = x % 100000
            y = y % 100000
        
        # Получаем тысячные части координат
        x_thousand = int(x / 1000)
        y_thousand = int(y / 1000)
        
        # Вычисляем остаток от деления на 1000 для определения позиции внутри квадрата
        x_remainder = int((x % 1000) / 250)  # 0-3
        y_remainder = int((y % 1000) / 250)  # 0-3
        
        # Вычисляем номер квадрата (1-16)
        # Нумерация идет сверху слева (0,0) до снизу справа (3,3)
        square_number = (3 - y_remainder) * 4 + x_remainder + 1
        
        # Формируем номенклатуру в формате "YY+XX;NN"
        nomenclature = f"{y_thousand:02d}+{x_thousand:02d};{square_number:02d}"
        
        logger.debug(f"Рассчитана номенклатура: {nomenclature}")
        return nomenclature
        
    def detect_coordinate_system(self, x: float, y: float) -> str:
        """
        Определение системы координат по значениям X и Y.
        :param x: Координата X
        :param y: Координата Y
        :return: 'СК63' или 'МСК'
        """
        # Проверяем наличие миллионной части в координатах
        # В СК63 координаты содержат миллионную часть (например, 6 123 456)
        # В МСК координаты не содержат миллионную часть (например, 123 456)
        
        def has_million_part(coord):
            # Проверяем, есть ли миллионная часть в числе
            return coord >= 1_000_000
        
        # Если хотя бы одна из координат содержит миллионную часть, это СК63
        if has_million_part(x) or has_million_part(y):
            logger.info(f"Определена система координат СК63 по координатам: X={x:.2f}, Y={y:.2f}")
            return "СК63"
        else:
            logger.info(f"Определена система координат МСК по координатам: X={x:.2f}, Y={y:.2f}")
            return "МСК"
    
    def parse_dxf_file(self, file_path: str) -> MultiPolygon:
        """
        Парсинг DXF-файла и извлечение мультиполигона.
        :param file_path: Путь к DXF-файлу
        :return: MultiPolygon с полигонами из файла
        :raises ValueError: Если не найдено валидных полигонов
        """
        try:
            doc = ezdxf.readfile(file_path)
            polygons = []
            
            for entity in doc.modelspace():
                if entity.dxftype() == 'LWPOLYLINE':
                    try:
                        # получаем координаты вершин полилинии
                        points = entity.get_points()
                        # извлекаем только координаты x и y
                        vertices = [(point[0], point[1]) for point in points]
                        # создаем полигон и проверяем его валидность
                        polygon = Polygon(vertices)
                        if polygon.is_valid and not polygon.is_empty:
                            polygons.append(polygon)
                    except Exception as e:
                        logger.error(f"Ошибка при обработке полилинии: {e}")
                        continue
            
            if not polygons:
                raise ValueError("Файл не содержит валидных полигонов")
                
            return MultiPolygon(polygons)
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге DXF файла: {e}")
            raise
    
    def create_grid(self, multi_polygon: MultiPolygon, grid_size: int = 250) -> List[GridCell]:
        """
        Создание сетки для картограммы по мультиполигону.
        :param multi_polygon: Мультиполигон участка
        :param grid_size: Размер ячейки сетки (по умолчанию 250)
        :return: Список ячеек сетки (GridCell)
        """
        try:
            logger.info("Создание сетки")
            
            # Получаем границы мультиполигона
            minx, miny, maxx, maxy = multi_polygon.bounds
            
            # Добавляем отступ 10% от размера полигона
            x_margin = (maxx - minx) * 0.1
            y_margin = (maxy - miny) * 0.1
            
            # Расширяем границы с учетом отступа
            minx -= x_margin
            miny -= y_margin
            maxx += x_margin
            maxy += y_margin
            
            # Округляем границы до ближайшей сетки
            minx_grid = int(minx / grid_size) * grid_size
            miny_grid = int(miny / grid_size) * grid_size
            maxx_grid = int(np.ceil(maxx / grid_size)) * grid_size
            maxy_grid = int(np.ceil(maxy / grid_size)) * grid_size
            
            num_cells_x = int((maxx_grid - minx_grid) / grid_size)
            num_cells_y = int((maxy_grid - miny_grid) / grid_size)
            
            logger.info(f"Размер сетки: {num_cells_x}x{num_cells_y} ячеек")
            
            grid_cells = []
            
            # Создаем сетку только в пределах расширенных границ
            for i in range(num_cells_x):
                for j in range(num_cells_y):
                    x = minx_grid + i * grid_size
                    y = miny_grid + j * grid_size
                    cell = box(x, y, x + grid_size, y + grid_size)
                    
                    # Проверяем, что ячейка пересекается с полигоном и не находится внутри дыр
                    if cell.intersects(multi_polygon):
                        # Проверяем каждый полигон в мультиполигоне
                        is_valid = False
                        for polygon in multi_polygon.geoms:
                            # Если ячейка пересекается с внешним контуром
                            if cell.intersects(polygon.exterior):
                                # Проверяем, что ячейка не находится внутри дыр
                                is_in_hole = False
                                for interior in polygon.interiors:
                                    if cell.within(Polygon(interior)):
                                        is_in_hole = True
                                        break
                                if not is_in_hole:
                                    is_valid = True
                                    break
                        
                        if is_valid:
                            # Получаем номенклатуру для центра ячейки
                            center_x = x + grid_size / 2
                            center_y = y + grid_size / 2
                            nomenclature = self.calculate_nomenclature(center_x, center_y)
                            
                            grid_cell = GridCell(
                                bounds=(x, y, x + grid_size, y + grid_size),
                                center=(center_x, center_y),
                                nomenclature=nomenclature
                            )
                            grid_cells.append(grid_cell)
            
            logger.info(f"Создано {len(grid_cells)} ячеек сетки")
            return grid_cells
            
        except Exception as e:
            logger.error(f"Ошибка при создании сетки: {e}")
            raise
    
    def get_nomenclature_list(self, grid_cells: List[GridCell]) -> List[NomenclatureInfo]:
        """
        Получение списка уникальных номенклатур по ячейкам сетки.
        :param grid_cells: Список ячеек сетки
        :return: Список NomenclatureInfo
        """
        try:
            if not grid_cells:
                return []
                
            # Создаем словарь для группировки номенклатур
            nomenclature_groups = {}
            
            # Собираем номенклатуры для каждой ячейки
            for cell in grid_cells:
                # Разбиваем номенклатуру на части
                parts = cell.nomenclature.split(';')
                if len(parts) == 2:
                    base = parts[0]  # YY+XX
                    number = parts[1]  # NN
                    
                    if base not in nomenclature_groups:
                        nomenclature_groups[base] = set()
                    nomenclature_groups[base].add(number)
            
            # Формируем отсортированный список
            nomenclature_list = []
            for base in sorted(nomenclature_groups.keys()):
                numbers = sorted(nomenclature_groups[base])
                nomenclature_str = f"{base};{','.join(numbers)}"
                
                nomenclature_info = NomenclatureInfo(
                    base=base,
                    numbers=list(numbers),
                    full_nomenclature=nomenclature_str
                )
                nomenclature_list.append(nomenclature_info)
            
            return nomenclature_list
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка номенклатур: {e}")
            raise
    
    def save_grid_to_dxf(self, grid_cells: List[GridCell], multi_polygon: MultiPolygon, file_path: str):
        """
        Сохранение сетки и полигона в DXF-файл.
        :param grid_cells: Список ячеек сетки
        :param multi_polygon: Мультиполигон участка
        :param file_path: Путь для сохранения DXF-файла
        """
        try:
            # Создаем новый DXF документ
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Добавляем линии сетки
            for cell in grid_cells:
                # Получаем координаты ячейки
                minx, miny, maxx, maxy = cell.bounds
                
                # Создаем полилинию для квадрата
                points = [
                    (minx, miny),  # левый нижний угол
                    (maxx, miny),  # правый нижний угол
                    (maxx, maxy),  # правый верхний угол
                    (minx, maxy),  # левый верхний угол
                    (minx, miny),  # замыкаем полилинию
                ]
                msp.add_lwpolyline(points)
            
            # Добавляем текст номенклатуры
            for cell in grid_cells:
                # Создаем текст
                text = msp.add_text(
                    cell.nomenclature,
                    dxfattribs={
                        'height': 20,  # Высота текста
                        'style': 'Standard',
                    }
                )
                # Устанавливаем позицию и выравнивание текста
                text.set_placement(
                    cell.center,  # Точка вставки
                    align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER  # Выравнивание по центру
                )
            
            # Если есть полигон, добавляем его
            if multi_polygon is not None:
                # Обрабатываем каждый полигон в мультиполигоне
                for polygon in multi_polygon.geoms:
                    # Добавляем внешний контур
                    exterior_coords = list(polygon.exterior.coords)
                    msp.add_lwpolyline(exterior_coords)
                    
                    # Добавляем внутренние контуры (дыры)
                    for interior in polygon.interiors:
                        interior_coords = list(interior.coords)
                        msp.add_lwpolyline(interior_coords)
            
            # Сохраняем файл
            doc.saveas(file_path)
            logger.info(f"Сетка успешно сохранена в файл: {file_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении DXF файла: {e}")
            raise 