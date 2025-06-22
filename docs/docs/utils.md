# Утилиты (utils)

## FileUtils
Класс для работы с файлами (JSON, директории, расширения):
- `save_json(data: dict, filename: str) -> bool` — сохранить данные в JSON
- `load_json(filename: str) -> dict | None` — загрузить данные из JSON
- `ensure_directory(path: str) -> bool` — создать директорию, если не существует
- `get_file_extension(filename: str) -> str` — получить расширение файла

## LoggerConfig / GeoOfficeLogger
Гибкая настройка логирования для приложения и модулей:
- Разделение логов по уровням и модулям
- Форматирование для файлов, консоли, UI
- Ротация и хранение логов

## ScaleUtils
Вспомогательные методы для работы с масштабами:
- `calculate_scale_from_distance(real_distance, map_distance)`
- `calculate_map_distance(real_distance, scale)`
- `calculate_real_distance(map_distance, scale)`
- `STANDARD_SCALES` — стандартные масштабы карт

## CoordinateUtils
Парсинг и форматирование координат:
- `parse(text: str) -> List[Coordinate]`
- `format(coords: List[Coordinate], sep: str = "\t") -> str` 