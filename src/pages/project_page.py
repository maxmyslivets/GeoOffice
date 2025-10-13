import os

import flet as ft
from pathlib import Path

from .base_page import BasePage
from models.project_model import ProjectModel
from services.project_service import ProjectService
from utils.logger_config import log_exception
from components.link_section import LinkSection


class ProjectPage(BasePage):
    """
    Динамическая страница проекта.
    Генерируется на основе данных конкретного проекта.
    """

    @log_exception
    def __init__(self, app, project_id: int):
        super().__init__(app)

        self.project_service = ProjectService(app.database_service, app.settings)

        # Загружаем данные проекта
        self.project = self.project_service.get_project(project_id)
        
        # UI компоненты
        self.header = self.create_header()
        self.link_section = self.create_link_section()
        self.project_info_container = self.create_project_info_container()
        self.deadline_container = self.create_deadline_container()

        self.logger.info(f"Инициализирована страница объекта id={project_id}")

    @log_exception
    def get_content(self):
        """
        Возвращает содержимое страницы проекта (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            # Заголовок страницы
            self.header,
            ft.Divider(height=20),
            self.link_section,
            self.project_info_container,
            self.deadline_container,
        ])

    @log_exception
    def create_header(self):
        """Создание заголовка страницы"""
        return ft.Row([
            ft.Column([
                ft.Text(f"{self.project.number} {self.project.name}", size=28, weight=ft.FontWeight.BOLD,
                        max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ft.Text(self.project.customer, size=18, color=ft.Colors.GREY_600,
                        overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ft.Text(self.project.chief_engineer, size=18, color=ft.Colors.GREY_600, weight=ft.FontWeight.BOLD,
                        overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                ft.Row([ft.Text(self.project.modified_date.strftime('Изм. %a, %d %B %Y, %H:%M:%S'), size=10,
                                color=ft.Colors.GREY),], alignment=ft.MainAxisAlignment.END),
            ], spacing=5, expand=True),
        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    def create_link_section(self):
        project_path = self.project.get_path(
            Path(self.app.settings.paths.file_server) / self.project_service.database_service.get_settings_project_dir())
        try:
            links = [[name, Path(project_path) / name]
                     for name in os.listdir(project_path) if (Path(project_path) / name).is_dir()]
        except FileNotFoundError as e:
            self.app.show_warning(e)
            links = []
        links.insert(0, [self.project.number, project_path])
        link_section = LinkSection(self.app).create(title="Быстрый доступ", links=links, is_edit=False)
        return link_section

    @log_exception
    def create_project_info_container(self):
        """Создание информационной карточки проекта"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Информация об объекте", size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Column([
                    ft.Row([ft.Text("Номер", weight=ft.FontWeight.BOLD), ft.Text(self.project.number)]),
                    ft.Row([ft.Text("Название", weight=ft.FontWeight.BOLD), ft.Text(self.project.name)]),
                    ft.Row([ft.Text("Заказчик", weight=ft.FontWeight.BOLD), ft.Text(self.project.customer)]),
                    ft.Row([ft.Text("ГИП", weight=ft.FontWeight.BOLD), ft.Text(self.project.chief_engineer)]),
                    ft.Row([ft.Text("Местоположение", weight=ft.FontWeight.BOLD), ft.Text(self.project.address)]),
                ]),
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.only(left=10, right=10, top=15, bottom=15),
            border_radius=8,
            ink=True,
            on_click=lambda _: self.edit_project_info_container(),
        )

    @log_exception
    def edit_project_info_container(self):
        old_content = self.project_info_container.content
        old_click = self.project_info_container.on_click
        old_border = self.project_info_container.border
        def save():
            self.project.number = tf_number.value
            self.project.name = tf_name.value
            self.project.customer = tf_customer.value
            self.project.chief_engineer = tf_chief_engineer.value
            self.project.address = tf_address.value
            self.project_service.update_project_in_database(self.project)
            self.project_info_container.content = old_content
            self.project_info_container.on_click = old_click
            self.project_info_container.border = old_border
            self.update_page()
            self.app.show_project_page(self.project.id)

        tf_number = ft.TextField(label="Номер", value=self.project.number)
        tf_name = ft.TextField(label="Название", value=self.project.name, max_lines=5)
        tf_customer = ft.TextField(label="Заказчик", value=self.project.customer, max_lines=5)
        tf_chief_engineer = ft.TextField(label="ГИП", value=self.project.chief_engineer)
        tf_address = ft.TextField(label="Местоположение", value=self.project.address, max_lines=5)

        self.project_info_container.on_click=None
        self.project_info_container.content = ft.Column([
            ft.Row([ft.Text("Информация об объекте", size=20, weight=ft.FontWeight.BOLD)]),
            ft.Column([tf_number, tf_name, tf_customer, tf_chief_engineer, tf_address]),
            ft.Row([ft.TextButton("Сохранить", on_click=lambda _: save())],
                   alignment=ft.MainAxisAlignment.END)], spacing=10, alignment=ft.MainAxisAlignment.START)
        self.project_info_container.border = ft.border.all(1, ft.Colors.GREY_500)
        self.update_page()


    @log_exception
    def create_deadline_container(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Сроки", size=20, weight=ft.FontWeight.BOLD),
                ]),
                ft.Column([
                    ft.Text("Заказчику", weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Text("Начало работ", weight=ft.FontWeight.W_600),
                            ft.Text("не указан")]),
                    ft.Row([ft.Text("Предварительные выдачи", weight=ft.FontWeight.W_600),
                            ft.Text("не указан"),
                            ft.Text("не указан"),]),
                    ft.Row([ft.Text("Итоговая выдача", weight=ft.FontWeight.W_600),
                            ft.Text("не указан")]),
                    ft.Text("Архитектуре", weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Text("Сдать материалы до", weight=ft.FontWeight.W_600),
                            ft.Text("не указан")]),
                    ft.Text("Смежникам", weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Text("ГИПу", weight=ft.FontWeight.W_600),
                            ft.Text("не указан")]),
                ]),
                ft.Row([
                    ft.TextButton("Редактировать",
                                  on_click=lambda _: self.app.show_warning("Функция находится в разработке"))
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.only(left=10, right=10, top=15, bottom=15),
            border_radius=8,
            expand=True,
        )     # FIXME: Сделать горизонтальную прокрутку

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