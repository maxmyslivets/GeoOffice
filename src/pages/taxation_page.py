import flet as ft
from .base_page import BasePage


class TaxationPage(BasePage):
    """
    Страница таксации.
    Позволяет выполнять расчёт отходов, проверку ведомости и расчёт таксации.
    """
    
    def get_content(self):
        """
        Возвращает содержимое страницы таксации (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Text("Таксация", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Row([
                ft.ElevatedButton("Расчет отходов", icon=ft.Icons.CALCULATE, on_click=self.calculate_waste),
                ft.ElevatedButton("Проверка ведомости", icon=ft.Icons.VERIFIED, on_click=self.check_statement),
            ]),
            
            ft.Divider(height=20),
            
            ft.Text("Ввод данных", size=18, weight=ft.FontWeight.BOLD),
            ft.TextField(label="Площадь участка (га)", keyboard_type=ft.KeyboardType.NUMBER),
            ft.TextField(label="Количество деревьев", keyboard_type=ft.KeyboardType.NUMBER),
            ft.ElevatedButton("Рассчитать", icon=ft.Icons.CALCULATE, on_click=self.calculate_taxation)
        ])
    
    def calculate_waste(self, e=None):
        """
        Расчёт отходов.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Расчет отходов...")
    
    def check_statement(self, e=None):
        """
        Проверка ведомости.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Проверка ведомости...")
    
    def calculate_taxation(self, e=None):
        """
        Расчёт таксации.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Расчет таксации...") 