import flet as ft
from .base_page import BasePage


class ConversionPage(BasePage):
    """
    Страница конвертации файлов.
    Позволяет конвертировать файлы JSON и SHP в форматы DXF/DWG.
    """
    
    def get_content(self):
        """
        Возвращает содержимое страницы конвертации (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Text("Конвертация файлов", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("ГЗУ из геопортала", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Конвертация JSON в DXF/DWG", color=ft.Colors.GREY_600),
                        ft.Row([
                            ft.ElevatedButton("Выбрать JSON файл", icon=ft.Icons.FILE_OPEN, on_click=self.select_json_file),
                            ft.ElevatedButton("Конвертировать", icon=ft.Icons.TRANSFORM, on_click=self.convert_json),
                        ])
                    ]),
                    padding=20
                )
            ),
            
            ft.Divider(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Shape файлы НЦА", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Конвертация SHP в DXF/DWG", color=ft.Colors.GREY_600),
                        ft.Row([
                            ft.ElevatedButton("Выбрать SHP файл", icon=ft.Icons.FILE_OPEN, on_click=self.select_shp_file),
                            ft.ElevatedButton("Конвертировать", icon=ft.Icons.TRANSFORM, on_click=self.convert_shp),
                        ])
                    ]),
                    padding=20
                )
            )
        ])
    
    def select_json_file(self, e=None):
        """
        Выбор JSON файла для конвертации.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Выбор JSON файла...")
    
    def convert_json(self, e=None):
        """
        Конвертация выбранного JSON файла в DXF/DWG.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Конвертация JSON в DXF/DWG...")
    
    def select_shp_file(self, e=None):
        """
        Выбор SHP файла для конвертации.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Выбор SHP файла...")
    
    def convert_shp(self, e=None):
        """
        Конвертация выбранного SHP файла в DXF/DWG.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Конвертация SHP в DXF/DWG...") 