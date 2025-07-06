import flet as ft
from src.utils.logger_config import get_logger

logger = get_logger("components.categorized_menu")


class CategorizedMenu:
    """
    Меню с категориями и подпрограммами.
    Позволяет навигировать по разделам приложения через иерархическое меню.
    """
    
    def __init__(self, app):
        """
        Инициализация меню с категориями.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        self.expanded_categories = set()  # Множество развернутых категорий
        self.current_page = "home"  # Текущая активная страница
        self.menu_container = None  # Контейнер меню для обновления
        
        # Определение категорий и их подпрограмм
        self.categories = {
            "Главная": {
                "icon": ft.Icons.HOME,
                "color": ft.Colors.BLUE,
                "items": [
                    {"name": "Главная страница", "icon": ft.Icons.HOME_OUTLINED, "page": "home"},
                    {"name": "Управление проектами", "icon": ft.Icons.FOLDER_OPEN_OUTLINED, "page": "projects"},
                ]
            },
            "Документы": {
                "icon": ft.Icons.DESCRIPTION,
                "color": ft.Colors.BLUE,
                "items": [
                    {"name": "Управление документами", "icon": ft.Icons.FOLDER_OUTLINED, "page": "documents"},
                    {"name": "Импорт файлов", "icon": ft.Icons.UPLOAD_OUTLINED, "page": "documents_import"},
                    {"name": "Экспорт данных", "icon": ft.Icons.DOWNLOAD_OUTLINED, "page": "documents_export"},
                    {"name": "Архив документов", "icon": ft.Icons.ARCHIVE_OUTLINED, "page": "documents_archive"},
                    {"name": "Картограмма", "icon": ft.Icons.MAP_OUTLINED, "page": "cartogram"},
                ]
            },
            "Геодезические работы": {
                "icon": ft.Icons.EXPLORE,
                "color": ft.Colors.GREEN,
                "items": [
                    {"name": "Координаты", "icon": ft.Icons.EXPLORE_OUTLINED, "page": "coordinates"},
                    {"name": "Конвертация", "icon": ft.Icons.TRANSFORM_OUTLINED, "page": "conversion"},
                    {"name": "Масштабы", "icon": ft.Icons.STRAIGHTEN_OUTLINED, "page": "scale"},
                ]
            },
            "Специализированные инструменты": {
                "icon": ft.Icons.BUILD,
                "color": ft.Colors.ORANGE,
                "items": [
                    {"name": "AutoCAD", "icon": ft.Icons.BUILD_OUTLINED, "page": "autocad"},
                    {"name": "Таксация", "icon": ft.Icons.FOREST_OUTLINED, "page": "taxation"},
                ]
            },
            "Система": {
                "icon": ft.Icons.SETTINGS,
                "color": ft.Colors.GREY,
                "items": [
                    {"name": "Настройки", "icon": ft.Icons.SETTINGS_OUTLINED, "page": "settings"},
                ]
            }
        }
    
    def create_menu(self):
        """
        Создание меню с категориями.
        :return: Flet Column с элементами меню
        """
        logger.debug("Создание меню с категориями")
        
        menu_items = []
        
        # Добавляем поиск в начало меню
        if hasattr(self.app, 'menu_search'):
            search_widget = self.app.menu_search.create_search_widget()
            menu_items.append(search_widget)
            menu_items.append(ft.Divider(height=1, color=ft.Colors.GREY_300))
        
        for category_name, category_data in self.categories.items():
            category_item = self.create_category_item(category_name, category_data)
            menu_items.append(category_item)
        
        # Добавляем статистику использования в конец меню
        if hasattr(self.app, 'usage_stats'):
            stats_widget = self.app.usage_stats.create_stats_widget()
            menu_items.append(
                ft.Container(
                    content=stats_widget,
                    margin=ft.margin.only(top=20, left=10, right=10),
                    padding=ft.padding.only(bottom=10)
                )
            )
        
        menu_column = ft.Column(
            controls=menu_items,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Сохраняем ссылку на контейнер меню
        self.menu_container = menu_column
        
        return menu_column
    
    def create_category_item(self, category_name, category_data):
        """
        Создание элемента категории.
        :param category_name: Название категории
        :param category_data: Данные категории
        :return: Flet Container или Column
        """
        is_expanded = category_name in self.expanded_categories
        
        # Проверяем, есть ли активная страница в этой категории
        has_active_item = any(item["page"] == self.current_page for item in category_data["items"])
        
        # Для главной страницы создаём прямую ссылку без выпадающего меню
        if category_name == "Главная":
            return ft.Container(
                content=ft.Row([
                    ft.Icon(
                        category_data["icon"],
                        color=ft.Colors.BLUE if has_active_item else category_data["color"],
                        size=20
                    ),
                    ft.Text(
                        category_name,
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        color=ft.Colors.BLUE if has_active_item else category_data["color"]
                    )
                ], spacing=10),
                padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
                on_click=lambda e, page="home": self.navigate_to_page(page),
                border_radius=8,
                bgcolor=ft.Colors.BLUE_50 if has_active_item else ft.Colors.TRANSPARENT,
                border=ft.border.all(1, ft.Colors.BLUE_200) if has_active_item else None,
                ink=True
            )
        
        # Создаём заголовок категории для остальных категорий
        category_header = ft.Container(
            content=ft.Row([
                ft.Icon(
                    category_data["icon"],
                    color=category_data["color"],
                    size=20
                ),
                ft.Text(
                    category_name,
                    weight=ft.FontWeight.BOLD,
                    size=14,
                    color=category_data["color"]
                ),
                ft.Icon(
                    ft.Icons.EXPAND_MORE if is_expanded else ft.Icons.EXPAND_LESS,
                    size=16,
                    color=ft.Colors.GREY_600
                )
            ], spacing=10),
            padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
            on_click=lambda e, name=category_name: self.toggle_category(name),
            border_radius=8,
            bgcolor=ft.Colors.GREY_50 if (is_expanded or has_active_item) else ft.Colors.TRANSPARENT,
            ink=True
        )
        
        # Создаём список подпрограмм
        sub_items = []
        if is_expanded:
            for item in category_data["items"]:
                sub_item = self.create_sub_item(item)
                sub_items.append(sub_item)
        
        return ft.Column([
            category_header,
            ft.Container(
                content=ft.Column(
                    controls=sub_items,
                    spacing=2
                ),
                padding=ft.padding.only(left=20),
                visible=is_expanded
            )
        ])
    
    def create_sub_item(self, item_data):
        """
        Создание элемента подпрограммы.
        :param item_data: Данные подпрограммы
        :return: Flet Container
        """
        is_active = item_data["page"] == self.current_page
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    item_data["icon"],
                    size=16,
                    color=ft.Colors.BLUE if is_active else ft.Colors.GREY_600
                ),
                ft.Text(
                    item_data["name"],
                    size=12,
                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                    color=ft.Colors.BLUE if is_active else ft.Colors.GREY_700
                )
            ], spacing=8),
            padding=ft.padding.only(left=15, right=15, top=8, bottom=8),
            on_click=lambda e, page=item_data["page"]: self.navigate_to_page(page),
            border_radius=6,
            bgcolor=ft.Colors.BLUE_50 if is_active else ft.Colors.TRANSPARENT,
            border=ft.border.all(1, ft.Colors.BLUE_200) if is_active else None,
            ink=True
        )
    
    def toggle_category(self, category_name):
        """
        Переключение состояния категории (развернуть/свернуть).
        :param category_name: Название категории
        """
        logger.debug(f"Переключение категории: {category_name}")
        
        if category_name in self.expanded_categories:
            self.expanded_categories.remove(category_name)
        else:
            self.expanded_categories.add(category_name)
        
        # Пересоздаём меню
        self.recreate_menu()
    
    def recreate_menu(self):
        """
        Пересоздание меню с обновлённым состоянием.
        """
        try:
            if self.app.navigation and hasattr(self.app.navigation, 'content'):
                # Создаём новое меню
                new_menu = self.create_menu()
                
                # Обновляем содержимое навигации
                if len(self.app.navigation.content.controls) >= 2:
                    self.app.navigation.content.controls[2] = new_menu  # Индекс 2 - это меню после заголовка и разделителя
                else:
                    # Если структура изменилась, обновляем весь контент
                    menu_header = self.app.navigation.content.controls[0]
                    divider = self.app.navigation.content.controls[1]
                    self.app.navigation.content.controls = [menu_header, divider, new_menu]
                
                self.app.page.update()
                logger.debug("✅ Меню пересоздано")
        except Exception as e:
            logger.error(f"❌ Ошибка пересоздания меню: {e}")
    
    def navigate_to_page(self, page_name):
        """
        Переход к странице.
        :param page_name: Имя страницы
        """
        logger.debug(f"Переход к странице: {page_name}")
        self.current_page = page_name
        
        # Увеличиваем счётчик использования
        if hasattr(self.app, 'usage_stats'):
            self.app.usage_stats.increment_usage(page_name)
        
        self.app.show_page(page_name)
        
        # Автоматически разворачиваем категорию с активной страницей
        for category_name, category_data in self.categories.items():
            if any(item["page"] == page_name for item in category_data["items"]):
                if category_name not in self.expanded_categories:
                    self.expanded_categories.add(category_name)
                break
        
        # Пересоздаём меню
        self.recreate_menu()
    
    def set_current_page(self, page_name):
        """
        Установка текущей активной страницы.
        :param page_name: Имя страницы
        """
        self.current_page = page_name
        # Пересоздаём меню для обновления активного состояния
        self.recreate_menu() 