import re
from pathlib import Path

import flet as ft

from .base_page import BasePage
from components.banners import BannerDiffProjects
from services.project_service import ProjectService
from utils.logger_config import log_exception


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
        self.results_list = None
        self.loading_indicator = None
        self.search_field = None
        self.project_service = ProjectService(self.app.database_service)

        # Пагинация/ленивая загрузка
        self._all_results: list[tuple] = []  # (project_id, number, name, customer)
        self._loaded_count: int = 0
        self._page_size: int = 100
        self._max_controls: int = 600  # ограничение числа одновременно отрисованных элементов
        self._is_loading_page: bool = False
        self._current_search_id: int = 0

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

        # Контейнер результатов теперь ListView с прокруткой
        self.results_list = ft.ListView(
            expand=True,
            spacing=0,
            padding=0,
            auto_scroll=False,
            on_scroll=self._on_results_scroll,
        )
        self.results_container = ft.Container(content=self.results_list, expand=True)

        return ft.Column([
            ft.Row([
                ft.Text("Поиск по объектам", size=20, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        icon=ft.Icons.SYNC,
                        text="Проверить базу данных",
                        on_click=lambda e: self.start_diff_project(),
                    ),
                    ft.ElevatedButton(
                        icon=ft.Icons.ADD,
                        text="Добавить объект",
                        on_click=lambda e: self.start_diff_project(),
                    ),
                ], alignment=ft.MainAxisAlignment.END),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                self.search_field,
                self.loading_indicator
            ], spacing=10, expand=True),
            self.results_container,
        ], expand=True)

    @log_exception
    def post_show(self):
        self.project_search()
        self.page.update()

    @log_exception
    def on_query_change(self, e):
        """
        Обработчик изменения строкипоиска.
        """
        self.search_query = e.control.value
        self.results_container.content = ft.Text("Поиск...", color=ft.Colors.GREY_500)
        self.page.update()
        # Увеличиваем идентификатор поиска и запускаем новый
        self._current_search_id += 1
        self.project_search()

    @log_exception
    def _render_items(self, items: list[tuple]) -> list[ft.Control]:
        controls: list[ft.Control] = []
        query_text = self.search_query.strip()
        highlight_re = re.compile(re.escape(query_text), re.IGNORECASE) if query_text else None
        for project_id, number, name, customer in items:
            text = f"{number} {name}"
            icon = ft.Icons.DESCRIPTION
            display_name = []
            if highlight_re:
                last = 0
                for m in highlight_re.finditer(text):
                    if m.start() > last:
                        display_name.append(ft.Text(text[last:m.start()]))
                    display_name.append(
                        ft.Text(text[m.start():m.end()], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE))
                    last = m.end()
                if last < len(text):
                    display_name.append(ft.Text(text[last:]))
                if not display_name:
                    display_name = [ft.Text(text)]
            else:
                display_name = [ft.Text(text)]

            controls.append(
                ft.ListTile(
                    leading=ft.Icon(icon, color=ft.Colors.GREY_700),
                    title=ft.Row(display_name, spacing=0),
                    subtitle=ft.Text(customer, size=11, color=ft.Colors.GREY_500),
                    on_click=lambda e, pid=project_id: self.app.show_project_page(pid),
                    dense=True,
                )
            )
        return controls

    @log_exception
    def _reset_results(self):
        self._all_results = []
        self._loaded_count = 0
        if isinstance(self.results_container.content, ft.ListView):
            self.results_container.content.controls.clear()
        else:
            self.results_container.content = self.results_list
        self.page.update()

    @log_exception
    def _load_next_page(self):
        if self._loaded_count >= len(self._all_results):
            return
        if self._is_loading_page:
            return
        self._is_loading_page = True
        end = min(self._loaded_count + self._page_size, len(self._all_results))
        batch = self._all_results[self._loaded_count:end]
        new_controls = self._render_items(batch)
        self.results_list.controls.extend(new_controls)
        self._loaded_count = end

        # Ограничиваем число отрисованных элементов
        if len(self.results_list.controls) > self._max_controls:
            trim = len(self.results_list.controls) - self._max_controls
            del self.results_list.controls[:trim]
        self._is_loading_page = False
        self.page.update()

    @log_exception
    def _on_results_scroll(self, e: ft.OnScrollEvent):
        # Если докрутили до низа — догружаем следующую порцию (с защитой от повторных вызовов)
        if e.pixels is not None and e.max_scroll_extent is not None:
            near_bottom = (e.max_scroll_extent - e.pixels) < 200
            if near_bottom and not self._is_loading_page:
                self._load_next_page()

    @log_exception
    def project_search(self):
        """
        Запускает поиск по объектам и обновляет UI с результатами.
        """
        self.loading_indicator.visible = True
        self.page.update()

        empty_result_text = ft.Text("Ничего не найдено")

        if not self.app.database_service.connected:
            self.results_container.content = empty_result_text
            self.app.show_error("База данных не подключена")
            self.loading_indicator.visible = False
            self.page.update()
        else:
            # Останавливаем предыдущую задачу поиска, если она ещё выполняется
            if "project_search" in self.app.background_service.get_tasks().keys():
                self.app.background_service.stop_task("project_search")

            # Снимок текущего идентификатора поиска
            search_id = self._current_search_id

            # Очистим предыдущие результаты сразу, чтобы не мелькали старые
            self._reset_results()

            def task(progress, stop_event):
                return self.app.database_service.search_project(self.search_query, sorted_from_modified_date=True)

            def on_complete(results: list):
                # Игнорируем устаревший результат
                if search_id != self._current_search_id:
                    return
                self._reset_results()
                if len(results) > 0:
                    self._all_results = results
                    # Рендерим первую страницу
                    self._load_next_page()
                    self.results_container.content = self.results_list
                else:
                    self.results_container.content = empty_result_text
                self.loading_indicator.visible = False
                self.page.update()

            def on_cancel():
                # Игнорируем устаревшую отмену
                if search_id != self._current_search_id:
                    return
                self.results_container.content = empty_result_text
                self.loading_indicator.visible = False
                self.page.update()
                self.app.show_warning("Проверка прервана пользователем")

            # Используем диалог без прогресса для переноса вычислений в поток
            self.app.background_dialog_runner.run(
                task_name="project_search",
                task_func=task,
                show_progress=False,
                on_cancel=on_cancel,
                on_complete=on_complete,
            )

    @log_exception
    def show_diff_projects_result(self, only_in_files, only_in_database):

        # TODO: перенести ui результата сравнения проектов в компоненты;
        #  при нажатии на кнопку действия при необходимости раскрывать элемент списка для ввода данных,
        #  т.к. при попытке вызова дополнительного диалога, исходный диалог закрывается;
        #  также предусмотреть сокращение списка при решении проблемы.
        #  Продумать возможность замены диалога на временную боковую панель для
        #  возможности параллельного редактирования проектов и контроля списка сравнения

        def find_exist(text):
            self.page.close(dlg)
            self.search_field.value = Path(text).name
            self.results_container.content = ft.Text("Ничего не найдено", color=ft.Colors.GREY_500)
            self.page.update()

        def show_exist(text):
            project_id = self.app.database_service.get_project_from_path(text).id
            self.page.close(dlg)
            if project_id is None:
                self.app.show_error(f"Объект с расположением `{text}` не найден в базе данных. "
                                    f"Попробуйте найти вручную через поиск объектов.")
            self.app.show_project_page(project_id)

        def delete_exist(text):
            project_id = self.app.database_service.get_project_from_path(text).id
            self.page.close(dlg)
            if project_id is None:
                self.app.show_error(f"Объект с расположением `{text}` не найден в базе данных. "
                                    f"Попробуйте найти вручную через поиск объектов.")
            # self.app.project_service.delete_project(project_id)   # TODO: допилить метод `project_service.delete_project`
            self.app.show_warning("Функция в разработке")

        def add_exist(text):
            try:
                path = Path(text)
                folder_name = path.name
                number, name = folder_name.split(" ")[0], " ".join(folder_name.split(" ")[1:])
                customer = chief_engineer = status = address = "Не указано"
                project = self.project_service.add_project(number, name, customer, chief_engineer, status, address, path)
                self.app.show_info(f"Объект \"{project.number} {project.name}\" успешно добавлен в базу данных")
            except Exception as e:
                self.app.show_error(f"Ошибка при добавлении объекта: {e}")
                raise e

        content = ft.Container(
            content = ft.Column([
                ft.Column([
                    ft.Text("Нет в базе данных", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Если объект ранее не находился в базе данных, необходимо создать проект объекта.\n"
                            "Если в файловой системе изменился путь к папке объекта, необходимо перейти на страницу "
                            "объекта и изменить путь к папке.", size=14, weight=ft.FontWeight.W_200),
                ]),
                ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DESCRIPTION),
                        title=ft.Text(text),
                        trailing=ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.Icons.ADD,
                                    text="Добавить в базу данных",
                                    on_click=lambda e, t=text: add_exist(t)
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.Icons.EDIT,
                                    text="Изменить существующий",
                                    on_click=lambda e, t=text: find_exist(t)
                                ),
                            ]
                        )
                    )
                    for text in only_in_files
                ] if len(only_in_files) > 0 else [ft.ListTile(title=ft.Text("..."))]),
                ft.Column([
                    ft.Text("Нет в файловой системе", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Если объект есть в базе данных, но в файловой системе путь к нему изменился, необходимо "
                            "перейти на страницу объекта и изменить путь к папке.\n"
                            "Если объект был удален из файловой системы, то необходимо перейти на страницу объекта "
                            "и удалить объект из базы данных.", size=14, weight=ft.FontWeight.W_200),
                ]),
                ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.DESCRIPTION),
                        title=ft.Text(text),
                        trailing=ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.Icons.ADD,
                                    text="Изменить существующий",
                                    on_click=lambda e, t=text: show_exist(t)
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.Icons.DELETE,
                                    text="Удалить из базы данных",
                                    on_click=lambda e, t=text: delete_exist(t)
                                ),
                            ]
                        )
                    )
                    for text in only_in_database
                ] if len(only_in_database) > 0 else [ft.ListTile(title=ft.Text("..."))]),
            ], scroll=ft.ScrollMode.AUTO, expand=True),
        )
        dlg = ft.AlertDialog(content=content,)
        self.page.open(dlg)

    @log_exception
    def start_diff_project(self):
        """Запуск сравнения проектов с отображением прогресса и возможностью отмены"""
        # Останавливаем предыдущую задачу, если она существует
        if "diff_projects" in self.app.background_service.get_tasks().keys():
            self.app.background_service.stop_task("diff_projects")

        projects_root = Path(self.app.settings.paths.file_server) / self.app.settings.paths.projects_folder

        def task(progress, stop_event):
            return self.project_service.diff_projects_with_progress(projects_root, progress, stop_event)

        def on_complete(diff: dict):
            if diff is None:
                return
            count_only_in_files = len(diff.get("only_in_files", []))
            count_only_in_database = len(diff.get("only_in_database", []))
            text = "Требуется обновление базы данных."
            if (count_only_in_files + count_only_in_database) > 0:
                if count_only_in_files > 0:
                    text += f"\nНет в базе данных: {count_only_in_files}"
                if count_only_in_database > 0:
                    text += f"\nНет в файловой системе: {count_only_in_database}"
                banner = BannerDiffProjects(self.app)
                banner.create(text,
                              {
                                  "Обновить": lambda e: (
                                      banner.close_banner(e),
                                      self.show_diff_projects_result(diff["only_in_files"], diff["only_in_database"])
                                  ),
                                  "Отмена": banner.close_banner
                              })
                banner.show()
            else:
                self.app.show_info("База данных актуальна")

        self.app.background_dialog_runner.run(
            task_name="Проверка различий проектов",
            task_func=task,
            show_progress=True,
            on_cancel=lambda: self.app.show_warning("Проверка прервана пользователем"),
            on_complete=on_complete,
        )
