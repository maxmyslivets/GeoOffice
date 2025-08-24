from typing import Any

import flet as ft


class BannerDiffProjects:
    """
    Компонент для отображения баннера.
    """
    def __init__(self, app):
        """
        Инициализация компонента баннера.
        :param app: Экземпляр основного приложения
        """
        self.app = app
        self.page = app.page
        self.banner: ft.Banner | None = None

    def close_banner(self, e):
        self.page.close(self.banner)

    def create(self, text: str, actions: dict[str, Any]) -> ft.Banner:
        self.banner = ft.Banner(
            bgcolor=ft.Colors.AMBER_100,
            leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40),
            content=ft.Text(value=text, color=ft.Colors.BLACK),
            actions=[
                ft.TextButton(text=t, on_click=a)
                for t, a in actions.items()
            ],
        )
        return self.banner

    def show(self) -> None:
        self.page.open(self.banner)
