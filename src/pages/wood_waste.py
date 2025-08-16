import flet as ft
from .base_page import BasePage


class WoodWastePage(BasePage):
    """
    Страница для расчета отходов древесины.
    Позволяет выполнять расчёт отходов при вырубке древесины на основе таксационного плана.
    """

    def get_content(self):
        """
        Возвращает содержимое страницы расчета отходов древесины (UI).
        :return: Flet Column с элементами интерфейса
        """
        # return ft.Column([
        #     ft.Text("Таксация", size=24, weight=ft.FontWeight.BOLD),
        #     ft.Divider(height=20),
        #
        #     ft.Row([
        #         ft.ElevatedButton("Расчет отходов", icon=ft.Icons.CALCULATE, on_click=self.calculate_waste),
        #         ft.ElevatedButton("Проверка ведомости", icon=ft.Icons.VERIFIED, on_click=self.check_statement),
        #     ]),
        #
        #     ft.Divider(height=20),
        #
        #     ft.Text("Ввод данных", size=18, weight=ft.FontWeight.BOLD),
        #     ft.TextField(label="Площадь участка (га)", keyboard_type=ft.KeyboardType.NUMBER),
        #     ft.TextField(label="Количество деревьев", keyboard_type=ft.KeyboardType.NUMBER),
        #     ft.ElevatedButton("Рассчитать", icon=ft.Icons.CALCULATE, on_click=self.calculate_taxation)
        # ])
        return ft.Text("Страница в разработке...", color=ft.Colors.RED, size=20)
