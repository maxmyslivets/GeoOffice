from typing import Any
from pathlib import Path

import flet as ft

from services.project_service import ProjectService
from utils.file_utils import FileUtils


class AddProjectDialog:
    """
    Компонент для отображения диалога добавления объекта.
    """
    def __init__(self, projects_page) -> None:
        self.app = projects_page.app
        self.page = self.app.page
        self.projects_page = projects_page

        self.project_service = ProjectService(self.app.database_service, self.app.settings)

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Добавление объекта"),
            actions=[
                ft.TextButton("Создать", on_click=self._add_clicked),
                ft.TextButton("Отмена", on_click=self._cancel_clicked),
            ]
        )

        self.radio_group = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="new", label="Создать по шаблону"),
                ft.Radio(value="exist", label="Добавить существующий"),
            ]),
            on_change=self._radiogroup_changed,
        )

        self.name_field = ft.TextField(label="Название объекта", multiline=True, min_lines=2, max_lines=5,
                                       on_change=self._check_name_field)

        self.path_project_text_field = ft.TextField(label="Расположение для папки объекта",
                                                    on_change=self._check_dir,
                                                    expand=True, error_max_lines=2)
        self.path_project_folder_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_size=24,
                                                        tooltip="Выбрать путь",
                                                        on_click=self._select_dir_action)

        self.input_column = ft.Column([
            ft.Row([self.path_project_text_field, self.path_project_folder_button]),
            self.name_field
        ])
        self.radio_group.value = "new"

        self.dlg.content = ft.Column([
            self.radio_group,
            self.input_column,
        ], tight=True, spacing=12, width=400)

    def show(self) -> None:
        self.page.open(self.dlg)
        self.page.update()

    def _cancel_clicked(self, e) -> None:
        self.dlg.open = False
        self.page.update()

    def _add_clicked(self, e) -> None:
        if not self._is_valid():
            self.app.show_error("Проверьте введенные значения")
            return

        try:
            if self.radio_group.value == "new":
                project = self.project_service.create_project(name=self.name_field.value, path=self.path)
            else:
                project = self.project_service.create_project(name=None, path=self.path, exists=True)
            self.app.show_project_page(project.id)
        except Warning as w:
            self.app.show_warning(w)
        except Exception as e:
            self.app.show_error(e)

        self.dlg.open = False
        self.page.update()

    def _radiogroup_changed(self, e) -> None:
        if self.radio_group.value == "new":
            self.dlg.actions[0].text = "Создать"
            self.name_field.disabled = False
            self.path_project_text_field.label = "Расположение для папки объекта"
        else:
            self.dlg.actions[0].text = "Добавить"
            self.name_field.disabled = True
            self.path_project_text_field.label = "Расположение папки объекта"
        self.page.update()

    def _select_dir_action(self, e) -> None:

        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.path_project_text_field.value = e.path
                self._check_dir(e.path)
                self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.get_directory_path()

    def _check_dir(self, e) -> None:
        if Path(self.path_project_text_field.value).is_dir():
            self.path_project_text_field.error_text = None
            try:
                self.path = Path(self.path_project_text_field.value).relative_to(
                    Path(self.app.settings.paths.file_server) / self.project_service.database_service.get_settings_project_dir())
            except ValueError:
                self.path_project_text_field.error_text = "Выберите расположение в папке объектов на файловом сервере"
        else:
            self.path_project_text_field.error_text = "Путь не является папкой"
        self.page.update()

    def _check_name_field(self, e) -> None:
        if FileUtils.is_valid_dirname(self.name_field.value):
            self.name_field.error_text = None
        else:
            if len(self.name_field.value) == 0:
                self.name_field.error_text = "Введите название объекта"
            else:
                self.name_field.error_text = "Название содержит недопустимые для создания папки символы"
        self.page.update()

    def _is_valid(self) -> bool:
        self._check_dir(None)
        validations = [
            len(self.path_project_text_field.value) != 0,
            self.path_project_text_field.error_text is None,
        ]
        if self.radio_group.value == "new":
            validations.append(FileUtils.is_valid_dirname(self.name_field.value))
        return all(validations)
