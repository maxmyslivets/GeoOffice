import flet as ft
from .base_page import BasePage
from src.services.cartogram_service import CartogramService
from src.models.cartogram_models import CartogramData
import logging
from shapely.geometry import Polygon, MultiPolygon
import os
from datetime import datetime
from src.utils.logger_config import log_exception


class CartogramPage(BasePage):
    """Страница создания картограмм"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger.info("🔧 Инициализация страницы картограммы")
        self.cartogram_service = CartogramService()
        self.current_cartogram = None
        self.dxf_file_path = None
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.save_picker = ft.FilePicker(on_result=self.on_save_picked)
        self.grid_size_field = ft.TextField(
            label="Размер ячейки сетки (м)",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="250",
            value="250"
        )
        self.coordinate_system_dropdown = ft.Dropdown(
            label="Система координат",
            options=[
                ft.dropdown.Option("СК63"),
                ft.dropdown.Option("МСК")
            ],
            value="СК63",
            on_change=self.on_coordinate_system_changed
        )
        self.info_text = ft.Text("", size=14)
        self.nomenclature_text = ft.TextField(
            label="Список номенклатур",
            multiline=True,
            min_lines=10,
            max_lines=15,
            read_only=True,
            expand=True
        )
        self.log_text = ft.TextField(
            label="Логи",
            multiline=True,
            min_lines=8,
            max_lines=12,
            read_only=True,
            expand=True
        )
        self.controls = [self.file_picker, self.save_picker]
        self.logger.info("✅ Страница картограммы инициализирована")

    def get_content(self):
        # self.logger.debug("📄 Создание контента страницы картограммы")
        # return ft.Column([
        #     *self.controls,
        #     ft.Text("Создание картограммы", size=24, weight=ft.FontWeight.BOLD),
        #     ft.Divider(height=20),
        #     ft.Row([
        #         ft.ElevatedButton("Загрузить DXF", icon=ft.Icons.FILE_OPEN, on_click=self.open_file_picker),
        #         ft.ElevatedButton("Создать сетку", icon=ft.Icons.GRID_ON, on_click=self.create_grid),
        #         ft.ElevatedButton("Сохранить в DXF", icon=ft.Icons.SAVE, on_click=self.open_save_picker),
        #         ft.ElevatedButton("Очистить", icon=ft.Icons.CLEAR, on_click=self.clear_all),
        #     ]),
        #     ft.Divider(height=20),
        #     ft.Card(
        #         content=ft.Container(
        #             content=ft.Column([
        #                 ft.Text("Настройки", size=18, weight=ft.FontWeight.BOLD),
        #                 ft.Row([
        #                     self.grid_size_field,
        #                     self.coordinate_system_dropdown,
        #                 ]),
        #             ]),
        #             padding=20
        #         )
        #     ),
        #     ft.Divider(height=20),
        #     ft.Row([
        #         ft.Column([
        #             ft.Text("Информация", size=18, weight=ft.FontWeight.BOLD),
        #             self.info_text,
        #             ft.Divider(height=20),
        #             ft.Text("Логи", size=16, weight=ft.FontWeight.BOLD),
        #             self.log_text,
        #         ], expand=True),
        #         ft.VerticalDivider(width=1),
        #         ft.Column([
        #             ft.Text("Список номенклатур", size=18, weight=ft.FontWeight.BOLD),
        #             self.nomenclature_text,
        #         ], expand=True),
        #     ], expand=True),
        # ])
        return ft.Text("Страница в разработке...", color=ft.Colors.RED, size=20)

    @log_exception
    def open_file_picker(self, e=None):
        self.logger.info("📂 Открытие диалога выбора файла DXF")
        self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["dxf"])

    @log_exception
    def on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            self.dxf_file_path = e.files[0].path
            self.logger.info(f"📁 Выбран файл: {os.path.basename(self.dxf_file_path)}")
            try:
                self.logger.debug("🔍 Парсинг DXF файла")
                multi_polygon = self.cartogram_service.parse_dxf_file(self.dxf_file_path)
                bounds = multi_polygon.bounds
                self.logger.debug(f"📍 Границы полигона: {bounds}")
                
                self.logger.debug("🗺️ Определение системы координат")
                coordinate_system = self.cartogram_service.detect_coordinate_system(bounds[0], bounds[1])
                self.cartogram_service.set_coordinate_system(coordinate_system)
                self.coordinate_system_dropdown.value = coordinate_system
                
                self.logger.debug("📊 Создание объекта картограммы")
                self.current_cartogram = CartogramData(
                    multi_polygon=multi_polygon,
                    grid_cells=[],
                    nomenclature_list=[],
                    coordinate_system=coordinate_system
                )
                
                self.update_info()
                self.log_message(f"Загружен файл: {os.path.basename(self.dxf_file_path)} (система координат: {coordinate_system})")
                self.app.show_info("Файл DXF загружен успешно!")
                self.update_page()
                
                self.logger.info(f"✅ Файл DXF успешно загружен: {os.path.basename(self.dxf_file_path)}")
            except Exception as ex:
                self.logger.error(f"❌ Ошибка при загрузке файла: {str(ex)}")
                self.log_message(f"Ошибка при загрузке файла: {str(ex)}")
                self.app.show_error(f"Ошибка при загрузке файла: {str(ex)}")
        else:
            self.logger.info("❌ Файл не выбран")

    @log_exception
    def create_grid(self, e=None):
        try:
            if not self.current_cartogram:
                self.logger.warning("⚠️ Попытка создать сетку без загруженного файла")
                self.app.show_warning("Сначала загрузите DXF файл")
                return
                
            grid_size = int(self.grid_size_field.value or 250)
            self.logger.info(f"🔲 Создание сетки с размером ячейки: {grid_size} м")
            
            self.logger.debug("📐 Создание ячеек сетки")
            grid_cells = self.cartogram_service.create_grid(
                self.current_cartogram.multi_polygon, grid_size)
            
            self.logger.debug("📋 Генерация списка номенклатур")
            nomenclature_list = self.cartogram_service.get_nomenclature_list(grid_cells)
            
            self.current_cartogram.grid_cells = grid_cells
            self.current_cartogram.nomenclature_list = nomenclature_list
            self.current_cartogram.grid_size = grid_size
            
            self.update_info()
            self.update_nomenclature_list()
            self.log_message(f"Создана сетка: {len(grid_cells)} ячеек")
            self.app.show_info("Сетка создана успешно!")
            self.update_page()
            
            self.logger.info(f"✅ Сетка создана успешно: {len(grid_cells)} ячеек, {len(nomenclature_list)} номенклатур")
        except Exception as ex:
            self.logger.error(f"❌ Ошибка при создании сетки: {str(ex)}")
            self.log_message(f"Ошибка при создании сетки: {str(ex)}")
            self.app.show_error(f"Ошибка при создании сетки: {str(ex)}")

    @log_exception
    def open_save_picker(self, e=None):
        self.logger.info("💾 Открытие диалога сохранения файла")
        self.save_picker.save_file(file_name="cartogram.dxf", allowed_extensions=["dxf"])

    @log_exception
    def on_save_picked(self, e: ft.FilePickerResultEvent):
        if e.path and self.current_cartogram and self.current_cartogram.grid_cells:
            self.logger.info(f"💾 Сохранение сетки в файл: {os.path.basename(e.path)}")
            try:
                self.logger.debug("📝 Сохранение сетки в DXF")
                self.cartogram_service.save_grid_to_dxf(
                    self.current_cartogram.grid_cells,
                    self.current_cartogram.multi_polygon,
                    e.path
                )
                self.log_message(f"Сетка сохранена в файл: {os.path.basename(e.path)}")
                self.app.show_info(f"Сетка сохранена в файл: {os.path.basename(e.path)}")
                self.update_page()
                
                self.logger.info(f"✅ Сетка успешно сохранена: {os.path.basename(e.path)}")
            except Exception as ex:
                self.logger.error(f"❌ Ошибка при сохранении файла: {str(ex)}")
                self.log_message(f"Ошибка при сохранении файла: {str(ex)}")
                self.app.show_error(f"Ошибка при сохранении файла: {str(ex)}")
        else:
            self.logger.warning("⚠️ Нет данных для сохранения")
            self.app.show_warning("Нет данных для сохранения!")

    @log_exception
    def clear_all(self, e=None):
        self.logger.info("🧹 Очистка всех данных")
        self.current_cartogram = None
        self.dxf_file_path = None
        self.info_text.value = ""
        self.nomenclature_text.value = ""
        self.log_message("Все данные очищены")
        self.update_page()
        self.logger.info("✅ Все данные очищены")

    @log_exception
    def on_coordinate_system_changed(self, e=None):
        if e and e.control.value:
            try:
                self.logger.info(f"🗺️ Изменение системы координат на: {e.control.value}")
                self.cartogram_service.set_coordinate_system(e.control.value)
                if self.current_cartogram:
                    self.current_cartogram.coordinate_system = e.control.value
                self.log_message(f"Система координат изменена на: {e.control.value}")
                self.update_page()
                self.logger.info(f"✅ Система координат изменена: {e.control.value}")
            except Exception as ex:
                self.logger.error(f"❌ Ошибка при изменении системы координат: {str(ex)}")
                self.app.show_error(f"Ошибка при изменении системы координат: {str(ex)}")

    @log_exception
    def update_info(self):
        if self.current_cartogram:
            self.logger.debug("📊 Обновление информации о картограмме")
            bounds = self.current_cartogram.get_bounds()
            info = f"""
📊 ИНФОРМАЦИЯ О КАРТОГРАММЕ

🗺️ Система координат: {self.current_cartogram.coordinate_system}
📐 Размер ячейки: {self.current_cartogram.grid_size} м
🔲 Количество ячеек: {self.current_cartogram.get_cell_count()}
📋 Количество номенклатур: {self.current_cartogram.get_nomenclature_count()}

📍 Границы:
   X: {bounds[0]:.2f} - {bounds[2]:.2f}
   Y: {bounds[1]:.2f} - {bounds[3]:.2f}
            """.strip()
            self.info_text.value = info
            self.logger.debug("✅ Информация обновлена")
        else:
            self.info_text.value = "Нет загруженных данных"
            self.logger.debug("⚠️ Нет данных для отображения информации")

    @log_exception
    def update_nomenclature_list(self):
        if self.current_cartogram and self.current_cartogram.nomenclature_list:
            self.logger.debug("📋 Обновление списка номенклатур")
            nomenclature_text = "\n".join([
                item.full_nomenclature for item in self.current_cartogram.nomenclature_list
            ])
            self.nomenclature_text.value = nomenclature_text
            self.logger.debug(f"✅ Список номенклатур обновлен: {len(self.current_cartogram.nomenclature_list)} элементов")
        else:
            self.nomenclature_text.value = "Нет данных о номенклатурах"
            self.logger.debug("⚠️ Нет данных о номенклатурах")

    @log_exception
    def log_message(self, message: str):
        current_logs = self.log_text.value or ""
        new_log = f"[{self.get_current_time()}] {message}"
        self.log_text.value = f"{current_logs}\n{new_log}" if current_logs else new_log
        self.logger.debug(f"📝 UI лог: {message}")

    def get_current_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S") 