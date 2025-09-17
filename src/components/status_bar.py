import flet as ft


class StatusBar:
    # FIXME
    def __init__(self, app):
        self._app = app
        self.progress_bar = ft.ProgressBar(0)
        self.tasks = []
        self.content = ft.Container(content=None)

    def _start_progress(self):
        self.progress_bar.value = None
        self.content = ft.Container(content=ft.Column([
            self.progress_bar,
            ft.Text(f"({len(self.tasks)})"),
        ], expand=True))

    def _stop_progress(self):
        self.progress_bar.value = 0
        self.content = ft.Container(content=None)

    def add_task(self, task):
        self.tasks.append(task)
        self._start_progress()
        self._app.page.update()

    def delete_task(self, task):
        self.tasks.remove(task)
        self._stop_progress()
        self._app.page.update()
