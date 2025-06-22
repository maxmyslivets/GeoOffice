import flet as ft
from src.utils.logger_config import get_logger

logger = get_logger("breadcrumbs")


class Breadcrumbs:
    """
    Компонент для отображения хлебных крошек (навигационной цепочки).
    Позволяет пользователю видеть путь и быстро возвращаться к разделам.
    """
    
    def __init__(self, app):
        """
        Инициализация компонента хлебных крошек.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        
        # Маппинг страниц на их категории и названия
        self.page_mapping = {
            "home": {"category": "Главная", "name": "Главная страница"},
            "documents": {"category": "Документы", "name": "Управление документами"},
            "documents_import": {"category": "Документы", "name": "Импорт файлов"},
            "documents_export": {"category": "Документы", "name": "Экспорт данных"},
            "documents_archive": {"category": "Документы", "name": "Архив документов"},
            "cartogram": {"category": "Документы", "name": "Картограмма"},
            "coordinates": {"category": "Геодезические работы", "name": "Координаты"},
            "conversion": {"category": "Геодезические работы", "name": "Конвертация"},
            "scale": {"category": "Геодезические работы", "name": "Масштабы"},
            "autocad": {"category": "Специализированные инструменты", "name": "AutoCAD"},
            "taxation": {"category": "Специализированные инструменты", "name": "Таксация"},
            "settings": {"category": "Система", "name": "Настройки"},
        }
    
    def create_breadcrumbs(self, current_page):
        """
        Создание хлебных крошек для текущей страницы.
        :param current_page: Имя текущей страницы
        :return: Flet Container с хлебными крошками
        """
        if current_page not in self.page_mapping:
            return ft.Container()
        
        page_info = self.page_mapping[current_page]
        
        # Создаём интерактивные элементы хлебных крошек
        home_link = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HOME, size=16, color=ft.Colors.BLUE),
                ft.Text("GeoOffice", size=12, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
            ], spacing=5),
            on_click=lambda e: self.navigate_to_page("home"),
            ink=True,
            border_radius=4,
            padding=ft.padding.only(left=5, right=5, top=2, bottom=2)
        )
        
        category_link = ft.Container(
            content=ft.Text(page_info["category"], size=12, color=ft.Colors.BLUE, weight=ft.FontWeight.BOLD),
            on_click=lambda e: self.navigate_to_category(page_info["category"]),
            ink=True,
            border_radius=4,
            padding=ft.padding.only(left=5, right=5, top=2, bottom=2)
        )
        
        current_page_text = ft.Text(page_info["name"], size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700)
        
        breadcrumbs = ft.Row([
            home_link,
            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=12, color=ft.Colors.GREY_400),
            category_link,
            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=12, color=ft.Colors.GREY_400),
            current_page_text,
        ], spacing=5)
        
        return ft.Container(
            content=breadcrumbs,
            padding=ft.padding.only(left=20, top=10, bottom=10),
            bgcolor=ft.Colors.GREY_50,
            border_radius=8
        )
    
    def navigate_to_page(self, page_name):
        """
        Переход к странице по хлебным крошкам.
        :param page_name: Имя страницы
        """
        logger.debug(f"Переход по хлебным крошкам к странице: {page_name}")
        self.app.show_page(page_name)
    
    def navigate_to_category(self, category_name):
        """
        Переход к категории (показывает первую страницу категории).
        :param category_name: Имя категории
        """
        logger.debug(f"Переход по хлебным крошкам к категории: {category_name}")
        
        # Маппинг категорий на первую страницу
        category_to_page = {
            "Главная": "home",
            "Документы": "documents",
            "Геодезические работы": "coordinates",
            "Специализированные инструменты": "autocad",
            "Система": "settings"
        }
        
        if category_name in category_to_page:
            self.app.show_page(category_to_page[category_name])
        else:
            logger.warning(f"⚠️ Категория {category_name} не найдена в маппинге") 