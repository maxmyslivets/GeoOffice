# Модели данных

## CartogramData
Модель данных картограммы:
- `multi_polygon: MultiPolygon` — геометрия
- `grid_cells: List[GridCell]` — ячейки сетки
- `nomenclature_list: List[NomenclatureInfo]` — список номенклатур
- `coordinate_system: str` — система координат
- `grid_size: int = 250` — размер сетки
- Методы: `get_bounds()`, `get_cell_count()`, `get_nomenclature_count()`

## ScaleCalculation
Модель для хранения результатов расчёта масштаба:
- `scale: float` — числовой масштаб
- `scale_text: str` — текстовое представление
- `accuracy: float` — точность
- `calculation_type: str` — тип расчёта (manual, area, distance)
- `real_area`, `map_area` — исходные данные

## Coordinate
Модель координаты:
- `x: float`
- `y: float`

Модели используются в сервисах, компонентах и для сериализации данных. 