import flet as ft
from .base_page import BasePage
from src.services.scale_service import ScaleService


class ScalePage(BasePage):
    """Страница расчета масштабов"""
    
    def __init__(self, app):
        super().__init__(app)
        self.current_calculation = None
        
        # Поля для расчета по расстояниям
        self.real_distance_field = ft.TextField(
            label="Реальное расстояние (м)",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="100.0"
        )
        self.map_distance_field = ft.TextField(
            label="Расстояние на карте (мм)",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="20.0"
        )
        
        # Поля для расчета по площадям
        self.real_area_field = ft.TextField(
            label="Реальная площадь (га)",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="1.5"
        )
        self.map_area_field = ft.TextField(
            label="Площадь на карте (мм²)",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="600.0"
        )
        
        # Поле для ручного ввода масштаба
        self.manual_scale_field = ft.TextField(
            label="Масштаб (например: 1:1000)",
            hint_text="1:1000"
        )
        
        # Поле для расчета расстояний
        self.input_distance_field = ft.TextField(
            label="Введите расстояние",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="100.0"
        )
        self.input_scale_field = ft.TextField(
            label="Масштаб",
            hint_text="1:1000"
        )
        
        # Результаты
        self.result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
        self.distance_result_text = ft.Text("", size=14)
        
        # Выпадающий список стандартных масштабов
        self.standard_scales_dropdown = ft.Dropdown(
            label="Стандартные масштабы",
            options=[ft.dropdown.Option(scale) for scale in ScaleService.get_standard_scales()],
            on_change=self.on_standard_scale_selected
        )
    
    def get_content(self):
        return ft.Column([
            ft.Text("Расчет масштабов", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            # Расчет по расстояниям
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Расчет масштаба по расстояниям", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.real_distance_field,
                            self.map_distance_field,
                        ]),
                        ft.ElevatedButton("Рассчитать масштаб", on_click=self.calculate_scale_from_distances),
                    ]),
                    padding=20
                )
            ),
            
            ft.Divider(height=20),
            
            # Расчет по площадям
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Расчет масштаба по площадям", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.real_area_field,
                            self.map_area_field,
                        ]),
                        ft.ElevatedButton("Рассчитать масштаб", on_click=self.calculate_scale_from_areas),
                    ]),
                    padding=20
                )
            ),
            
            ft.Divider(height=20),
            
            # Ручной ввод масштаба
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Ручной ввод масштаба", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.manual_scale_field,
                            self.standard_scales_dropdown,
                        ]),
                        ft.ElevatedButton("Рассчитать точность", on_click=self.calculate_manual_scale),
                    ]),
                    padding=20
                )
            ),
            
            ft.Divider(height=20),
            
            # Расчет расстояний
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Расчет расстояний по масштабу", size=18, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.input_distance_field,
                            self.input_scale_field,
                        ]),
                        ft.Row([
                            ft.ElevatedButton("Расстояние на карте", on_click=self.calculate_map_distance),
                            ft.ElevatedButton("Реальное расстояние", on_click=self.calculate_real_distance),
                        ]),
                        self.distance_result_text,
                    ]),
                    padding=20
                )
            ),
            
            ft.Divider(height=20),
            
            # Результаты
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Результаты расчета", size=18, weight=ft.FontWeight.BOLD),
                        self.result_text,
                    ]),
                    padding=20
                )
            ),
        ])
    
    def calculate_scale_from_distances(self, e=None):
        """Расчет масштаба по расстояниям"""
        try:
            real_distance = float(self.real_distance_field.value or 0)
            map_distance = float(self.map_distance_field.value or 0)
            
            if real_distance <= 0 or map_distance <= 0:
                raise ValueError("Расстояния должны быть больше нуля")
            
            self.current_calculation = ScaleService.calculate_scale_from_distances(real_distance, map_distance)
            self.show_result()
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка: {str(ex)}")
    
    def calculate_scale_from_areas(self, e=None):
        """Расчет масштаба по площадям"""
        try:
            real_area = float(self.real_area_field.value or 0)
            map_area = float(self.map_area_field.value or 0)
            
            if real_area <= 0 or map_area <= 0:
                raise ValueError("Площади должны быть больше нуля")
            
            self.current_calculation = ScaleService.calculate_scale_from_areas(real_area, map_area)
            self.show_result()
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка: {str(ex)}")
    
    def calculate_manual_scale(self, e=None):
        """Расчет точности для ручного масштаба"""
        try:
            scale_text = self.manual_scale_field.value or ""
            if not scale_text:
                raise ValueError("Введите масштаб")
            
            self.current_calculation = ScaleService.calculate_manual_scale(scale_text)
            self.show_result()
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка: {str(ex)}")
    
    def calculate_map_distance(self, e=None):
        """Расчет расстояния на карте"""
        try:
            real_distance = float(self.input_distance_field.value or 0)
            scale_text = self.input_scale_field.value or ""
            
            if real_distance <= 0:
                raise ValueError("Расстояние должно быть больше нуля")
            if not scale_text:
                raise ValueError("Введите масштаб")
            
            scale = ScaleService.calculate_manual_scale(scale_text).scale
            map_distance = ScaleService.calculate_map_distance_from_scale(real_distance, scale)
            
            self.distance_result_text.value = f"Расстояние на карте: {map_distance:.2f} мм"
            self.update_page()
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка: {str(ex)}")
    
    def calculate_real_distance(self, e=None):
        """Расчет реального расстояния"""
        try:
            map_distance = float(self.input_distance_field.value or 0)
            scale_text = self.input_scale_field.value or ""
            
            if map_distance <= 0:
                raise ValueError("Расстояние должно быть больше нуля")
            if not scale_text:
                raise ValueError("Введите масштаб")
            
            scale = ScaleService.calculate_manual_scale(scale_text).scale
            real_distance = ScaleService.calculate_real_distance_from_scale(map_distance, scale)
            
            self.distance_result_text.value = f"Реальное расстояние: {real_distance:.2f} м"
            self.update_page()
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка: {str(ex)}")
    
    def on_standard_scale_selected(self, e=None):
        """Обработка выбора стандартного масштаба"""
        if e and e.control.value:
            self.manual_scale_field.value = e.control.value
            self.update_page()
    
    def show_result(self):
        """Показать результат расчета"""
        if self.current_calculation:
            result = f"""
Масштаб: {self.current_calculation.scale_text}
Точность: {self.current_calculation.accuracy:.2f} м
Тип расчета: {self.current_calculation.calculation_type}
            """.strip()
            
            self.result_text.value = result
            self.show_snack_bar("Расчет выполнен успешно!")
            self.update_page() 