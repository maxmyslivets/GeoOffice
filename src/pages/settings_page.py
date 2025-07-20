from pathlib import Path
from typing import Any

import flet as ft
from datetime import datetime
from .base_page import BasePage


class SettingsPage(BasePage):
    """
    Страница настроек приложения.
    Позволяет управлять автосохранением, темой, экспортом/импортом данных и сбросом настроек.
    """

    def _select_dir_action(self, obj: Any, parameter: str) -> None:
        """Добавляет новую директорию в закрепленные"""

        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                obj.value = e.path
                self._save_parameter(parameter, e.path)

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.get_directory_path()

    def _save_parameter(self, parameter: str, value: str | int | float) -> None:
        match parameter:
            case 'file_server':
                self.app.settings.paths.file_server = value
            case 'projects_folder':
                self.app.settings.paths.projects_folder = value
        self.app.save_settings()
        self.page.update()
    
    def get_content(self):
        """
        Возвращает содержимое страницы настроек (UI).
        :return: Flet Column с элементами интерфейса
        """
        # Настройки интерфейса
        interface_is_last_page_switch = ft.Switch(
            label='Запоминать последнюю открытую страницу',
            value=True,
            # on_change=self._select_dir_action,  # TODO
        )
        interface_is_position_and_size_switch = ft.Switch(
            label='Запоминать положение и размер окна',
            value=True,
            # on_change=self._select_dir_action,  # TODO
        )
        # Выбор файлового сервера
        paths_file_server_text_field = ft.TextField(label="Файловый сервер", value=self.app.settings.paths.file_server,
                                                    expand=True)
        paths_file_server_text_field.on_submit = lambda _: self._save_parameter('file_server', paths_file_server_text_field.value)
        paths_file_server_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE, icon_size=24,
                                                 tooltip="Выбрать путь",
                                                 on_click=lambda e: self._select_dir_action(paths_file_server_text_field, 'file_server'))
        # Выбор папки проектов
        paths_projects_folder_text_field = ft.TextField(label="Папка объектов",
                                                        value=self.app.settings.paths.projects_folder,
                                                        expand=True)
        paths_projects_folder_text_field.on_submit = lambda _: self._save_parameter('projects_folder', paths_file_server_text_field.value)
        paths_projects_folder_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE, icon_size=24,
                                                     tooltip="Выбрать путь",
                                                     on_click=lambda e: self._select_dir_action(paths_projects_folder_text_field, 'projects_folder'))
        return ft.Column([
            ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Text("О программе", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("GeoOffice v0.0.0"),  # TODO: разобраться с версионированием
            ft.Text("Ведение документации по объектам и геодезические расчеты"),
            ft.Text(f"Автор: Мысливец Максим"),
            ft.Divider(height=20),
            
            ft.Column([
                ft.Text("Настройки интерфейса", size=18, weight=ft.FontWeight.BOLD),
                interface_is_last_page_switch,
                interface_is_position_and_size_switch,
            ]),

            ft.Column([
                ft.Text("Настройки путей", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([paths_file_server_text_field, paths_file_server_button]),
                ft.Row([paths_projects_folder_text_field, paths_projects_folder_button]),
            ]),

            # ...

            ft.ElevatedButton("Сброс настроек", icon=ft.Icons.RESTORE, on_click=self.reset_settings),
        ])
    
    def reset_settings(self, e=None):
        """
        Сброс настроек приложения к значениям по умолчанию.
        :param e: Событие нажатия кнопки
        """
        self.app.settings.init_default_settings()
        self.app.save_settings()
        self.app.show_info("Выполнен сброс настроек приложения к значениям по умолчанию")
