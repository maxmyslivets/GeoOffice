import flet as ft
from .base_page import BasePage
from src.services.coordinate_service import CoordinateService


class CoordinatesPage(BasePage):
    """
    Страница работы с координатами и форматированием.
    Позволяет создавать файлы пересчёта, формировать координаты для Metashape и DJI Terra, а также форматировать вводимые координаты.
    """
    
    def __init__(self, app):
        """
        Инициализация страницы координат.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.input_field = ft.TextField(
            label="Введите координаты (X Y)",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="100.123 200.456\n101.789 201.654",
            expand=True
        )
        self.result_field = ft.TextField(
            label="Результат форматирования",
            multiline=True,
            min_lines=5,
            max_lines=10,
            read_only=True,
            expand=True
        )
        self.error_text = ft.Text("", color=ft.Colors.RED, size=14)
    
    def get_content(self):
        """
        Возвращает содержимое страницы координат (UI).
        :return: Flet Column с элементами интерфейса
        """
        return ft.Column([
            ft.Text("Работа с системами координат", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            ft.Row([
                ft.ElevatedButton("Создать файл пересчета", icon=ft.Icons.CREATE, on_click=self.create_conversion_file),
                ft.ElevatedButton("Proj-файл для Metashape", icon=ft.Icons.FILE_COPY, on_click=self.create_metashape_file),
                ft.ElevatedButton("DJI Terra файл", icon=ft.Icons.FLIGHT, on_click=self.create_dji_file),
            ]),
            
            ft.Divider(height=20),
            
            ft.Text("Форматирование координат", size=18, weight=ft.FontWeight.BOLD),
            self.input_field,
            ft.Row([
                ft.ElevatedButton("Форматировать", icon=ft.Icons.FORMAT_ALIGN_LEFT, on_click=self.format_coordinates),
                ft.ElevatedButton("Очистить", icon=ft.Icons.CLEAR, on_click=self.clear_coordinates),
                ft.ElevatedButton("Пример", icon=ft.Icons.INSERT_DRIVE_FILE, on_click=self.load_example),
            ]),
            self.error_text,
            self.result_field,
        ])
    
    def create_conversion_file(self, e=None):
        """
        Создание файла пересчёта координат.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Создание файла пересчета...")
    
    def create_metashape_file(self, e=None):
        """
        Создание proj-файла для Metashape.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Создание proj-файла для Metashape...")
    
    def create_dji_file(self, e=None):
        """
        Создание файла для DJI Terra.
        :param e: Событие нажатия кнопки
        """
        self.show_snack_bar("Создание файла для DJI Terra...")
    
    def format_coordinates(self, e=None):
        """
        Форматирование введённых координат.
        :param e: Событие нажатия кнопки
        """
        text = self.input_field.value or ""
        self.error_text.value = ""
        self.result_field.value = ""
        try:
            coords = CoordinateService.parse(text)
            formatted = CoordinateService.format(coords, sep="\t")
            self.result_field.value = formatted
            self.show_snack_bar("Координаты успешно отформатированы!")
        except Exception as ex:
            self.error_text.value = str(ex)
        self.update_page()
    
    def clear_coordinates(self, e=None):
        """
        Очистка полей ввода и результата.
        :param e: Событие нажатия кнопки
        """
        self.input_field.value = ""
        self.result_field.value = ""
        self.error_text.value = ""
        self.update_page()
    
    def load_example(self, e=None):
        """
        Загрузка примера координат из файла.
        :param e: Событие нажатия кнопки
        """
        try:
            with open("assets/example.txt", "r", encoding="utf-8") as f:
                self.input_field.value = f.read()
            self.error_text.value = ""
        except Exception as ex:
            self.error_text.value = f"Ошибка загрузки примера: {ex}"
        self.update_page() 