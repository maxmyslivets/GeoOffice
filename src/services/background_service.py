import threading
import time
from typing import Dict, Callable, Any
import flet as ft

from utils.logger_config import get_logger, log_exception

logger = get_logger("services.background_service")


class BackgroundService:
    """
    Сервис для управления фоновыми задачами.
    Предотвращает утечки памяти путем централизованного управления потоками.
    """

    def __init__(self, app):
        """Инициализация сервиса фоновых задач"""
        self._app = app
        self._tasks: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        logger.info("Инициализирован сервис фоновых задач")

    def get_tasks(self) -> Dict[str, threading.Thread]:
        return self._tasks

    def start_task(self, task_name: str, task_func: Callable):
        with self._lock:
            if task_name in self._tasks and self._tasks[task_name].is_alive():
                logger.warning(f"Задача {task_name} уже запущена")
                return False

            # Создаем событие для остановки
            stop_event = threading.Event()
            self._stop_events[task_name] = stop_event

            # Создаем и запускаем поток
            thread = threading.Thread(target=task_func, daemon=True, name=f"BackgroundTask-{task_name}")
            self._tasks[task_name] = thread
            thread.start()

            logger.info(f"Запущена фоновая задача: {task_name}")
            return True

    @log_exception
    def start_periodic_task(self, task_name: str, task_func: Callable,
                            initial_delay: float = 1.0,
                            interval: float = 30 * 60) -> bool:
        """
        Запускает периодическую задачу.

        :param task_name: Уникальное имя задачи
        :param task_func: Функция для выполнения
        :param initial_delay: Задержка перед первым запуском (в секундах)
        :param interval: Интервал между выполнениями (в секундах)
        :return: True если задача запущена, False если уже запущена
        """
        with self._lock:
            if task_name in self._tasks and self._tasks[task_name].is_alive():
                logger.warning(f"Задача {task_name} уже запущена")
                return False

            # Создаем событие для остановки
            stop_event = threading.Event()
            self._stop_events[task_name] = stop_event

            def periodic_wrapper():
                """Обертка для периодического выполнения задачи"""
                try:
                    # Первоначальная задержка
                    if stop_event.wait(initial_delay):
                        return  # Задача остановлена

                    # Первый запуск
                    task_func()

                    # Периодическое выполнение
                    while not stop_event.wait(interval):
                        try:
                            task_func()
                        except Exception as e:
                            logger.error(f"Ошибка в периодической задаче {task_name}: {e}")
                            # Пауза перед следующей попыткой
                            if stop_event.wait(60):
                                break

                except Exception as e:
                    logger.exception(f"Критическая ошибка в задаче {task_name}: {e}")
                finally:
                    logger.debug(f"Задача {task_name} завершена")

            # Создаем и запускаем поток
            thread = threading.Thread(target=periodic_wrapper, daemon=True, name=f"BackgroundTask-{task_name}")
            self._tasks[task_name] = thread
            thread.start()

            logger.info(f"Запущена периодическая задача: {task_name}")
            return True

    @log_exception
    def stop_task(self, task_name: str) -> bool:
        """
        Останавливает задачу.

        :param task_name: Имя задачи для остановки
        :return: True если задача остановлена, False если не найдена
        """
        with self._lock:
            if task_name not in self._tasks:
                logger.warning(f"Задача {task_name} не найдена")
                return False

            # Сигнализируем остановку
            if task_name in self._stop_events:
                self._stop_events[task_name].set()

            # Ждем завершения потока (максимум 5 секунд)
            thread = self._tasks[task_name]
            thread.join(timeout=5.0)

            # Удаляем из словарей
            del self._tasks[task_name]
            if task_name in self._stop_events:
                del self._stop_events[task_name]

            logger.info(f"Задача {task_name} остановлена")
            return True

    @log_exception
    def stop_all_tasks(self):
        """Останавливает все задачи"""
        task_names = list(self._tasks.keys())
        for task_name in task_names:
            self.stop_task(task_name)
        logger.info("Все фоновые задачи остановлены")

    def __del__(self):
        """Деструктор - останавливает все задачи при удалении объекта"""
        try:
            self.stop_all_tasks()
        except:
            pass  # Игнорируем ошибки при удалении