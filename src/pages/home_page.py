from pathlib import Path
from urllib.parse import quote

import flet as ft
import sys

from .base_page import BasePage
from ..components.link_section import LinkSection

from ..services.project_service import ProjectService
from ..utils.file_utils import FileUtils
from ..utils.interface_utils import InterfaceUtils

from ..utils.logger_config import log_exception


sys.path.append("..")


class HomePage(BasePage):
    """Главная страница приложения GeoOffice. Содержит UI и логику поиска файлов."""
    
    def __init__(self, app):
        """
        Инициализация главной страницы, создание всех UI-компонентов и переменных состояния.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.page = None
        self.search_query = ""
        self.results_container = None
        self.loading_indicator = None
        self.search_field = None
        self.project_service = ProjectService(app.database_project_service)

    def get_content(self):
        """
        Формирует и возвращает содержимое главной страницы (UI-компоненты Flet).
        :return: Flet Column с элементами интерфейса
        """
        self.page = self.app.page
        # Создаём поля поиска
        self.search_field = ft.TextField(
            hint_text="Название объекта...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_query_change,
            border_radius=20,
            text_size=14,
            height=40,
            expand=True
        )
        self.loading_indicator = ft.ProgressRing(visible=False, width=30, height=30)
        self.results_container = ft.Container(
            content=ft.Text("Результаты поиска появятся здесь...", color=ft.Colors.GREY_500),
            padding=10,
            # bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            margin=ft.margin.only(top=10)
        )
        self.project_search(empty_search=True)
        return ft.Column([
            ft.Row([
                ft.Image(src="icon.png", height=64),
                ft.Column([
                    ft.Text("Добро пожаловать в GeoOffice", size=32, weight=ft.FontWeight.BOLD,
                            overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                    ft.Text("Ведение документации по объектам и геодезические расчеты",
                            size=16, color=ft.Colors.GREY_600, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2, expand=True),
            ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Divider(height=40),

            LinkSection(self.app).create(title="Закреплённые папки",
                                         links=self.app.settings.paths.favorite_folders, is_edit=True),
            self.create_statistics_section(),
            
            ft.Text("Поиск по объектам", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        self.search_field,
                        self.loading_indicator
                    ], spacing=10, expand=True),
                    self.results_container
                ]),
                padding=20,
                border_radius=8,
                margin=ft.margin.only(top=10, bottom=10),
                expand=True
            ),
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

    @log_exception
    def on_query_change(self, e):
        """
        Обработчик изменения строки поиска.
        """
        self.search_query = e.control.value
        if self.search_query:
            self.results_container.content = ft.Text("Поиск...", color=ft.Colors.GREY_500)
            self.loading_indicator.visible = True
            self.page.update()
            self.project_search()
        else:
            self.project_search(empty_search=True)

    @log_exception
    def project_search(self, empty_search=False):
        """
        Запускает поиск по объектам и обновляет UI с результатами.
        """
        # FIXME: При возвращении на домашнюю страницу контейнер с результатами поиска не сбрасывается
        # FIXME: Элементы списка результатов не совпадают со своими id проектов
        if empty_search:
            results = self.project_service.search_projects(self.search_query, return_all=True, limit=50)
        else:
            results = self.project_service.search_projects(self.search_query)
        items = []
        import re
        query_text = self.search_query.strip()
        highlight_re = re.compile(re.escape(query_text), re.IGNORECASE)
        for project_id, number, name, customer in results:
            text = f"{number} {name}"
            icon = ft.Icons.DESCRIPTION
            display_name = []
            last = 0
            for m in highlight_re.finditer(text):
                if m.start() > last:
                    display_name.append(ft.Text(text[last:m.start()]))
                display_name.append(ft.Text(text[m.start():m.end()], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE))
                last = m.end()
            if last < len(text):
                display_name.append(ft.Text(text[last:]))
            if not display_name:
                display_name = [ft.Text(text)]
            items.append(
                ft.ListTile(
                    leading=ft.Icon(icon, color=ft.Colors.GREY_700),
                    title=ft.Row(display_name, spacing=0),
                    subtitle=ft.Text(customer, size=11, color=ft.Colors.GREY_500),
                    on_click=lambda e: self.app.show_project_page(project_id),
                    dense=True,
                    bgcolor=ft.Colors.BLUE_50
                )
            )
        if not items:
            self.results_container.content = ft.Text("Ничего не найдено", color=ft.Colors.GREY_500)
        else:
            self.results_container.content = ft.Column(items, scroll=ft.ScrollMode.AUTO, height=350)
        self.loading_indicator.visible = False
        self.page.update()
