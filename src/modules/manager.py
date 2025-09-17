import multiprocessing
import flet as ft


class ModuleManager:

    def __init__(self, app):
        self.app = app

    def run(self):
        multiprocessing.Process(target=self._flet_run).start()

    def _flet_run(self):
        ft.app(target=self._main, assets_dir="assets")

    def _main(self, page: ft.Page):
        self.app().main(page)
