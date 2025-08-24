from pathlib import Path

import flet as ft

from src.utils.file_utils import FileUtils


class LinkSection:
    """
    Компонент для отображения статистики использования функций приложения.
    Позволяет отслеживать, какие разделы наиболее востребованы пользователями.
    """

    def __init__(self, app):
        """
        Инициализация компонента статистики использования.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        self.page = app.page
        self.link_section: ft.Container | None = None

    def create(self, title: str, links: list[list[Path | str]], is_edit: bool) -> ft.Container:
        if is_edit:
            buttons = [*[self._create_fab(text, path) for text, path in links],
                       ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.BLUE, icon_size=20,
                                     tooltip="Добавить папку", on_click=lambda e: self._add_link())]
        else:
            buttons = [self._create_fab(text, path, context_menu=False) for text, path in links]
        self.link_section = ft.Container(
            content=ft.Column([
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                ft.Row([*buttons], spacing=10, wrap=True, alignment=ft.MainAxisAlignment.START)
            ]), padding=15, border_radius=8, expand=True)
        return self.link_section

    def _create_fab(self, text, path, context_menu=True):
        def on_right_click(e):
            def remove_from_favorites(e):
                """Удаляет папку из избранного"""
                self.app.settings.remove_favorite_folder(text, path)
                self.app.save_settings()
                buttons = self.link_section.content.controls[-1].controls
                buttons.remove(fab_with_context)
                self.page.close(dialog)
                self.page.update()

            def edit(e):
                """Переименовывает ссылку папки"""

                def save(e):
                    new_name = dialog_rename.content.controls[0].value
                    new_path = dialog_rename.content.controls[1].value
                    if new_name == "" or new_path == "":
                        self.app.show_error("Пустое поле")
                        return
                    self.app.settings.edit_favorite_folder([text, path], [new_name, new_path])
                    self.app.save_settings()
                    buttons: list = self.link_section.content.controls[-1].controls
                    index = buttons.index(fab_with_context)
                    buttons.remove(fab_with_context)
                    buttons.insert(index, self._create_fab(new_name, new_path))
                    self.page.close(dialog_rename)
                    self.page.update()

                dialog_rename = ft.AlertDialog(
                    title=ft.Text("Изменение ярлыка", width=400),
                    content=ft.Column([
                        ft.TextField(label="Название...", on_submit=save, value=text),
                        ft.TextField(label="Путь...", on_submit=save, value=path),
                        ft.Row([
                            ft.TextButton("Сохранить", on_click=save),
                            ft.TextButton("Отмена", on_click=lambda _: self.page.close(dialog_rename))
                        ])
                    ], tight=True)
                )
                self.page.open(dialog_rename)

            dialog = ft.AlertDialog(
                title=ft.Text("Действия"),
                content=ft.Column([
                    ft.TextButton("Изменить", on_click=edit),
                    ft.TextButton("Удалить", on_click=remove_from_favorites),
                    ft.TextButton("Отмена", on_click=lambda _: self.page.close(dialog))
                ], tight=True),
            )
            self.page.open(dialog)

        def open_folder(e):
            if not Path(path).exists():
                self.app.show_error(f"Директория '{path}' была изменена или удалена.")
                return
            FileUtils.open_folder(path)

        fab = ft.FloatingActionButton(text=text, on_click=open_folder,
                                      icon=ft.Icons.FOLDER)
        fab_with_context = ft.GestureDetector(content=fab, on_secondary_tap=on_right_click)
        return fab_with_context if context_menu else fab

    def _add_link(self) -> None:
        """Добавляет новую директорию в закрепленные"""

        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                dir_name = Path(e.path).name
                # Добавляем в настройки
                self.app.settings.add_favorite_folder(dir_name, e.path)
                self.app.save_settings()
                buttons = self.link_section.content.controls[-1].controls
                buttons.insert(-1, self._create_fab(dir_name, e.path))
                # Обновляем интерфейс
                self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.get_directory_path()
