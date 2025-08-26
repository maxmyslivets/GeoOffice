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