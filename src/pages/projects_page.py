import sys
from pathlib import Path

import flet as ft

from .base_page import BasePage
from ..components.banners import BannerDiffProjects
from ..services.background_service import BackgroundService
from ..services.project_service import ProjectService
from ..utils.logger_config import log_exception

sys.path.append("..")


class ProjectsPage(BasePage):
    """Страница приложения GeoOffice. Содержит функционал поиска и создания проектов."""

    def __init__(self, app):
        """
        Инициализация страницы.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.page = None
        self.search_query = ""
        self.results_container = None
        self.loading_indicator = None
        self.search_field = None
        self.project_service = ProjectService(app.database_service)
        # Получаем или создаем BackgroundService
        # if not hasattr(app, 'background_service'):
        #     app.background_service = BackgroundService()
        # self.start_periodic_diff()

    def get_content(self):
        """
        Формирует и возвращает содержимое главной страницы (UI-компоненты Flet).
        :return: Flet Column с элементами интерфейса
        """
        self.page = self.app.page
        # Сбрасываем поисковой запрос
        self.search_query = ""
        if self.search_field:
            self.search_field.value = ""
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
            content=ft.Text("Результаты поиска появятся здесь..."),
            # padding=10,
            # border_radius=8,
            # margin=ft.margin.only(top=10)
        )
        self.project_search(empty_search=True)
        return ft.Column([
            ft.Text("Поиск по объектам", size=20, weight=ft.FontWeight.BOLD),
            # ft.Container(
            #     content=ft.Column([
            #         ft.Row([
            #             self.search_field,
            #             self.loading_indicator
            #         ], spacing=10, expand=True),
            #         self.results_container
            #     ]),
            #     padding=20,
            #     border_radius=8,
            #     margin=ft.margin.only(top=10, bottom=10),
            #     expand=True
            # )
            ft.Row([
                self.search_field,
                self.loading_indicator
            ], spacing=10, expand=True),
            self.results_container,
        ])

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
                    on_click=lambda e, pid=project_id: self.app.show_project_page(pid),
                    dense=True,
                    bgcolor=ft.Colors.BLUE_50
                )
            )
        if not items:
            self.results_container.content = ft.Text("Ничего не найдено", color=ft.Colors.GREY_500)
        else:
            self.results_container.content = ft.Column(
                items,
                scroll=ft.ScrollMode.AUTO,
                # height=400,
            )
        self.loading_indicator.visible = False
        self.page.update()

    # @log_exception
    # def diff_projects(self):
    #     """
    #     Запускает процесс сравнения проектов в файловой системе и проектов из базы данных.
    #     """
    #
    #     diff = self.project_service.diff_projects(
    #         Path(self.app.settings.paths.file_server) / self.app.settings.paths.projects_folder)
    #     count_only_in_files = len(diff["only_in_files"])
    #     count_only_in_database = len(diff["only_in_database"])
    #     text = "Требуется обновление базы данных."
    #     if (count_only_in_files + count_only_in_database) > 0:
    #         if count_only_in_files > 0:
    #             text += f"\nНайдено новых объектов: {count_only_in_files}"
    #         if count_only_in_database > 0:
    #             text += f"\nУдалено объектов: {count_only_in_database}"
    #         banner = BannerDiffProjects(self.app)
    #         banner.create(text,
    #                       {
    #                           "Обновить": lambda e: (
    #                               banner.close_banner(e),
    #                               self.app.show_error("Функция в разработке")  # TODO: Заглушка
    #                           ),
    #                           "Отложить обновление": banner.close_banner
    #                       })
    #         banner.show()
    #
    # @log_exception
    # def start_periodic_diff(self):
    #     """Запуск периодической проверки проектов через BackgroundService"""
    #     # Останавливаем предыдущую задачу, если она существует
    #     self.app.background_service.stop_task("diff_projects")
    #
    #     # Запускаем новую задачу
    #     self.app.background_service.start_periodic_task(
    #         task_name="diff_projects",
    #         task_func=self.diff_projects,
    #         initial_delay=5,  # до первого запуска
    #         interval=30 * 60  # между запусками
    #     )
