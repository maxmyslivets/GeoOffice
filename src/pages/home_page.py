import flet as ft
from .base_page import BasePage
import os
import difflib
import threading
import re
import sys
sys.path.append("..")
from ..utils import search_utils
from ..services.semantic_search_service import SemanticSearchService
import time
import socket
from src.services.search_service import SearchService

from ..utils.logger_config import log_exception


class HomePage(BasePage):
    """Главная страница приложения GeoOffice. Содержит UI и логику поиска файлов."""
    
    def __init__(self, app):
        """
        Инициализация главной страницы, создание всех UI-компонентов и переменных состояния.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.search_query = ""
        self.search_path = ""
        self.use_default_path = False
        self.search_results = []
        self.results_container = None
        self.path_field = None
        self.checkbox = None
        self.smart_checkbox = None
        self.page = None
        self.default_path_key = "geooffice_default_search_path"
        self.loading_indicator = None
        self.search_field = None
        self.use_smart_search = False
        self.use_morph_search = False
        self.search_service = SearchService()

    @staticmethod
    def get_user_default_path_file():
        """
        Получить путь к файлу, где хранится путь поиска по умолчанию для текущего пользователя.
        :return: str - путь к файлу
        """
        computer_name = socket.gethostname()
        return os.path.join("storage", "users", computer_name, "default_path.txt")

    def get_content(self):
        """
        Формирует и возвращает содержимое главной страницы (UI-компоненты Flet).
        :return: Flet Column с элементами интерфейса
        """
        self.page = self.app.page
        # Создаём поля поиска
        self.search_field = ft.TextField(
            hint_text="Поиск объектов...",
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
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            margin=ft.margin.only(top=10)
        )
        return ft.Column([
            ft.Row([
                ft.Image(src="icon.png", height=64),
                ft.Column([
                    ft.Text("Добро пожаловать в GeoOffice", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Ведение геодезической документации и расчетов", size=16, color=ft.Colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
            ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=40),
            
            ft.Text("Обзор системы", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.create_info_card("Документы", "Создание геодезической документации",
                                      ft.Icons.DESCRIPTION, ft.Colors.BLUE, self.show_documents),
                self.create_info_card("Приложения", "Вычисление координат и масштабов, конвертация файлов",
                                      ft.Icons.EXPLORE, ft.Colors.GREEN, self.show_geodetic_works),
                self.create_info_card("Специализированные инструменты",
                                      "Плагины AutoCAD и Metashape, таксационные расчеты",
                                      ft.Icons.BUILD, ft.Colors.ORANGE, self.show_specialized_tools),
            ], wrap=True),
            
            ft.Divider(height=40),
            
            ft.Text("Объекты", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        self.search_field,
                        self.loading_indicator
                    ], spacing=10, expand=True),
                    self.results_container
                ]),
                padding=20,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                margin=ft.margin.only(top=10, bottom=10),
                expand=True
            ),
        ])

    def create_info_card(self, title, description, icon, color, on_click=None):
        """
        Создаёт информационную карточку для раздела.
        :param title: Заголовок
        :param description: Описание
        :param icon: Иконка Flet
        :param color: Цвет иконки
        :param on_click: Обработчик клика
        :return: Flet Card
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=12, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.START),
                padding=20,
                width=250,
                height=180,
                alignment=ft.alignment.top_left,
                on_click=on_click,
                ink=True,
                border_radius=8
            )
        )
    
    def show_documents(self, e=None):
        """
        Показать раздел документов. Вызывает уведомление и может переключить страницу.
        """
        self.show_snack_bar("Переход к документам...")
        # Можно добавить переход к первой функции из категории
        # self.app.show_page('documents')
    
    def show_geodetic_works(self, e=None):
        """
        Показать раздел геодезических работ. Вызывает уведомление и может переключить страницу.
        """
        self.show_snack_bar("Переход к геодезическим работам...")
        # Можно добавить переход к первой функции из категории
        # self.app.show_page('coordinates')
    
    def show_specialized_tools(self, e=None):
        """
        Показать раздел специализированных инструментов. Вызывает уведомление и может переключить страницу.
        """
        self.show_snack_bar("Переход к специализированным инструментам...")
        # Можно добавить переход к первой функции из категории
        # self.app.show_page('autocad')

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

    def project_search(self):
        """
        Запускает поиск по объектам и обновляет UI с результатами.
        """
        results = self.search_service.project_search(self.search_query)
        items = []
        import re
        query_text = self.search_query.strip()
        highlight_re = re.compile(re.escape(query_text), re.IGNORECASE)
        for number, name in results:
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
                    subtitle=ft.Text("Наименование заказчика", size=11, color=ft.Colors.GREY_500),    # TODO: Заказчик
                    on_click=lambda e: self.app.show_project_page(number, name),
                    dense=True,
                )
            )
        if not items:
            self.results_container.content = ft.Text("Ничего не найдено", color=ft.Colors.GREY_500)
        else:
            self.results_container.content = ft.Column(items, scroll=ft.ScrollMode.AUTO, height=350)
        self.loading_indicator.visible = False
        self.page.update()


