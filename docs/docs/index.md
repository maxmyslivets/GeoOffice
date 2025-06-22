# GeoOffice: Документация для разработчиков

GeoOffice — модульное Python-приложение для автоматизации геодезических работ, управления документацией, расчетов координат, масштабов, создания картограмм и интеграции с AutoCAD.

## Архитектура
- **app.py** — точка входа, инициализация страниц, компонентов и сервисов
- **pages/** — страницы приложения (документы, координаты, картограмма и др.), наследуют BasePage
- **components/** — переиспользуемые UI-компоненты (меню, поиск, хлебные крошки, статистика)
- **services/** — бизнес-логика (работа с картограммой, масштабами, координатами)
- **models/** — структуры данных (картограмма, масштаб, координаты)
- **utils/** — утилиты (работа с файлами, логирование, расчёты)

## Ключевые классы и сервисы
- `GeoOfficeApp` — основной класс приложения
- `FileUtils`, `LoggerConfig`, `ScaleUtils`, `CoordinateUtils` — утилиты
- `CartogramService`, `ScaleService`, ... — сервисы для бизнес-логики
- `CartogramData`, `ScaleCalculation`, `Coordinate` — основные модели данных
- Компоненты: `CategorizedMenu`, `MenuSearch`, `Breadcrumbs`, `UsageStats`

## Быстрые ссылки
- [Архитектура](architecture.md)
- [Модели данных](models.md)
- [Сервисы](service_cartogram.md), [service_scale.md], ...
- [Компоненты](components_menu.md), [components_search.md], ...
- [Утилиты](utils.md)

Документация ориентирована на разработчиков: содержит описание структуры кода, интерфейсов классов, сервисов и компонентов. Для пользовательских сценариев см. отдельные разделы.

# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
