import re
import shutil
from pathlib import Path

import flet as ft
from .base_page import BasePage
from ..models.wood_waste_model import Project, Parameters
from ..services.wood_waste_service.table_extraction import ExtractTable
from ..utils.file_utils import FileUtils


class WoodWastePage(BasePage):
    """
    Страница для расчета отходов древесины.
    Позволяет выполнять расчёт отходов при вырубке древесины на основе таксационного плана.
    """
    def __init__(self, app):
        """
        Инициализация главной страницы, создание всех UI-компонентов и переменных состояния.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.project: Project | None = None
        self.parameters = Parameters(root_percentage_wood=0.3, root_percentage_shrub=0.03)
        self.project_field = ft.Row([ft.Text("Создайте или откройте проект", size=14),
                                     ft.IconButton(icon=ft.Icons.FOLDER_OPEN, disabled=True)])
        self.create_project_button = ft.ElevatedButton("Создать проект",
                                                  icon=ft.Icons.CREATE_NEW_FOLDER, icon_color=ft.Colors.BLUE,
                                                  on_click=lambda e: self._show_new_project_name_dialog())
        self.open_project_button = ft.ElevatedButton("Открыть проект",
                                                icon=ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE,
                                                on_click=lambda e: self._open_project())

        self.root_percentage_wood_field = ft.TextField(
            label="Доля корневой системы у дерева",
            value=str(self.parameters.root_percentage_wood),
            autofocus=True,
            on_change=lambda e: (self._validate_root_percentage(e), self._apply_root_percentage_wood_field(e)),
            expand=True
        )
        self.root_percentage_shrub_field = ft.TextField(
            label="Доля корневой системы у кустарника",
            value=str(self.parameters.root_percentage_shrub),
            autofocus=True,
            on_change=lambda e: (self._validate_root_percentage(e), self._apply_root_percentage_wood_field(e)),
            expand=True
        )

        self.parameters_container = ft.Container(content=ft.Column([
            self.root_percentage_wood_field,
            self.root_percentage_shrub_field,
        ]))

        self.containers = ft.Column([])

    def _init_containers(self):
        self.containers.controls.clear()
        self._create_container(name="dxf", title="Исходные DXF файлы")
        self._create_container(name="xls", title="XLS таблицы удаляемых деревьев")
        self._create_container(name="out", title="Выходные таблицы отходов")
        self.page.update()

    def _init_project(self, path: Path):
        self.project = Project(project_path=path, dxf_files=[], xls_files=[], out_files=[])
        for file in (self.project.project_path / "dxf").iterdir():
            if file.is_file() and file.suffix == ".dxf":
                self.project.dxf_files.append(file)
        for file in (self.project.project_path / "xls").iterdir():
            if file.is_file() and file.suffix == ".xlsx":
                self.project.xls_files.append(file)
        for file in (self.project.project_path / "out").iterdir():
            if file.is_file() and file.suffix == ".xlsx":
                self.project.out_files.append(file)
        self._init_containers()

    def _open_project(self):
        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                self._init_project(Path(e.path))
                self.project_field.controls[0].value = self.project.project_path
                self.project_field.controls[1].on_click=lambda _: FileUtils.open_folder(self.project.project_path)
                self.project_field.controls[1].disabled=False
                self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.get_directory_path()

    def _show_new_project_name_dialog(self):

        def validate_project_name(e):
            project_name = project_name_field.value.strip()
            if project_name:
                # Убираем недопустимые символы для имени папки
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    project_name = project_name.replace(char, '_')

                # Убираем множественные пробелы и подчеркивания
                project_name = ' '.join(project_name.split())
                project_name = '_'.join(filter(None, project_name.split('_')))

                project_name_field.value = project_name
                self.page.update()

        project_name_field = ft.TextField(
            label="Имя проекта",
            hint_text="Введите название проекта",
            autofocus=True,
            on_change=validate_project_name,
            expand=True
        )

        def on_submit(e):
            project_name = project_name_field.value.strip()
            if project_name:
                self.page.close(project_name_dialog)
                # После ввода имени проекта открываем диалог выбора папки
                self._show_folder_new_project_picker_dialog(project_name)
            else:
                project_name_field.error_text = "Введите имя проекта"

        def on_cancel(e):
            self.page.close(project_name_dialog)

        project_name_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Создание нового проекта"),
            content=ft.Column([
                ft.Text("Введите название для нового проекта:"),
                project_name_field
            ], width=400, height=150),
            actions=[
                ft.TextButton("Отмена", on_click=on_cancel),
                ft.TextButton("Далее", on_click=on_submit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.open(project_name_dialog)

    def _show_folder_new_project_picker_dialog(self, project_name):
        def on_result(e: ft.FilePickerResultEvent):
            project_path = Path(e.path) / project_name
            if e.path:
                folders = ["dxf", "xls", "out"]
                for folder in folders:
                    (project_path / folder).mkdir(parents=True, exist_ok=True)
                self._init_project(Path(e.path) / project_name)
                self.project_field.controls[0].value = self.project.project_path
                self.project_field.controls[1].on_click=lambda _: FileUtils.open_folder(self.project.project_path)
                self.project_field.controls[1].disabled=False
                self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.get_directory_path()

    def _import_dxf_action(self):
        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                for idx, file in enumerate(e.files):
                    shutil.copy(file.path, self.project.project_path / "dxf" / file.name)
                self._init_project(self.project.project_path)
        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.pick_files(
            allowed_extensions=["dxf"],
            allow_multiple=True
        )

    def _validate_root_percentage(self, e):
        pattern = r'^(?:0(?:\.\d+)?|1(?:\.0+)?)$'
        if re.fullmatch(pattern, e.control.value):
            e.control.error_text = None
        else:
            e.control.error_text = "Введите число с плавающей запятой от 0.0 до 1.0"
        self.page.update()

    def _apply_root_percentage_wood_field(self, e):
        self.parameters.root_percentage_wood = e.control.value

    def _apply_root_percentage_shrub_field(self, e):
        self.parameters.root_percentage_shrub = e.control.value

    def _delete_dxf_action(self):
        pass    # TODO: удаление выделенных dxf файлов

    def _extraction_action(self):
        # FIXME: добавить structure в параметры обработки
        # FIXME: добавить выборочную обработку
        ExtractTable(
            structure=(("A", 'номер'), ("B", 'порода'), ("C", 'количество'), ("D", 'высота'), ("E", 'диаметр')),
            input_dir=self.project.project_path / "dxf", output_dir=self.project.project_path / "xls"
        ).extraction()
        self._init_project(self.project.project_path)

    def _create_container(self, name: str, title: str):
        exception = Exception('В WoodWastePage._create_container() ожидается "dxf", "xls" или "out".')
        match name:
            case "dxf":
                files = self.project.dxf_files
            case "xls":
                files = self.project.xls_files
            case "out":
                files = self.project.out_files
            case _:
                raise exception
        checkboxes = ft.Column([ft.Checkbox(label=file.name, value=True) for file in files])
        def delete_action():
            pass    # TODO: удаление выделенных файлов
        def calculation_action():
            pass    # TODO: расчет отходов
        def get_summary_action():
            pass    # TODO: создание общего файла
        reload_button = ft.IconButton(icon=ft.Icons.WIFI_PROTECTED_SETUP, icon_color=ft.Colors.BLUE,
                                      tooltip="Обновить список файлов",
                                      on_click=lambda e: self._init_project(self.project.project_path))
        upload_dxf_button = ft.IconButton(icon=ft.Icons.FILE_UPLOAD, icon_color=ft.Colors.BLUE,
                                          tooltip="Загрузить DXF файлы", on_click=lambda e: self._import_dxf_action())
        delete_button = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.BLUE,
                                      tooltip="Удалить файлы", on_click=lambda e: delete_action())
        extraction_button = ft.IconButton(icon=ft.Icons.PIVOT_TABLE_CHART, icon_color=ft.Colors.BLUE,
                                          tooltip="Извлечь таблицы", on_click=lambda e: self._extraction_action())
        calculation_button = ft.IconButton(icon=ft.Icons.CALCULATE, icon_color=ft.Colors.BLUE,
                                          tooltip="Рассчитать отходы", on_click=lambda e: calculation_action())
        summary_button = ft.IconButton(icon=ft.Icons.SUMMARIZE, icon_color=ft.Colors.BLUE,
                                          tooltip="Объединить в общий файл", on_click=lambda e: get_summary_action())

        buttons = [reload_button, delete_button]
        match name:
            case "dxf": buttons.append(upload_dxf_button)
            case "xls": buttons.append(extraction_button)
            case "out": buttons.extend([calculation_button, summary_button])
            case _: raise exception

        self.containers.controls.append(ft.Container(content=ft.Column([
            ft.Row([ft.Text(title, weight=ft.FontWeight.BOLD), *buttons]),
            checkboxes,
        ])))
        self.page.update()

    def get_content(self):
        """
        Возвращает содержимое страницы расчета отходов древесины (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Row([
                ft.Text("Расчет отходов древесины", size=24, weight=ft.FontWeight.BOLD),
                ft.Row([self.create_project_button, self.open_project_button]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.project_field,
            ft.Divider(height=20),

            ft.Text("Параметры обработки", size=18, weight=ft.FontWeight.BOLD),
            self.parameters_container,
            ft.Divider(height=20),

            self.containers
        ])
