import traceback

import flet as ft
from pathlib import Path

from src.components.menu import Menu
from src.models.settings_model import Settings
from src.pages.projects_page import ProjectsPage
from src.pages.tools_page import ToolsPage
from src.services.background_service import BackgroundService
from src.services.database_service import DatabaseService

from src.utils.logger_config import setup_logging, get_logger, log_exception
from src.utils.file_utils import FileUtils

from src.pages.dashboard_page import DashboardPage
# from src.pages.projects_page import ProjectsPage
# from src.pages.tools_page import ToolsPage
from src.pages.settings_page import SettingsPage


# Настройка логирования
logger = get_logger("main")


class GeoOfficeApp:
    @log_exception
    def __init__(self):
        logger.info("🔧 Инициализация приложения GeoOffice")
        self.page = None
        # self.current_view = None

        # Меню
        self.menu = None
        # Контейнер для основного содержимого
        self.content = None

        self.background_service = BackgroundService()

        # Инициализация настроек
        self.settings = Settings(data=None)
        self.load_settings()

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
        page.window.width = self.settings.interface.width
        page.window.height = self.settings.interface.height
        page.window.min_width = 800
        page.window.min_height = 600
        page.window.left = self.settings.interface.left
        page.window.top = self.settings.interface.top
        page.padding = 20

        # Создание навигации
        self.create_menu()

        # Создание основного контента
        self.create_content()

        # Создаем Row с навигацией и контентом
        main_layout = ft.Row([
            self.menu,  # Полное меню
            ft.VerticalDivider(width=1),  # Разделитель
            self.content,  # Основной контент
        ], expand=True)

        # Добавляем основной интерфейс на страницу
        page.add(main_layout)
        page.update()

        # Показ начальной страницы
        self.show_page(DashboardPage)

        page.update()

        logger.info("✅ Пользовательский интерфейс инициализирован")

    @log_exception
    def create_menu(self):
        """Создание боковой навигации с категориями"""
        logger.debug("🧭 Создание навигации с категориями")

        menu_items = [
            ("Доска", {"icon": ft.Icons.DASHBOARD, "page": DashboardPage}),
            ("Объекты", {"icon": ft.Icons.ARTICLE, "page": ProjectsPage}),
            # ("Инструменты", {"icon": ft.Icons.BUILD, "page": ToolsPage}),
            ("Настройки", {"icon": ft.Icons.SETTINGS, "page": SettingsPage}),
        ]

        # Создаем меню с категориями
        self.menu = Menu(self).create_menu(menu_items)

        logger.debug("✅ Навигация с категориями создана")

    @log_exception
    def create_content(self):
        """Создание основного контента"""
        logger.debug("📄 Создание основного контента")

        # Создаем контейнер для основного содержимого
        self.content = ft.Container(
            content=ft.Text("Загрузка..."),
            padding=20,
            expand=True
        )

        logger.debug("✅ Основной контент создан")

    @log_exception
    def show_page(self, page):
        """Показать страницу"""
        logger.debug(f"📖 Отображение страницы: {page}")
        self.content.content = page(self).get_scrollable_content()
        self.page.update()

    @log_exception
    def show_project_page(self, project_id):
        """Показать страницу объекта по id"""
        logger.debug(f"📖 Отображение страницы объекта id={project_id}")
        
        # Создаем динамическую страницу проекта
        from src.pages.project_page import ProjectPage
        project_page = ProjectPage(self, project_id)
        project = project_page.project
        
        # Отображаем страницу проекта
        self.content.content = project_page.get_scrollable_content()

        self.page.update()
        logger.debug(f"✅ Страница объекта id={project.id} отображена")

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
    def __del__(self):
        """Деструктор - выполняется при удалении страницы"""
        try:
            self.settings.interface.width = int(self.page.window.width)
            self.settings.interface.height = int(self.page.window.height)
            self.settings.interface.left = int(self.page.window.left)
            self.settings.interface.top = int(self.page.window.top)
            # self.settings.interface.last_page = self.page
            self.save_settings()
        except Exception as e:
            traceback.print_exc()


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
