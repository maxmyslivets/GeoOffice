from typing import Any
from pathlib import Path

import flet as ft

from utils.file_utils import FileUtils


class AddProjectDialog:
    """
    Компонент для отображения диалога добавления объекта.
    """
    def __init__(self, app) -> None:
        self.app = app
        self.page = app.page

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

        self.number_field = ft.TextField(label="Номер объекта", on_change=self._check_number_field)
        self.name_field = ft.TextField(label="Название объекта", multiline=True, min_lines=2, max_lines=5,
                                       on_change=self._check_name_field)

        self.path_project_text_field = ft.TextField(label="Расположение папки объекта",
                                                    on_change=self._check_dir,
                                                    expand=True, error_max_lines=2)
        self.path_project_folder_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_size=24,
                                                        tooltip="Выбрать путь",
                                                        on_click=self._select_dir_action)

        self.input_column = ft.Column([])
        self.radio_group.value = "new"
        self._set_input_column_new()

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

        if self.radio_group.value == "new":
            # project = self.app.project_service.create_project()     # TODO: реализовать в create_project() копирование шаблонной
            #                                                         #  папки и добавление в базу данных
            print(self.number_field.value)
            print(self.name_field.value)
            print(self.path)
        else:
            # project = self.app.project_service.add_project()    # TODO: реализовать в add_project() расшифровку номера
            #                                                     #  и имени объекта из имени папки, сделать присвоение
            #                                                     #  uid в файл проекта и базу данных
            print(self.path)

        self.dlg.open = False
        self.page.update()

        # self.app.show_project_page(project.id)

    def _set_input_column_new(self) -> None:
        self.input_column.controls = [
            self.number_field,
            self.name_field,
            ft.Row([self.path_project_text_field, self.path_project_folder_button])
        ]

    def _set_input_column_exist(self) -> None:
        self.input_column.controls = [
            ft.Row([self.path_project_text_field, self.path_project_folder_button])
        ]

    def _radiogroup_changed(self, e) -> None:
        if self.radio_group.value == "new":
            self.dlg.actions[0].text = "Создать"
            self._set_input_column_new()
        else:
            self.dlg.actions[0].text = "Добавить"
            self._set_input_column_exist()
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
                    self.app.settings.paths.get_projects_pathdir())
            except ValueError:
                self.path_project_text_field.error_text = "Выберите расположение в папке объектов на файловом сервере"
        else:
            self.path_project_text_field.error_text = "Путь не является папкой"
        self.page.update()

    def _check_number_field(self, e) -> None:
        if FileUtils.is_valid_dirname(self.number_field.value):
            self.number_field.error_text = None
        else:
            if len(self.number_field.value) == 0:
                self.number_field.error_text = "Введите номер объекта"
            else:
                self.number_field.error_text = "Номер содержит недопустимые для создания папки символы"
        self.page.update()

    def _check_name_field(self, e) -> None:
        if FileUtils.is_valid_dirname(self.name_field.value):
            self.name_field.error_text = None
        else:
            if len(self.number_field.value) == 0:
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
            validations.append(FileUtils.is_valid_dirname(self.number_field.value + " " + self.name_field.value))
        return all(validations)
