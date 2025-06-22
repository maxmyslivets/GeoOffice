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
            
            ft.Switch(label="Автосохранение", value=True, on_change=self.toggle_auto_save),
            ft.Switch(label="Темная тема", value=False, on_change=self.toggle_theme),
            
            ft.Divider(height=20),
            
            ft.Text("О программе", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("GeoOffice v1.0"),
            ft.Text("Система для геодезических работ"),
            ft.Text(f"Создано: {datetime.now().strftime('%Y-%m-%d')}"),
            
            ft.Divider(height=20),
            
            ft.Row([
                ft.ElevatedButton("Экспорт данных", icon=ft.Icons.DOWNLOAD, on_click=self.export_data),
                ft.ElevatedButton("Импорт данных", icon=ft.Icons.UPLOAD, on_click=self.import_data),
                ft.ElevatedButton("Сброс настроек", icon=ft.Icons.RESTORE, on_click=self.reset_settings),
            ])
        ])
    
    def toggle_auto_save(self, e=None):
        """
        Переключение режима автосохранения.
        :param e: Событие переключения
        """
        if e and hasattr(e, 'control'):
            self.show_snack_bar(f"Автосохранение: {'включено' if e.control.value else 'выключено'}")
    
    def toggle_theme(self, e=None):
        """
        Переключение темы оформления приложения.
        :param e: Событие переключения
        """
        if e and hasattr(e, 'control') and e.control.value:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.update_page()
        self.show_snack_bar("Тема изменена")
    
    def export_data(self, e=None):
        """
        Экспорт данных приложения.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Экспорт данных...")
    
    def import_data(self, e=None):
        """
        Импорт данных в приложение.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Импорт данных...")
    
    def reset_settings(self, e=None):
        """
        Сброс настроек приложения к значениям по умолчанию.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Сброс настроек...") 