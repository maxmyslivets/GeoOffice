import sys
import flet as ft

from .base_page import BasePage
from components.link_section import LinkSection
from services.project_service import ProjectService
from utils.logger_config import log_exception

sys.path.append("..")


class DashboardPage(BasePage):
    """Страница приложения GeoOffice. Содержит интерактивные доски для анализа работы."""

    def __init__(self, app):
        """
        Инициализация страницы.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.page = None
        self.project_service = ProjectService(app.database_service)

    def get_content(self):
        """
        Формирует и возвращает содержимое главной страницы (UI-компоненты Flet).
        :return: Flet Column с элементами интерфейса
        """
        self.page = self.app.page
        link_section = LinkSection(self.app).create(title="Закреплённые папки",
                                                    links=self.app.settings.paths.favorite_folders,
                                                    is_edit=True)

        return ft.Column([
            link_section,
            # self.create_statistics_section(),
        ])

    @log_exception
    def create_statistics_section(self):
        """Создание секции статистики"""
        stats = self.project_service.get_project_statistics()

        def create_stat_card(title: str, value: int, icon: str, color: str = ft.Colors.BLUE):
            """Создание карточки статистики"""
            return ft.Card(ft.Container(
                content=ft.Column([
                    ft.Icon(icon, color=color, size=24),
                    ft.Text(title, size=14, color=ft.Colors.GREY_600),
                    ft.Text(str(value), size=18, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=10,
                border_radius=8,
                width=150,
                height=90
            ))

        return ft.Container(
            ft.Column([
                ft.Text("Статистика объектов", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    create_stat_card("Активные", stats["active_projects"], ft.Icons.FOLDER_OPEN, ft.Colors.GREEN),
                    create_stat_card("Выданы", stats["completed_projects"], ft.Icons.FOLDER_SPECIAL, ft.Colors.BLUE),
                    create_stat_card("В архиве", stats["archived_projects"], ft.Icons.FOLDER_OFF, ft.Colors.GREY),
                    create_stat_card("Перспективные", stats["promising_projects"], ft.Icons.DESCRIPTION, ft.Colors.ORANGE),
                    create_stat_card("Всего", stats["total_projects"], ft.Icons.FOLDER),
                ], spacing=10, wrap=True, alignment=ft.MainAxisAlignment.START,
                )
            ]),
            padding=ft.padding.only(left=10, right=10, top=15, bottom=15),
            border_radius=8,
            expand=True
        )
