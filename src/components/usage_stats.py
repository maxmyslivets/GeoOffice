import flet as ft
from src.utils.logger_config import get_logger

logger = get_logger("usage_stats")


class UsageStats:
    """
    Компонент для отображения статистики использования функций приложения.
    Позволяет отслеживать, какие разделы наиболее востребованы пользователями.
    """
    
    def __init__(self, app):
        """
        Инициализация компонента статистики использования.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        self.stats = {
            "home": 0,
            "documents": 0,
            "coordinates": 0,
            "conversion": 0,
            "scale": 0,
            "autocad": 0,
            "taxation": 0,
            "cartogram": 0,
            "settings": 0,
        }
    
    def increment_usage(self, page_name):
        """
        Увеличить счётчик использования страницы.
        :param page_name: Имя страницы
        """
        if page_name in self.stats:
            self.stats[page_name] += 1
            logger.debug(f"Увеличено использование страницы {page_name}: {self.stats[page_name]}")
    
    def get_most_used_pages(self, limit=3):
        """
        Получить наиболее используемые страницы.
        :param limit: Максимальное количество возвращаемых страниц
        :return: Список кортежей (имя страницы, количество)
        """
        sorted_stats = sorted(self.stats.items(), key=lambda x: x[1], reverse=True)
        return sorted_stats[:limit]
    
    def create_stats_widget(self):
        """
        Создать виджет статистики использования.
        :return: Flet Container с отображением статистики
        """
        most_used = self.get_most_used_pages()
        
        if not most_used or all(count == 0 for _, count in most_used):
            return ft.Container(
                content=ft.Text("Статистика использования пока недоступна", 
                               size=12, color=ft.Colors.GREY_500),
                padding=10
            )
        
        stats_items = []
        for page_name, count in most_used:
            if count > 0:
                page_names = {
                    "home": "Главная",
                    "documents": "Документы", 
                    "coordinates": "Координаты",
                    "conversion": "Конвертация",
                    "scale": "Масштабы",
                    "autocad": "AutoCAD",
                    "taxation": "Таксация",
                    "cartogram": "Картограмма",
                    "settings": "Настройки"
                }
                
                stats_items.append(
                    ft.Row([
                        ft.Text(page_names.get(page_name, page_name), size=10),
                        ft.Text(f"{count}", size=10, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Часто используемые:", size=10, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1),
                *stats_items
            ], spacing=5),
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=6
        ) 