# Сервис: Масштабы

`ScaleService` — сервис для расчетов масштабов, используется на страницах и в компонентах для вычислений и рекомендаций.

## Основные методы
- `calculate_scale_from_distance(real_distance: float, map_distance: float) -> ScaleCalculation`
  — расчет масштаба по расстояниям
- `calculate_area_scale(real_area: float, map_area: float) -> ScaleCalculation`
  — расчет масштаба по площадям
- `calculate_manual_scale(scale_text: str) -> ScaleCalculation`
  — ручной ввод масштаба (например, '1:5000')
- `get_standard_scales() -> List[str]`
  — список стандартных масштабов

## Пример использования
```python
from src.services.scale_service import ScaleService
result = ScaleService.calculate_scale_from_distance(1000, 20)
print(result.scale_text)  # '1:50'
```

## Сценарии применения
- Автоматический расчет масштаба по данным пользователя
- Проверка соответствия масштаба стандартам
- Получение точности для выбранного масштаба

Сервис не зависит от UI и может использоваться в любых модулях приложения. 