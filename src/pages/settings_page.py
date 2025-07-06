import flet as ft
from datetime import datetime
from .base_page import BasePage


class SettingsPage(BasePage):
    """
    Страница настроек приложения.
    Позволяет управлять автосохранением, темой, экспортом/импортом данных и сбросом настроек.
    """
    
    def get_content(self):
        """
        Возвращает содержимое страницы настроек (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Text("Настройки", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Text("О программе", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("GeoOffice v1.0"),
            ft.Text("Система для геодезических работ"),
            ft.Text(f"Создано: {datetime.now().strftime('%Y-%m-%d')}"),
            
            ft.Divider(height=20),
            
            ft.Row([
                # ft.ElevatedButton("Экспорт данных", icon=ft.Icons.DOWNLOAD, on_click=self.export_data),
                # ft.ElevatedButton("Импорт данных", icon=ft.Icons.UPLOAD, on_click=self.import_data),
                ft.ElevatedButton("Сброс настроек", icon=ft.Icons.RESTORE, on_click=self.reset_settings),
            ])
        ])
    
    def reset_settings(self, e=None):
        """
        Сброс настроек приложения к значениям по умолчанию.
        :param e: Событие нажатия кнопки
        """
        self.app.settings.init_default_settings()
        self.app.save_settings()
        self.app.show_info("Выполнен сброс настроек приложения к значениям по умолчанию")
