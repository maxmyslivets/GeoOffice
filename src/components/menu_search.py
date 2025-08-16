import flet as ft
from src.utils.logger_config import get_logger

logger = get_logger("components.menu_search")


class MenuSearch:
    """
    Компонент для поиска по функциям в меню.
    Позволяет быстро находить и переходить к нужным разделам приложения.
    """
    
    def __init__(self, app):
        """
        Инициализация компонента поиска по меню.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        self.search_results = []
        
        # Список всех функций для поиска
        self.all_functions = []
    
    def create_search_widget(self, categories: dict):
        """
        Создание виджета поиска по функциям меню.
        :return: Flet Column с полем поиска и результатами
        """
        self.all_functions.clear()
        for category in categories:
            for item in categories[category]["items"]:
                self.all_functions.append({"name": item["name"], "page": item["page"]})

        self.search_field = ft.TextField(
            hint_text="Поиск функций...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change,
            border_radius=20,
            text_size=12,
            height=35
        )
        
        self.search_results_container = ft.Container(
            content=ft.Text(""),
            visible=False,
            padding=10
        )
        
        return ft.Column([
            ft.Container(
                content=self.search_field,
                padding=ft.padding.only(left=10, right=10, top=10, bottom=5)
            ),
            self.search_results_container
        ])
    
    def on_search_change(self, e):
        """
        Обработка изменения поискового запроса.
        :param e: Событие изменения поля поиска
        """
        query = e.control.value.lower().strip()
        
        if not query:
            self.search_results_container.visible = False
            self.search_results_container.content = ft.Text("")
        else:
            # Поиск по функциям
            results = []
            for func in self.all_functions:
                if query in func["name"].lower():
                    results.append(func)
            
            if results:
                self.show_search_results(results)
            else:
                self.show_no_results()
        
        self.app.page.update()
    
    def show_search_results(self, results):
        """
        Показать результаты поиска по функциям меню.
        :param results: Список найденных функций
        """
        result_items = []
        
        for func in results:
            result_item = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(func["name"], size=12, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                padding=ft.padding.only(left=15, right=15, top=8, bottom=8),
                on_click=lambda e, page=func["page"]: self.navigate_to_result(page),
                border_radius=6,
                ink=True
            )
            result_items.append(result_item)
        
        self.search_results_container.content = ft.Column(
            controls=result_items,
            spacing=2
        )
        self.search_results_container.visible = True
    
    def show_no_results(self):
        """
        Показать сообщение об отсутствии результатов поиска.
        """
        self.search_results_container.content = ft.Text(
            "Функция не найдена",
            size=12,
            color=ft.Colors.GREY_500
        )
        self.search_results_container.visible = True
    
    def navigate_to_result(self, page_name):
        """
        Переход к найденной функции из поиска.
        :param page_name: Имя страницы
        """
        logger.debug(f"Переход к найденной функции: {page_name}")
        
        # Очищаем поиск
        self.search_field.value = ""
        self.search_results_container.visible = False
        self.search_results_container.content = ft.Text("")
        
        # Переходим к странице
        self.app.show_page(page_name) 