import flet as ft
from .base_page import BasePage


class DocumentsPage(BasePage):
    """
    Страница работы с документами.
    Позволяет создавать отчёты, картограммы и технические задания, а также использовать шаблоны документов.
    """
    
    def get_content(self):
        """
        Возвращает содержимое страницы документов (UI).
        :return: Flet Column с элементами интерфейса
        """
        # return ft.Column([
        #     ft.Text("Работа с документами", size=24, weight=ft.FontWeight.BOLD),
        #     ft.Divider(height=20),
        #
        #     ft.Row([
        #         ft.ElevatedButton("Создать отчет", icon=ft.Icons.ADD, on_click=self.create_report),
        #         ft.ElevatedButton("Создать картограмму", icon=ft.Icons.MAP, on_click=self.create_cartogram),
        #         ft.ElevatedButton("Техническое задание", icon=ft.Icons.ASSIGNMENT, on_click=self.create_technical_task),
        #     ]),
        #
        #     ft.Divider(height=20),
        #
        #     ft.Text("Шаблоны документов", size=18, weight=ft.FontWeight.BOLD),
        #     ft.DataTable(
        #         columns=[
        #             ft.DataColumn(ft.Text("Название")),
        #             ft.DataColumn(ft.Text("Описание")),
        #             ft.DataColumn(ft.Text("Действия")),
        #         ],
        #         rows=[
        #             ft.DataRow(
        #                 cells=[
        #                     ft.DataCell(ft.Text("Отчет о геодезических работах")),
        #                     ft.DataCell(ft.Text("Стандартный отчет по результатам измерений")),
        #                     ft.DataCell(ft.ElevatedButton("Использовать", on_click=self.use_template)),
        #                 ]
        #             ),
        #             ft.DataRow(
        #                 cells=[
        #                     ft.DataCell(ft.Text("Картограмма участка")),
        #                     ft.DataCell(ft.Text("План участка с нанесенными точками")),
        #                     ft.DataCell(ft.ElevatedButton("Использовать", on_click=self.use_template)),
        #                 ]
        #             ),
        #         ]
        #     )
        # ])
        return ft.Text("Страница в разработке...", color=ft.Colors.RED, size=20)
    
    def create_report(self, e=None):
        """
        Создание отчёта по геодезическим работам.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Создание отчета...")
    
    def create_cartogram(self, e=None):
        """
        Создание картограммы участка.
        :param e: Событие нажатия кнопки
        """
        self.app.show_page('cartogram')
    
    def create_technical_task(self, e=None):
        """
        Создание технического задания.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Создание технического задания...")
    
    def use_template(self, e=None):
        """
        Использование выбранного шаблона документа.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Использование шаблона...") 