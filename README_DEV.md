# GeoOffice

## UV

### Запуск окружения
```shell
.venv/Scripts/activate
```

### Установка пакетов
```shell
uv add *package*
```

## Версионирование

### Патч (например, исправления)
```shell
bump2version patch
```

### Минорное обновление (новая функциональность)
```shell
bump2version minor
```

### Мажорное обновление (ломающее изменения)
```shell
bump2version major
```

## Запуск приложения (через uv)

Запуск оконного приложения:

```shell
uv run flet run
```

Горячий запуск:
```shell
uv run flet run -d -r
```

## Сборка

### Windows

```shell
uv run flet build windows
```