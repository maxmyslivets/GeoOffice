import flet as ft

from src.utils.logger_config import get_logger


class Menu:
    """
    Меню.
    Позволяет переходить по разделам приложения.
    """

    def __init__(self, app) -> None:
        """
        Инициализация меню.
        :param app: Экземпляр основного приложения
        """
        self._app = app
        self._menu_items: list | None = None
        self._navigation_rail: ft.NavigationRail | None = None

    def create_menu(self, items) -> ft.NavigationRail:
        self._menu_items = items
        destinations = []
        for name, properties in self._menu_items:
            destinations.append(
                ft.NavigationRailDestination(
                    icon=properties["icon"],
                    label=name,
                )
            )
        self._navigation_rail = ft.NavigationRail(
            selected_index=0,
            destinations=destinations,
        )
        self._navigation_rail.on_change = self._on_change

        return self._navigation_rail

    def _on_change(self, event) -> None:
        item_index = self._navigation_rail.selected_index
        page = self._menu_items[item_index][1]["page"]
        self._app.show_page(page)
