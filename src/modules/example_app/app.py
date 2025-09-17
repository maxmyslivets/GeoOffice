import flet as ft

from src.modules.base_app.app import BaseApp


class ExampleApp(BaseApp):

    def __init__(self):
        super().__init__("Example App")
        self.menu = None

    def get_content(self):
        self.menu = ft.NavigationRail()
        self.page.add(self.menu)
