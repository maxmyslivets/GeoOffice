import flet as ft
from src.utils.logger_config import setup_logging, get_logger, log_exception


logger = get_logger()


class BaseApp:

    @log_exception
    def __init__(self, app_name: str):
        self.app_name = app_name
        global logger
        logger = get_logger(self.app_name)
        logger.info(f"🔧 Инициализация приложения {self.app_name}")
        self.page = None
        self.menu = None

    @log_exception
    def main(self, page: ft.Page):
        logger.info("🎨 Инициализация пользовательского интерфейса")
        self.page = page
        page.title = self.app_name
        page.update()
        logger.info("✅ Пользовательский интерфейс инициализирован")

    # @log_exception
    # def create_main_content(self):
    #     """Создание основного контента"""
    #     logger.debug("📄 Создание основного контента")
    #
    #     # Создаем контейнер для основного содержимого
    #     self.content_container = ft.Container(
    #         content=ft.Text("Загрузка..."),
    #         padding=20,
    #         expand=True
    #     )
    #
    #     # Объединяем хлебные крошки и контент
    #     self.content_area = ft.Column([
    #         self.content_container
    #     ], expand=True)
    #
    #     logger.debug("✅ Основной контент создан")
    #
    # @log_exception
    # def initialize_pages(self):
    #     """Инициализация всех страниц"""
    #     logger.debug("📚 Инициализация страниц приложения")
    #     self.pages = {
    #         'home': HomePage(self),
    #         'settings': SettingsPage(self),
    #     }
    #     logger.info(f"✅ Инициализировано {len(self.pages)} страниц")
    #
    # @log_exception
    # def show_page(self, page_name):
    #     """Показать страницу по имени"""
    #     if page_name in self.pages:
    #         logger.debug(f"📖 Отображение страницы: {page_name}")
    #         page_instance = self.pages[page_name]
    #         self.content_container.content = page_instance.get_scrollable_content()
    #         self.current_view = page_name
    #
    #         self.page.update()
    #         logger.debug(f"✅ Страница {page_name} отображена")
    #     else:
    #         logger.warning(f"⚠️ Страница {page_name} не найдена")


