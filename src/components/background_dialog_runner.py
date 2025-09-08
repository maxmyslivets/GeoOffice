import threading
import time
from typing import Callable, Optional, Any

import flet as ft


class BackgroundDialogRunner:
    """
    Обёртка над BackgroundService, показывающая AlertDialog с прогрессом и кнопкой отмены.

    Ожидаемая сигнатура пользовательской задачи:
        task_func(progress: Callable[[float, Optional[str]], None], stop_event: threading.Event) -> Any
    """

    def __init__(self, app) -> None:
        self._app = app  # ожидается, что есть .page и .background_service

    def run(
        self,
        task_name: str,
        task_func: Callable[[Callable[[float, Optional[str]], None], threading.Event], Any],
        *,
        show_progress: bool = True,
        on_cancel: Optional[Callable[[], None]] = None,
        on_complete: Optional[Callable[[Any], None]] = None,
    ) -> bool:
        page: ft.Page = self._app.page
        service = self._app.background_service

        progress_bar = ft.ProgressBar(width=420, value=0 if show_progress else None)
        status_text = ft.Text("Подготовка...")

        def cancel_clicked(_: ft.ControlEvent) -> None:
            service.stop_task(task_name)
            status_text.value = "Отменено пользователем"
            page.update()
            if on_cancel is not None:
                try:
                    on_cancel()
                finally:
                    pass
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(task_name),
            content=ft.Column([
                status_text,
                progress_bar,
            ], tight=True, spacing=12),
            actions=[
                ft.TextButton("Отмена", on_click=cancel_clicked),
            ],
        )

        throttle_seconds = 0.1  # максимум ~10 обновлений в секунду
        last_update_ts = 0.0

        def worker() -> None:
            # Получаем stop_event, который установит BackgroundService
            stop_event = service._stop_events.get(task_name)

            def report_progress(value: float, message: Optional[str] = None) -> None:
                nonlocal last_update_ts
                if not show_progress:
                    return
                now = time.time()
                # Всегда обновляем значения в контролах, но page.update делаем редко
                v = 0.0 if value < 0 else 1.0 if value > 1 else float(value)
                progress_bar.value = v
                if message is not None:
                    status_text.value = message
                if (now - last_update_ts) >= throttle_seconds:
                    last_update_ts = now
                    page.update()

            try:
                status_text.value = "Выполняется..."
                page.update()
                result: Any = task_func(report_progress, stop_event)
                if stop_event is None or not stop_event.is_set():
                    if show_progress:
                        progress_bar.value = 1.0
                    status_text.value = "Готово"
                    page.update()
                    if on_complete is not None:
                        try:
                            on_complete(result)
                        finally:
                            pass
            finally:
                dlg.open = False
                page.update()

        def start_wrapper():
            # Запустить задачу через BackgroundService, передав наш worker
            return service.start_task(task_name, worker)

        if show_progress:
            page.open(dlg)
            page.update()

        return start_wrapper() 