import sys
import flet as ft

from .base_page import BasePage

sys.path.append("..")


class ToolsPage(BasePage):
    """Страница приложения GeoOffice. Содержит карточки инструментов."""

    def __init__(self, app):
        """
        Инициализация страницы.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.page = None

    def get_content(self):
        """
        Формирует и возвращает содержимое главной страницы (UI-компоненты Flet).
        :return: Flet Column с элементами интерфейса
        """
        self.page = self.app.page
        return ft.Placeholder(expand=True, color=ft.Colors.random())
