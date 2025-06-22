import flet as ft
from .base_page import BasePage


class AutocadPage(BasePage):
    """
    Страница плагинов AutoCAD.
    Позволяет устанавливать плагины для работы с мультивыносками и подписями координат.
    """
    
    def get_content(self):
        """
        Возвращает содержимое страницы AutoCAD (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Text("Плагины AutoCAD", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Расстановка мультивыносок", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Автоматическая расстановка выносок на чертеже", color=ft.Colors.GREY_600),
                        ft.ElevatedButton("Установить плагин", icon=ft.Icons.DOWNLOAD, on_click=self.install_multileader_plugin),
                    ]),
                    padding=20
                )
            ),
            
            ft.Divider(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Подписи координат", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Автоматическое нанесение координат на чертеж", color=ft.Colors.GREY_600),
                        ft.ElevatedButton("Установить плагин", icon=ft.Icons.DOWNLOAD, on_click=self.install_coordinates_plugin),
                    ]),
                    padding=20
                )
            )
        ])
    
    def install_multileader_plugin(self, e=None):
        """
        Установка плагина мультивыносок для AutoCAD.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Установка плагина мультивыносок...")
    
    def install_coordinates_plugin(self, e=None):
        """
        Установка плагина подписей координат для AutoCAD.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Установка плагина подписей координат...") 