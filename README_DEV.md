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

При проблеме сборки `error GA230D127: The language version 3.9 specified for the package 'webview_flutter_android' is too high` 
заменить в `build/flutter/pubspec.yaml` версию `webview_flutter_android` на `^3.9.4`.

## Выпуск релиза

1. Выполнить повышение версии через утилиту `bump2version` и выполнить `push`;
2. Выполнить Pull Request в ветку main;
3. Выполнить сборку через команду `uv run flet build windows`;
4. Собрать в установочный файл через программу `NSIS`;
   1. Собрать все файлы из `build\windows\` в ZIP архив;
   2. Запустить `NSIS` в режиме сборки из ZIP архива;
   3. Указать путь к ZIP архиву;
   4. Указать имя установочника `GeoOffice v{major}.{minor}.{patch}`;
   5. Интерфейс `modern` + `unicode`;
   6. Папка установки `$PROGRAMFILES\GeoOffice`;
   7. Компрессия `LZMA`.
5. Залить релиз в https://github.com/maxmyslivets/GeoOffice/releases/new.
   1. Создать новый тег `v{major}.{minor}.{patch}`;
   2. Название релиза `GeoOffice v{major}.{minor}.{patch}`;
   3. Выбрать `latest release`.