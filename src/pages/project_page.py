import os

import flet as ft
from pathlib import Path

from .base_page import BasePage
from src.models.project_model import Project
from src.services.project_service import ProjectService
from src.utils.logger_config import log_exception
from ..components.link_section import LinkSection


class ProjectPage(BasePage):
    """
    Динамическая страница проекта.
    Генерируется на основе данных конкретного проекта.
    """

    @log_exception
    def __init__(self, app, project_id: int):
        super().__init__(app)

        self.project_service = ProjectService(app.database_service)

        # Загружаем данные проекта
        self.project = self.project_service.get_project(project_id)
        
        # UI компоненты
        self.project_info_card = None
        self.deadline_card = None
        navigation_panel = None
        tools_panel = None
        documents_list = None

        # self.documents_list = None
        # self.actions_row = None
        # self.status_badge = None
        # self.customer_text = None
        # self.description_text = None
        # self.created_date_text = None
        # self.modified_date_text = None

        self.logger.info(f"Инициализирована страница объекта id={project_id}")

    @log_exception
    def get_content(self):
        """
        Возвращает содержимое страницы проекта (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            # Заголовок страницы
            self.create_header(),
            ft.Divider(height=20),
            self.create_link_section(),
            self.create_project_info_card(),
            self.create_deadline_card(),
        ])

    @log_exception
    def create_header(self):
        """Создание заголовка страницы"""
        return ft.Row([
            ft.Icon(ft.Icons.FOLDER, color=ft.Colors.BLUE, size=32),
            ft.Column([
                ft.Text(f"{self.project.number} {self.project.name}", size=28, weight=ft.FontWeight.BOLD,
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ft.Text(self.project.customer, size=18, color=ft.Colors.GREY_600,
                        overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ft.Text(self.project.chief_engineer, size=18, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD,
                        overflow=ft.TextOverflow.ELLIPSIS, expand=True)
            ], spacing=5, expand=True),
        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    @log_exception
    def create_project_info_card(self):
        """Создание информационной карточки проекта"""
        return ft.Card(content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Информация об объекте", size=20, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Column([
                        ft.Row([ft.Text("Номер", weight=ft.FontWeight.BOLD),
                                ft.SelectionArea(ft.Text(self.project.number))]),
                        ft.Row([ft.Text("Название", weight=ft.FontWeight.BOLD),
                                ft.SelectionArea(ft.Text(self.project.name))]),
                        ft.Row([ft.Text("Заказчик", weight=ft.FontWeight.BOLD),
                                ft.SelectionArea(ft.Text(self.project.customer))]),
                        ft.Row([ft.Text("ГИП", weight=ft.FontWeight.BOLD),
                                ft.SelectionArea(ft.Text(self.project.chief_engineer))]),
                        ft.Row([ft.Text("Местоположение", weight=ft.FontWeight.BOLD),
                                ft.SelectionArea(ft.Text(self.project.address))]),
                    ]),
                    ft.Row([
                        ft.Text("Изменен 04.07.2025 18:48", size=10, color=ft.Colors.GREY),
                        ft.TextButton("Редактировать",
                                      on_click=lambda _: self.app.show_warning("Функция находится в разработке"))
                    ], alignment=ft.MainAxisAlignment.END),
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(left=10, right=10, top=15, bottom=15),
                border_radius=8,
                expand=True
            ), expand=True)     # FIXME: Сделать горизонтальную прокрутку

    def create_link_section(self):
        project_path = self.project.get_path(
            Path(self.app.settings.paths.file_server) / self.app.settings.paths.projects_folder)
        links = [[name, Path(project_path) / name]
                 for name in os.listdir(project_path) if (Path(project_path) / name).is_dir()]
        links.insert(0, [self.project.number, project_path])
        return LinkSection(self.app).create(title="Быстрый доступ", links=links, is_edit=False)

    @log_exception
    def create_deadline_card(self):
        return ft.Card(content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Сроки", size=20, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Column([
                        ft.Text("Заказчику", weight=ft.FontWeight.BOLD),
                        ft.Row([ft.Text("Начало работ", weight=ft.FontWeight.W_600),
                                ft.Text(self.project.created_date.date().strftime("%d.%m.%Y"))]),
                        ft.Row([ft.Text("Предварительные выдачи", weight=ft.FontWeight.W_600),
                                ft.Text(self.project.created_date.date().strftime("%d.%m.%Y")),
                                ft.Text(self.project.created_date.date().strftime("%d.%m.%Y")),]),
                        ft.Row([ft.Text("Итоговая выдача", weight=ft.FontWeight.W_600),
                                ft.Text(self.project.created_date.date().strftime("%d.%m.%Y"))]),
                        ft.Text("Архитектуре", weight=ft.FontWeight.BOLD),
                        ft.Row([ft.Text("Сдать материалы до", weight=ft.FontWeight.W_600),
                                ft.Text(self.project.created_date.date().strftime("%d.%m.%Y"))]),
                        ft.Text("Смежникам", weight=ft.FontWeight.BOLD),
                        ft.Row([ft.Text("ГИПу", weight=ft.FontWeight.W_600),
                                ft.Text(self.project.created_date.date().strftime("%d.%m.%Y"))]),
                    ]),
                    ft.Row([
                        ft.Text("Изменен 04.07.2025 18:48", size=10, color=ft.Colors.GREY),
                        ft.TextButton("Редактировать",
                                      on_click=lambda _: self.app.show_warning("Функция находится в разработке"))
                    ], alignment=ft.MainAxisAlignment.END),
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                padding=ft.padding.only(left=10, right=10, top=15, bottom=15),
                border_radius=8,
                expand=True,
            ))     # FIXME: Сделать горизонтальную прокрутку

    # @log_exception
    # def create_actions_section(self):
    #     """Создание секции действий с проектом"""
    #     return ft.Column([
    #         ft.Text("Действия с проектом", size=18, weight=ft.FontWeight.BOLD),
    #         ft.Row([
    #             ft.ElevatedButton(
    #                 "Редактировать проект",
    #                 icon=ft.Icons.EDIT,
    #                 on_click=self.edit_project
    #             ),
    #             ft.ElevatedButton(
    #                 "Добавить документ",
    #                 icon=ft.Icons.ADD,
    #                 on_click=self.add_document
    #             ),
    #             ft.ElevatedButton(
    #                 "Создать отчет",
    #                 icon=ft.Icons.DESCRIPTION,
    #                 on_click=self.create_report
    #             ),
    #             ft.ElevatedButton(
    #                 "Создать картограмму",
    #                 icon=ft.Icons.MAP,
    #                 on_click=self.create_cartogram
    #             ),
    #         ], wrap=True),
    #     ])

    # @log_exception
    # def create_documents_section(self):
    #     """Создание секции документов проекта"""
    #     documents = self.project_data.documents
    #
    #     if not documents:
    #         documents_content = ft.Column([
    #             ft.Text("Документы отсутствуют", color=ft.Colors.GREY_500, italic=True)
    #         ])
    #     else:
    #         # Группируем документы по типам
    #         doc_types = {}
    #         for doc in documents:
    #             if doc.type not in doc_types:
    #                 doc_types[doc.type] = []
    #             doc_types[doc.type].append(doc)
    #
    #         # Создаем список документов
    #         doc_items = []
    #         for doc_type, docs in doc_types.items():
    #             # Заголовок типа документов
    #             type_icons = {
    #                 "report": ft.Icons.DESCRIPTION,
    #                 "cartogram": ft.Icons.MAP,
    #                 "technical_task": ft.Icons.ASSIGNMENT,
    #                 "coordinates": ft.Icons.LOCATION_ON,
    #                 "other": ft.Icons.INSERT_DRIVE_FILE
    #             }
    #
    #             doc_items.append(
    #                 ft.Container(
    #                     content=ft.Text(
    #                         f"{doc_type.title()} ({len(docs)})",
    #                         size=16,
    #                         weight=ft.FontWeight.BOLD
    #                     ),
    #                     padding=ft.padding.only(top=10, bottom=5)
    #                 )
    #             )
    #
    #             # Документы данного типа
    #             for doc in docs:
    #                 doc_items.append(
    #                     ft.ListTile(
    #                         leading=ft.Icon(type_icons.get(doc.type, ft.Icons.INSERT_DRIVE_FILE)),
    #                         title=ft.Text(doc.name),
    #                         subtitle=ft.Text(
    #                             f"{doc.get_formatted_size()} • {doc.modified_date.strftime('%d.%m.%Y')}"
    #                         ),
    #                         trailing=ft.PopupMenuButton(
    #                             icon=ft.Icons.MORE_VERT,
    #                             item_builder=lambda doc=doc: [
    #                                 ft.PopupMenuItem(
    #                                     text="Открыть",
    #                                     icon=ft.Icons.OPEN_IN_NEW,
    #                                     on_click=lambda e, d=doc: self.open_document(d)
    #                                 ),
    #                                 ft.PopupMenuItem(
    #                                     text="Удалить",
    #                                     icon=ft.Icons.DELETE,
    #                                     on_click=lambda e, d=doc: self.delete_document(d)
    #                                 ),
    #                             ]
    #                         ),
    #                         dense=True,
    #                     )
    #                 )
    #
    #         documents_content = ft.Column(doc_items, spacing=5)
    #
    #     return ft.Column([
    #         ft.Row([
    #             ft.Text("Документы проекта", size=18, weight=ft.FontWeight.BOLD),
    #             ft.Text(f"({len(documents)})", color=ft.Colors.GREY_600),
    #         ]),
    #         ft.Container(
    #             content=ft.Column(
    #                 controls=documents_content.controls,
    #                 scroll=ft.ScrollMode.AUTO,
    #                 height=300
    #             ),
    #             padding=10,
    #             bgcolor=ft.Colors.GREY_50,
    #             border_radius=8,
    #         )
    #     ])
    
    # # Обработчики событий
    # def edit_project(self, e=None):
    #     """Редактирование проекта"""
    #     self.show_snack_bar("Функция редактирования проекта в разработке")
    #
    # def add_document(self, e=None):
    #     """Добавление документа к проекту"""
    #     self.show_snack_bar("Функция добавления документа в разработке")
    #
    # def create_report(self, e=None):
    #     """Создание отчета для проекта"""
    #     self.app.show_page('documents')
    #     self.show_snack_bar("Переход к созданию отчета")
    #
    # def create_cartogram(self, e=None):
    #     """Создание картограммы для проекта"""
    #     self.app.show_page('cartogram')
    #     self.show_snack_bar("Переход к созданию картограммы")
    #
    # def open_document(self, document: ProjectDocument):
    #     """Открытие документа"""
    #     self.show_snack_bar(f"Открытие документа: {document.name}")
    #
    # def delete_document(self, document: ProjectDocument):
    #     """Удаление документа"""
    #     if self.project_service.remove_document_from_project(self.project_number, document.name):
    #         self.show_snack_bar(f"Документ {document.name} удален")
    #         # Обновляем страницу
    #         self.load_project_data()
    #         self.update_page()
    #     else:
    #         self.show_error("Ошибка удаления документа")
    #
    # def go_home(self, e=None):
    #     """Возврат на главную страницу"""
    #     self.app.show_home_page()