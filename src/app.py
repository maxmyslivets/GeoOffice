import flet as ft
from pathlib import Path

from src.models.settings_model import Settings
from src.services.database_service import DatabaseService

from src.utils.logger_config import setup_logging, get_logger, log_exception
from src.utils.file_utils import FileUtils

from src.components.categorized_menu import CategorizedMenu
from src.components.breadcrumbs import Breadcrumbs
from src.components.menu_search import MenuSearch

from src.pages.home_page import HomePage
from src.pages.documents_page import DocumentsPage
from src.pages.coordinates_page import CoordinatesPage
from src.pages.conversion_page import ConversionPage
from src.pages.autocad_page import AutocadPage
from src.pages.taxation_page import TaxationPage
from src.pages.settings_page import SettingsPage
from src.pages.scale_page import ScalePage
from src.pages.cartogram_page import CartogramPage


# Настройка логирования
logger = get_logger("main")


class GeoOfficeApp:
    @log_exception
    def __init__(self):
        logger.info("🔧 Инициализация приложения GeoOffice")
        self.page = None
        self.current_view = None

        # Меню с категориями
        self.categorized_menu = None
        # Контейнер для меню
        self.navigation = None
        # Свернутое меню с кнопкой разворачивания вверху
        self.collapsed_navigation = None

        # Компонент хлебных крошек
        self.breadcrumbs = None
        # Контейнер для хлебных крошек
        self.breadcrumbs_container = None
        # Контейнер для основного содержимого
        self.content_container = None
        # Объединяем хлебные крошки и контент
        self.content_area = None

        # Инициализация настроек
        self.settings = Settings(data=None)
        self.load_settings()

        # Инициализация страниц
        self.pages = {}

        # Инициализация поиска по меню
        self.menu_search = MenuSearch(self)

        # Инициализация базы данных
        self.database_service: DatabaseService | None = None
        self.init_database()

        logger.info("✅ Приложение инициализировано")

    @log_exception
    def load_settings(self) -> None:
        """Чтение настроек приложения"""
        logger.debug("📂 Чтение настроек приложения")
        settings_data = FileUtils.load_json(Path("storage") / "data" / "settings.json")
        if settings_data is not None:
            try:
                self.settings = Settings(data=settings_data)
                logger.info("✅ Настройки загружены успешно")
            except Warning as e:
                logger.warning(e)
        else:
            logger.info("📝 Создание настроек по умолчанию")
            self.save_settings()

    @log_exception
    def save_settings(self):
        """Сохранение настроек приложения"""
        logger.debug("💾 Сохранение настроек приложения")
        if FileUtils.save_json(self.settings.to_dict(), Path("storage") / "data" / "settings.json"):
            logger.info("✅ Настройки успешно сохранены")
        else:
            logger.error("❌ Ошибка сохранения настроек")

    @log_exception
    def main(self, page: ft.Page):
        logger.info("🎨 Инициализация пользовательского интерфейса")
        self.page = page
        page.title = "GeoOffice"
        page.theme_mode = self.settings.interface.theme
        page.window.width = 1200
        page.window.height = 1200
        page.window.min_width = 800
        page.window.min_height = 600
        page.padding = 20

        # Создание навигации
        self.create_navigation()

        # Создание основного контента
        self.create_main_content()

        # Инициализация страниц
        self.initialize_pages()

        # Создаем Row с навигацией и контентом
        main_layout = ft.Row([
            self.navigation,  # Полное меню
            self.collapsed_navigation,  # Свернутое меню
            ft.VerticalDivider(width=1),  # Разделитель
            self.content_area,  # Основной контент
        ], expand=True)

        # Добавляем основной интерфейс на страницу
        page.add(main_layout)
        page.update()

        # Показ главной страницы по умолчанию
        if not self.current_view:
            self.show_home_page()

        # Переключение меню в свернутый вид
        self.toggle_menu_visibility()

        page.update()
        logger.info("✅ Пользовательский интерфейс инициализирован")

    @log_exception
    def create_navigation(self):
        """Создание боковой навигации с категориями"""
        logger.debug("🧭 Создание навигации с категориями")

        # Создаем заголовок меню
        menu_header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.MENU, color=ft.Colors.BLUE, size=24),
                ft.Text("GeoOffice", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ], spacing=10),
            padding=ft.padding.only(left=15, right=15, top=15, bottom=15),
            on_click=self.toggle_menu_visibility,  # Клик по заголовку скрывает/показывает меню
            ink=True
        )

        # Создаем меню с категориями
        self.categorized_menu = CategorizedMenu(self)
        menu_content = self.categorized_menu.create_menu()

        # Создаем контейнер для меню
        self.navigation = ft.Container(
            content=ft.Column([
                menu_header,
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                menu_content
            ]),
            width=280,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            padding=0
        )

        logger.debug("✅ Навигация с категориями создана")

    @log_exception
    def create_collapsed_menu(self):
        """Создание свернутого меню с иконками"""
        logger.debug("📱 Создание свернутого меню")

        # Создаем кнопку разворачивания вверху
        expand_button = ft.IconButton(
            icon=ft.Icons.MENU,  # Такая же иконка как для скрытия
            icon_color=ft.Colors.BLUE,
            icon_size=24,
            on_click=self.toggle_menu_visibility,
            tooltip="Развернуть меню"
        )

        # Создаем иконки для основных функций
        icon_buttons = [
            ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color=ft.Colors.BLUE,
                icon_size=24,
                on_click=lambda e: self.show_page('home'),
                tooltip="Главная"
            ),
            ft.IconButton(
                icon=ft.Icons.DESCRIPTION,
                icon_color=ft.Colors.BLUE,
                icon_size=24,
                on_click=lambda e: self.show_page('documents'),
                tooltip="Документы"
            ),
            ft.IconButton(
                icon=ft.Icons.EXPLORE,
                icon_color=ft.Colors.GREEN,
                icon_size=24,
                on_click=lambda e: self.show_page('coordinates'),
                tooltip="Координаты"
            ),
            ft.IconButton(
                icon=ft.Icons.TRANSFORM,
                icon_color=ft.Colors.GREEN,
                icon_size=24,
                on_click=lambda e: self.show_page('conversion'),
                tooltip="Конвертация"
            ),
            ft.IconButton(
                icon=ft.Icons.STRAIGHTEN,
                icon_color=ft.Colors.GREEN,
                icon_size=24,
                on_click=lambda e: self.show_page('scale'),
                tooltip="Масштабы"
            ),
            ft.IconButton(
                icon=ft.Icons.BUILD,
                icon_color=ft.Colors.ORANGE,
                icon_size=24,
                on_click=lambda e: self.show_page('autocad'),
                tooltip="AutoCAD"
            ),
            ft.IconButton(
                icon=ft.Icons.FOREST,
                icon_color=ft.Colors.ORANGE,
                icon_size=24,
                on_click=lambda e: self.show_page('taxation'),
                tooltip="Таксация"
            ),
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color=ft.Colors.GREY,
                icon_size=24,
                on_click=lambda e: self.show_page('settings'),
                tooltip="Настройки"
            ),
        ]

        # Создаем свернутое меню с кнопкой разворачивания вверху
        self.collapsed_navigation = ft.Container(
            content=ft.Column([
                expand_button,  # Кнопка разворачивания вверху
                ft.Divider(height=1, color=ft.Colors.GREY_300),  # Разделитель
                *icon_buttons  # Все иконки функций
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=60,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            padding=ft.padding.only(top=10, bottom=10),
            visible=False
        )

        logger.debug("✅ Свернутое меню создано")

    @log_exception
    def toggle_menu_visibility(self, e=None):
        """Переключение видимости меню"""
        logger.debug("🔄 Переключение видимости меню")

        if hasattr(self, 'navigation') and hasattr(self, 'collapsed_navigation'):
            if self.navigation.visible:
                # Скрываем полное меню, показываем свернутое
                self.navigation.visible = False
                self.navigation.width = 0
                self.collapsed_navigation.visible = True
                self.collapsed_navigation.width = 60
            else:
                # Показываем полное меню, скрываем свернутое
                self.navigation.visible = True
                self.navigation.width = 280
                self.collapsed_navigation.visible = False
                self.collapsed_navigation.width = 0

            self.page.update()
            logger.debug("✅ Видимость меню переключена")

    @log_exception
    def create_main_content(self):
        """Создание основного контента"""
        logger.debug("📄 Создание основного контента")

        # Создаем компонент хлебных крошек
        self.breadcrumbs = Breadcrumbs(self)

        # Создаем свернутое меню
        self.create_collapsed_menu()

        # Создаем контейнер для хлебных крошек
        self.breadcrumbs_container = ft.Container(
            content=self.breadcrumbs.create_breadcrumbs("home"),
            padding=0
        )

        # Создаем контейнер для основного содержимого
        self.content_container = ft.Container(
            content=ft.Text("Загрузка..."),
            padding=20,
            expand=True
        )

        # Объединяем хлебные крошки и контент
        self.content_area = ft.Column([
            self.breadcrumbs_container,
            self.content_container
        ], expand=True)

        logger.debug("✅ Основной контент создан")

    @log_exception
    def initialize_pages(self):
        """Инициализация всех страниц"""
        logger.debug("📚 Инициализация страниц приложения")
        self.pages = {
            'home': HomePage(self),
            'documents': DocumentsPage(self),
            'documents_import': DocumentsPage(self),  # Заглушка - используем ту же страницу
            'documents_export': DocumentsPage(self),  # Заглушка - используем ту же страницу
            'documents_archive': DocumentsPage(self),  # Заглушка - используем ту же страницу
            'coordinates': CoordinatesPage(self),
            'conversion': ConversionPage(self),
            'scale': ScalePage(self),
            'autocad': AutocadPage(self),
            'taxation': TaxationPage(self),
            'settings': SettingsPage(self),
            'cartogram': CartogramPage(self),
        }
        logger.info(f"✅ Инициализировано {len(self.pages)} страниц")

    @log_exception
    def show_page(self, page_name):
        """Показать страницу по имени"""
        if page_name in self.pages:
            logger.debug(f"📖 Отображение страницы: {page_name}")
            page_instance = self.pages[page_name]
            self.content_container.content = page_instance.get_scrollable_content()
            self.current_view = page_name

            # Обновляем хлебные крошки
            self.breadcrumbs_container.content = self.breadcrumbs.create_breadcrumbs(page_name)

            # Обновляем состояние меню
            if hasattr(self, 'categorized_menu'):
                self.categorized_menu.set_current_page(page_name)

            # Обновляем активную страницу в свернутом меню
            self.update_collapsed_menu_active(page_name)

            self.page.update()
            logger.debug(f"✅ Страница {page_name} отображена")
        else:
            logger.warning(f"⚠️ Страница {page_name} не найдена")

    @log_exception
    def show_project_page(self, project_id):
        """Показать страницу объекта по id"""
        logger.debug(f"📖 Отображение страницы объекта id={project_id}")
        
        # Создаем динамическую страницу проекта
        from src.pages.project_page import ProjectPage
        project_page = ProjectPage(self, project_id)
        project = project_page.project
        
        # Отображаем страницу проекта
        self.content_container.content = project_page.get_scrollable_content()
        self.current_view = f"project_id{project.id}"
        
        # Обновляем хлебные крошки
        self.breadcrumbs_container.content = self.breadcrumbs.create_breadcrumbs(f"{project.number} {project.name}")

        self.page.update()
        logger.debug(f"✅ Страница объекта id={project.id} отображена")

    @log_exception
    def update_collapsed_menu_active(self, page_name):
        """Обновление активной страницы в свернутом меню"""
        if hasattr(self, 'collapsed_navigation'):
            # Маппинг страниц на индексы кнопок в свернутом меню
            # Индексы сдвинуты на 2 из-за кнопки разворачивания и разделителя вверху
            page_to_index = {
                'home': 2,
                'documents': 3,
                'documents_import': 3,
                'documents_export': 3,
                'documents_archive': 3,
                'cartogram': 3,
                'coordinates': 4,
                'conversion': 5,
                'scale': 6,
                'autocad': 7,
                'taxation': 8,
                'settings': 9
            }

            # Обновляем цвета всех кнопок (начиная с индекса 2, после кнопки разворачивания и разделителя)
            for i, button in enumerate(self.collapsed_navigation.content.controls[2:], start=2):
                if i == page_to_index.get(page_name, -1):
                    # Активная страница - синий цвет
                    button.icon_color = ft.Colors.BLUE
                else:
                    # Неактивная страница - возвращаем исходный цвет
                    if i < 4:  # Главная и Документы (индексы 2-3)
                        button.icon_color = ft.Colors.BLUE
                    elif i < 7:  # Геодезические работы (индексы 4-6)
                        button.icon_color = ft.Colors.GREEN
                    elif i < 9:  # Специализированные инструменты (индексы 7-8)
                        button.icon_color = ft.Colors.ORANGE
                    else:  # Система (индекс 9)
                        button.icon_color = ft.Colors.GREY

    @log_exception
    def show_home_page(self, e=None):
        """Показ главной страницы"""
        logger.debug("🏠 Отображение главной страницы")
        self.show_page('home')

    @log_exception
    def _show_snack_bar(self, message, level='info'):
        """Показать уведомление"""
        try:
            logger.debug(f"💬 Показ уведомления: {message}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text(message),
                                              behavior=ft.SnackBarBehavior.FLOATING)
            self.page.snack_bar.open = True
            self.page.snack_bar.show_close_icon = True
            match level:
                case 'error':
                    self.page.snack_bar.bgcolor = ft.Colors.RED
                case 'warning':
                    self.page.snack_bar.bgcolor = ft.Colors.ORANGE
                case _:
                    self.page.snack_bar.bgcolor = ft.Colors.LIGHT_BLUE_ACCENT_700
            self.page.overlay.append(self.page.snack_bar)
            self.page.update()
        except Exception as e:
            logger.error(f"Ошибка показа уведомления: {e}")

    @log_exception
    def show_error(self, message):
        """Показать ошибку"""
        try:
            logger.error(f"❌ Ошибка: {message}")
            self._show_snack_bar(f"Ошибка: {message}", 'error')
        except Exception as e:
            logger.error(f"Ошибка показа ошибки: {e}")

    @log_exception
    def show_warning(self, message):
        """Показать предупреждение"""
        try:
            logger.warning(f"⚠️ Предупреждение: {message}")
            self._show_snack_bar(f"Предупреждение: {message}", 'warning')
        except Exception as e:
            logger.error(f"Ошибка показа предупреждения: {e}")

    @log_exception
    def show_info(self, message):
        """Показать предупреждение"""
        try:
            logger.info(f"ℹ️ Информация: {message}")
            self._show_snack_bar(f"{message}", 'info')
        except Exception as e:
            logger.error(f"Ошибка показа информации: {e}")

    @log_exception
    def init_database(self):
        self.database_service = DatabaseService(
            Path(self.settings.paths.file_server) / self.settings.paths.database_path)


@log_exception
def main(page: ft.Page):
    logger.info("🚀 Запуск главной функции приложения")
    app = GeoOfficeApp()
    app.main(page)
    logger.info("✅ Главная функция завершена")


if __name__ == "__main__":
    # Настройка логирования при запуске
    setup_logging("GeoOffice")
    logger.info("🎯 Запуск приложения GeoOffice")
    ft.app(target=main)
