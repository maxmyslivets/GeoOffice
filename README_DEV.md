# GeoOffice

## UV

### Запуск окружения
```shell
.venv/Scripts/activate
```

### Установка пакетов
```shell
uv pip install flet
```

### Фиксация зависимостей
```shell
uv pip freeze | uv pip compile - -o requirements.txt
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

Запуск Web приложения:

```shell
uv run flet run --web
```

Горячий запуск:
```shell
uv run flet run --web -d -r
```

## Сборка

### Android

```shell
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).


### Windows

```shell
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).


### MkDocs

## Сборка документации
```shell
mkdocs build -f docs/mkdocs.yml
```

## Просмотр документации

```shell
mkdocs serve -f docs/mkdocs.yml
```
