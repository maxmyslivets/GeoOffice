import traceback
from pathlib import Path
from typing import Any

import flet as ft
from datetime import datetime

from services.database_service import DatabaseService
from .base_page import BasePage


class SettingsPage(BasePage):
    """
    Страница настроек приложения.
    Позволяет управлять автосохранением, темой, экспортом/импортом данных и сбросом настроек.
    """
    def __init__(self, app):
        super().__init__(app)
        # Настройка интерфейса
        self.dark_mode_switch = ft.Switch(label="Темная тема", value=self.app.settings.interface.dark_mode,
                                          on_change=self._dark_mode_change)
        # Выбор файлового сервера
        self.path_file_server_text_field = ft.TextField(label="Файловый сервер",
                                                        value=self.app.settings.paths.file_server,
                                                        on_change=lambda e: self._reset_text_error(
                                                            self.path_file_server_text_field),
                                                        expand=True)
        self.path_file_server_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_size=24, tooltip="Выбрать путь",
                                                     on_click=lambda e: self._select_dir_action(
                                                         self.path_file_server_text_field, 'file_server'))
        # Выбор папки проектов
        self.path_projects_folder_text_field = ft.TextField(label="Папка объектов",
                                                            value=f"{self.app.settings.paths.file_server}\\"
                                                                  f"{self.app.settings.paths.projects_folder}",
                                                            on_change=lambda e: self._reset_text_error(
                                                                self.path_projects_folder_text_field),
                                                            expand=True)
        self.path_projects_folder_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_size=24,
                                                         tooltip="Выбрать путь",
                                                         on_click=lambda e: self._select_dir_action(
                                                             self.path_projects_folder_text_field, 'projects_folder'))
        # Подключение базы данных
        self.path_database_text_field = ft.TextField(label="Путь к базе данных",
                                                     value=self.app.settings.paths.database_path,
                                                     on_change=lambda e: self._reset_text_error(
                                                         self.path_database_text_field),
                                                     expand=True)
        self.path_database_file_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, icon_size=24, tooltip="Выбрать путь",
                                                       on_click=lambda e: self._select_file_action(
                                                           self.path_database_text_field, 'database_path'))
        # Тест подключения к БД
        self.test_connection_button = ft.TextButton(text="Тест соединения ...", on_click=self._test_connection)

    def _dark_mode_change(self, e):
        if self.dark_mode_switch.value:
            self.app.settings.interface.dark_mode = True
            self.app.page.theme_mode = "dark"
        else:
            self.app.settings.interface.dark_mode = False
            self.app.page.theme_mode = "light"
        self.app.save_settings()
        self.app.page.update()

    def _select_dir_action(self, obj: Any, parameter: str) -> None:
        """Добавляет новую директорию в закрепленные"""

        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                obj.value = e.path
                self._reset_text_error(obj)
                self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.get_directory_path()

    def _select_file_action(self, obj: Any, parameter: str) -> None:
        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                obj.value = e.path
                self._reset_text_error(obj)
                self.page.update()

        pick_files_dialog = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.pick_files()

    def _reset_text_error(self, obj: Any) -> None:
        obj.error_text = None
        print("_reset_text_error", obj.error_text)
        self.page.update()

    def _test_connection(self, e) -> None:
        test_database_service = DatabaseService(self.path_database_text_field.value)
        try:
            test_database_service.connection()
            self.app.show_info("Соединение установлено!")
        except Exception as e:
            self.app.show_error("Соединение не установлено!")
            self.logger.error(f"Ошибка тестового подключения к базе данных:\n{traceback.format_exc()}")

    def get_content(self):
        """
        Возвращает содержимое страницы настроек (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Text("О программе", size=18, weight=ft.FontWeight.BOLD),
            ft.Text(f"GeoOffice\nВерсия {self.app.version}"),
            ft.Text("Ведение документации по объектам и геодезические расчеты"),
            ft.Text(f"Автор: Мысливец Максим"),
            ft.Divider(height=20),
            
            ft.Column([
                ft.Text("Интерфейс", size=18, weight=ft.FontWeight.BOLD),
                self.dark_mode_switch
            ]),

            ft.Column([
                ft.Text("Файловый сервер", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([self.path_file_server_text_field, self.path_file_server_button]),
                ft.Row([self.path_projects_folder_text_field, self.path_projects_folder_button]),
            ]),

            ft.Column([
                ft.Text("База данных", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([self.path_database_text_field, self.path_database_file_button]),
            ]),
            self.test_connection_button,

            ft.Row([
                ft.ElevatedButton("Сброс настроек", icon=ft.Icons.RESTORE, on_click=self.reset_settings),
                ft.ElevatedButton("Применить", icon=ft.Icons.CHECK, on_click=self.apply)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ])
    
    def reset_settings(self, e=None):
        """
        Сброс настроек приложения к значениям по умолчанию.
        :param e: Событие нажатия кнопки
        """
        self.app.settings.init_default_settings()
        self.app.save_settings()

        self.app.database_service = DatabaseService(self.app.settings.paths.database_path)

        self.path_file_server_text_field.value = self.app.settings.paths.file_server
        self.path_projects_folder_text_field.value = (f"{self.app.settings.paths.file_server}\\"
                                                      f"{self.app.settings.paths.projects_folder}")
        self.path_database_text_field.value = self.app.settings.paths.database_path

        self.dark_mode_switch.value = False
        self._dark_mode_change(None)

        self.app.page.update()

    def apply(self, e=None):
        """
        Применение настроек приложения
        :param e: Событие нажатия кнопки
        """
        def check_dir(dirpath: str | Path) -> bool:
            return Path(dirpath).is_dir()

        def check_file(filepath: str | Path) -> bool:
            return Path(filepath).exists()

        if check_dir(self.path_file_server_text_field.value):
            self.path_file_server_text_field.error_text = None
            self.app.settings.paths.file_server = self.path_file_server_text_field.value
            self.app.save_settings()
        else:
            self.path_file_server_text_field.error_text = "Неверный путь"

        if check_dir(self.path_projects_folder_text_field.value):
            if self.path_projects_folder_text_field.value.startswith(self.path_file_server_text_field.value):
                self.path_projects_folder_text_field.error_text = None
                self.app.settings.paths.projects_folder = self.path_projects_folder_text_field.value[
                                                          len(self.path_file_server_text_field.value) + 1:]
                self.app.save_settings()
            else:
                self.path_projects_folder_text_field.error_text = ("Папка не находится на файловом сервере либо "
                                                                   "неверно указано расположение файлового сервера")
        else:
            self.path_projects_folder_text_field.error_text = "Неверный путь"

        if check_file(self.path_database_text_field.value):
            self.path_database_text_field.error_text = None
            self.app.settings.paths.database_path = self.path_database_text_field.value
            self.app.database_service = DatabaseService(self.app.settings.paths.database_path)
            self.app.database_service.connection()
            self.app.save_settings()
        else:
            self.path_database_text_field.error_text = "Неверный путь"

        self.app.page.update()
