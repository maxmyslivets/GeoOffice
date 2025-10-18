import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional, Set, Dict, Any
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

from utils.logger_config import get_logger, log_exception
from config.file_watch_config import (
    DEFAULT_IGNORED_PATTERNS, 
    PROJECT_FILE_EXTENSIONS, 
    DEFAULT_PERFORMANCE_SETTINGS,
    LOGGING_SETTINGS
)

logger = get_logger("services.file_watch_service")
file_monitor_logger = get_logger("file_monitor")


class ProjectFileHandler(FileSystemEventHandler):
    """
    Обработчик событий файловой системы для проектов GeoOffice.
    Отслеживает изменения в файлах .geo_office_project и связанных папках.
    """
    
    def __init__(self, callback: Callable[[str, str, str], None], 
                 project_extensions: Set[str] = None,
                 debounce_time: float = 1.0,
                 ignored_patterns: Set[str] = None):
        """
        Инициализация обработчика событий.
        
        :param callback: Функция обратного вызова для обработки событий
        :param project_extensions: Расширения файлов для отслеживания
        :param debounce_time: Время задержки для группировки событий (секунды)
        :param ignored_patterns: Паттерны файлов для игнорирования
        """
        super().__init__()
        self.callback = callback
        self.project_extensions = project_extensions or PROJECT_FILE_EXTENSIONS
        self.debounce_time = debounce_time
        self.ignored_patterns = ignored_patterns or DEFAULT_IGNORED_PATTERNS
        self._pending_events: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._timer: Optional[threading.Timer] = None
        self._last_processed: Dict[str, float] = {}  # Для предотвращения дублирования
        
        logger.info(f"Инициализирован обработчик файловых событий с задержкой {debounce_time}с")

    def _is_project_file(self, file_path: str) -> bool:
        """Проверяет, является ли файл файлом проекта."""
        path = Path(file_path)
        return path.name in self.project_extensions

    def _is_project_directory(self, file_path: str) -> bool:
        """Проверяет, находится ли файл в директории проекта."""
        path = Path(file_path)
        return any((path.parent / ext).exists() for ext in self.project_extensions)

    def _should_ignore_file(self, file_path: str) -> bool:
        """Проверяет, нужно ли игнорировать файл."""
        path = Path(file_path)
        
        # Проверяем паттерны игнорирования
        for pattern in self.ignored_patterns:
            if pattern.startswith('*.'):
                # Расширение файла
                if path.suffix == pattern[1:]:
                    return True
            elif pattern.startswith('.'):
                # Скрытые файлы/папки
                if path.name.startswith(pattern):
                    return True
            else:
                # Точное совпадение имени
                if path.name == pattern:
                    return True
                    
        return False

    def _is_duplicate_event(self, event_type: str, src_path: str, dest_path: str = None) -> bool:
        """Проверяет, является ли событие дубликатом недавно обработанного."""
        current_time = time.time()
        key = f"{event_type}:{src_path}:{dest_path or ''}"
        
        if key in self._last_processed:
            # Если событие было обработано менее 5 секунд назад, считаем дубликатом
            if current_time - self._last_processed[key] < 5.0:
                return True
                
        self._last_processed[key] = current_time
        
        # Очищаем старые записи (старше 60 секунд)
        old_keys = [k for k, t in self._last_processed.items() if current_time - t > 60.0]
        for k in old_keys:
            del self._last_processed[k]
            
        return False

    def _should_process_event(self, event) -> bool:
        """Определяет, нужно ли обрабатывать событие."""
        if event.is_directory:
            return False
            
        # Игнорируем файлы по паттернам
        if self._should_ignore_file(event.src_path):
            return False
            
        # Проверяем на дубликаты
        dest_path = getattr(event, 'dest_path', None)
        if self._is_duplicate_event(event.event_type, event.src_path, dest_path):
            return False
            
        # Обрабатываем только файлы проектов или файлы в директориях проектов
        return (self._is_project_file(event.src_path) or 
                self._is_project_directory(event.src_path))

    def _debounce_event(self, event_type: str, src_path: str, dest_path: str = None):
        """Группирует события с задержкой для предотвращения множественных вызовов."""
        with self._lock:
            key = src_path
            self._pending_events[key] = {
                'event_type': event_type,
                'src_path': src_path,
                'dest_path': dest_path,
                'timestamp': time.time()
            }
            
            # Отменяем предыдущий таймер
            if self._timer:
                self._timer.cancel()
            
            # Устанавливаем новый таймер
            self._timer = threading.Timer(self.debounce_time, self._process_pending_events)
            self._timer.start()

    def _process_pending_events(self):
        """Обрабатывает накопленные события."""
        with self._lock:
            if not self._pending_events:
                return
                
            events_to_process = self._pending_events.copy()
            self._pending_events.clear()
            
        # Обрабатываем события
        for event_data in events_to_process.values():
            try:
                self.callback(
                    event_data['event_type'],
                    event_data['src_path'],
                    event_data.get('dest_path')
                )
            except Exception as e:
                logger.error(f"Ошибка при обработке события {event_data}: {e}")

    def on_created(self, event):
        """Обработка события создания файла."""
        if self._should_process_event(event):
            file_monitor_logger.info(f"FILE_CREATED: {event.src_path}")
            logger.info(f"Создан файл: {event.src_path}")
            self._debounce_event('created', event.src_path)
        else:
            if LOGGING_SETTINGS.get('log_ignored_events', False):
                file_monitor_logger.debug(f"IGNORED_CREATE: {event.src_path}")
            logger.debug(f"Игнорировано создание файла: {event.src_path}")

    def on_deleted(self, event):
        """Обработка события удаления файла."""
        if self._should_process_event(event):
            file_monitor_logger.info(f"FILE_DELETED: {event.src_path}")
            logger.info(f"Удален файл: {event.src_path}")
            self._debounce_event('deleted', event.src_path)
        else:
            if LOGGING_SETTINGS.get('log_ignored_events', False):
                file_monitor_logger.debug(f"IGNORED_DELETE: {event.src_path}")
            logger.debug(f"Игнорировано удаление файла: {event.src_path}")

    def on_modified(self, event):
        """Обработка события изменения файла."""
        if self._should_process_event(event):
            file_monitor_logger.info(f"FILE_MODIFIED: {event.src_path}")
            logger.info(f"Изменен файл: {event.src_path}")
            self._debounce_event('modified', event.src_path)
        else:
            if LOGGING_SETTINGS.get('log_ignored_events', False):
                file_monitor_logger.debug(f"IGNORED_MODIFY: {event.src_path}")
            logger.debug(f"Игнорировано изменение файла: {event.src_path}")

    def on_moved(self, event):
        """Обработка события перемещения файла."""
        if self._should_process_event(event):
            file_monitor_logger.info(f"FILE_MOVED: {event.src_path} -> {event.dest_path}")
            logger.info(f"Перемещен файл: {event.src_path} -> {event.dest_path}")
            self._debounce_event('moved', event.src_path, event.dest_path)
        else:
            if LOGGING_SETTINGS.get('log_ignored_events', False):
                file_monitor_logger.debug(f"IGNORED_MOVE: {event.src_path} -> {event.dest_path}")
            logger.debug(f"Игнорировано перемещение файла: {event.src_path} -> {event.dest_path}")


class FileWatchService:
    """
    Сервис для мониторинга изменений в файловой системе проектов.
    Использует watchdog для отслеживания изменений в реальном времени.
    """
    
    def __init__(self, watch_paths: Set[str], 
                 sync_callback: Callable[[str, str, str], None],
                 debounce_time: float = 2.0,
                 max_events_per_second: int = 10):
        """
        Инициализация сервиса мониторинга.
        
        :param watch_paths: Пути для мониторинга
        :param sync_callback: Функция обратного вызова для синхронизации
        :param debounce_time: Время задержки для группировки событий
        :param max_events_per_second: Максимальное количество событий в секунду
        """
        self.watch_paths = {Path(p) for p in watch_paths}
        self.sync_callback = sync_callback
        self.debounce_time = debounce_time
        self.max_events_per_second = max_events_per_second
        
        self.observer = Observer()
        self.handler = ProjectFileHandler(
            callback=self._handle_file_event,
            debounce_time=debounce_time,
            ignored_patterns=DEFAULT_IGNORED_PATTERNS
        )
        
        self.is_running = False
        self._lock = threading.Lock()
        self._event_count = 0
        self._last_reset_time = time.time()
        
        logger.info(f"Инициализирован сервис мониторинга файлов для путей: {watch_paths}")

    def _handle_file_event(self, event_type: str, src_path: str, dest_path: str = None):
        """
        Обработка события файловой системы.
        
        :param event_type: Тип события (created, deleted, modified, moved)
        :param src_path: Исходный путь файла
        :param dest_path: Путь назначения (для события moved)
        """
        try:
            # Проверяем ограничение скорости
            if not self._check_rate_limit():
                if LOGGING_SETTINGS.get('log_rate_limiting', True):
                    file_monitor_logger.warning(f"RATE_LIMIT_EXCEEDED: {event_type}: {src_path}")
                logger.debug(f"Событие пропущено из-за ограничения скорости: {event_type}: {src_path}")
                return
                
            if LOGGING_SETTINGS.get('log_file_events', True):
                file_monitor_logger.info(f"PROCESSING_EVENT: {event_type}: {src_path}")
            logger.info(f"Обработка события {event_type}: {src_path}")
            
            # Вызываем callback для синхронизации
            start_time = time.time()
            self.sync_callback(event_type, src_path, dest_path)
            processing_time = time.time() - start_time
            
            if LOGGING_SETTINGS.get('log_performance_stats', True):
                file_monitor_logger.info(f"EVENT_PROCESSED: {event_type}: {src_path} (took {processing_time:.3f}s)")
            logger.debug(f"Событие обработано за {processing_time:.3f} секунд")
            
        except Exception as e:
            file_monitor_logger.error(f"EVENT_ERROR: {event_type}: {src_path}: {e}")
            logger.error(f"Ошибка при обработке события файла {src_path}: {e}")

    def _check_rate_limit(self) -> bool:
        """
        Проверяет ограничение скорости обработки событий.
        
        :return: True если событие можно обработать, False если превышен лимит
        """
        current_time = time.time()
        
        # Сбрасываем счетчик каждую секунду
        if current_time - self._last_reset_time >= 1.0:
            self._event_count = 0
            self._last_reset_time = current_time
        
        # Проверяем лимит
        if self._event_count >= self.max_events_per_second:
            return False
            
        self._event_count += 1
        return True

    @log_exception
    def start(self) -> bool:
        """
        Запуск мониторинга файловой системы.
        
        :return: True если мониторинг запущен успешно
        """
        with self._lock:
            if self.is_running:
                logger.warning("Мониторинг файлов уже запущен")
                return False
            
            try:
                # Добавляем наблюдателей для каждого пути
                for watch_path in self.watch_paths:
                    if not watch_path.exists():
                        logger.warning(f"Путь для мониторинга не существует: {watch_path}")
                        continue
                        
                    self.observer.schedule(
                        self.handler, 
                        str(watch_path), 
                        recursive=True
                    )
                    logger.info(f"Добавлен мониторинг для пути: {watch_path}")
                
                # Запускаем наблюдатель
                self.observer.start()
                self.is_running = True
                
                file_monitor_logger.info(f"WATCH_SERVICE_STARTED: paths={[str(p) for p in self.watch_paths]}")
                logger.info("Мониторинг файловой системы запущен")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка при запуске мониторинга: {e}")
                return False

    @log_exception
    def stop(self) -> bool:
        """
        Остановка мониторинга файловой системы.
        
        :return: True если мониторинг остановлен успешно
        """
        with self._lock:
            if not self.is_running:
                logger.warning("Мониторинг файлов не запущен")
                return False
            
            try:
                self.observer.stop()
                self.observer.join(timeout=5.0)
                self.is_running = False
                
                file_monitor_logger.info("WATCH_SERVICE_STOPPED")
                logger.info("Мониторинг файловой системы остановлен")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка при остановке мониторинга: {e}")
                return False

    @log_exception
    def add_watch_path(self, path: str) -> bool:
        """
        Добавление нового пути для мониторинга.
        
        :param path: Путь для добавления
        :return: True если путь добавлен успешно
        """
        watch_path = Path(path)
        if not watch_path.exists():
            logger.warning(f"Путь для мониторинга не существует: {watch_path}")
            return False
        
        if watch_path in self.watch_paths:
            logger.warning(f"Путь уже отслеживается: {watch_path}")
            return False
        
        try:
            self.observer.schedule(
                self.handler, 
                str(watch_path), 
                recursive=True
            )
            self.watch_paths.add(watch_path)
            logger.info(f"Добавлен мониторинг для пути: {watch_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении пути мониторинга {watch_path}: {e}")
            return False

    @log_exception
    def remove_watch_path(self, path: str) -> bool:
        """
        Удаление пути из мониторинга.
        
        :param path: Путь для удаления
        :return: True если путь удален успешно
        """
        watch_path = Path(path)
        if watch_path not in self.watch_paths:
            logger.warning(f"Путь не отслеживается: {watch_path}")
            return False
        
        try:
            # Находим и удаляем наблюдателя для этого пути
            for watch in self.observer.watches:
                if str(watch_path) in watch.path:
                    self.observer.unschedule(watch)
                    break
            
            self.watch_paths.discard(watch_path)
            logger.info(f"Удален мониторинг для пути: {watch_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при удалении пути мониторинга {watch_path}: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Получение статуса сервиса мониторинга.
        
        :return: Словарь со статусом
        """
        return {
            'is_running': self.is_running,
            'watch_paths': [str(p) for p in self.watch_paths],
            'debounce_time': self.debounce_time,
            'max_events_per_second': self.max_events_per_second,
            'current_events_per_second': self._event_count,
            'observer_alive': self.observer.is_alive() if hasattr(self.observer, 'is_alive') else False
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Получение статистики производительности.
        
        :return: Словарь со статистикой
        """
        current_time = time.time()
        time_since_reset = current_time - self._last_reset_time
        
        return {
            'events_in_current_second': self._event_count,
            'time_since_reset': time_since_reset,
            'max_events_per_second': self.max_events_per_second,
            'rate_limit_active': self._event_count >= self.max_events_per_second,
            'total_watch_paths': len(self.watch_paths),
            'debounce_time': self.debounce_time
        }

    def __del__(self):
        """Деструктор - останавливает мониторинг при удалении объекта."""
        try:
            if self.is_running:
                self.stop()
        except:
            pass  # Игнорируем ошибки при удалении