import flet as ft
from abc import ABC, abstractmethod
from src.utils.logger_config import get_logger, log_exception


class BasePage(ABC):
    """
    Базовый абстрактный класс для всех страниц приложения GeoOffice.
    Определяет базовые методы для работы с UI и уведомлениями.
    """

    @log_exception
    def __init__(self, app):
        """
        Инициализация базовой страницы.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        self.page = app.page
        self._content = None
        
        # Получаем логгер для конкретной страницы
        self.logger = get_logger(f"pages.{self.__class__.__name__.lower()}")
        self.logger.debug(f"🔧 Инициализация страницы {self.__class__.__name__}")
    
    @abstractmethod
    def get_content(self):
        """
        Абстрактный метод. Возвращает содержимое страницы (UI-компоненты).
        :return: Flet UI-элемент
        """
        pass
    
    @log_exception
    def get_scrollable_content(self):
        """
        Возвращает содержимое страницы с прокруткой.
        :return: Flet Container с прокручиваемым содержимым
        """
        self.logger.debug("📄 Создание прокручиваемого контента")
        content = ft.Container(
            content=ft.Column([
                self.get_content()
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            alignment=ft.alignment.top_left,
            expand=True
        )
        self.logger.debug("✅ Прокручиваемый контент создан")
        return content
    
    @log_exception
    def update_page(self):
        """
        Обновить страницу (UI).
        """
        if self.page:
            self.logger.debug("🔄 Обновление страницы")
            self.page.update()
            self.logger.debug("✅ Страница обновлена")
        else:
            self.logger.warning("⚠️ Страница не инициализирована")
