# Сервис: Картограмма

`CartogramService` — сервис для работы с картограммами: парсинг DXF, генерация сетки, расчет номенклатур, экспорт.

## Основные методы
- `parse_dxf(file_path: str) -> MultiPolygon`
  — парсинг DXF-файла, извлечение геометрии
- `create_grid(multi_polygon: MultiPolygon, grid_size: int) -> List[GridCell]`
  — создание сетки по полигонам
- `calculate_nomenclature(grid_cells: List[GridCell]) -> List[NomenclatureInfo]`
  — расчет номенклатур
- `export_grid_to_dxf(grid_cells: List[GridCell], file_path: str)`
  — экспорт сетки в DXF
- `detect_coordinate_system(multi_polygon: MultiPolygon) -> str`
  — определение системы координат

## Пример использования
```python
from src.services.cartogram_service import CartogramService
mp = CartogramService.parse_dxf('input.dxf')
grid = CartogramService.create_grid(mp, 250)
CartogramService.export_grid_to_dxf(grid, 'output.dxf')
```

## Сценарии применения
- Автоматизация создания картограмм для отчетов
- Генерация сетки и расчет номенклатур для кадастровых работ
- Экспорт результатов в DXF для дальнейшей работы в AutoCAD

Сервис не зависит от UI и может использоваться в любых модулях приложения. 