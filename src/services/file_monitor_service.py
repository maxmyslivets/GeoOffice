"""
Сервис мониторинга файлов базы данных GeoOffice.

Отслеживает изменения в файле базы данных geo_office.db и реагирует на события:
- создание, изменение, удаление файла базы данных
"""
import traceback
from pathlib import Path
from typing import Optional, Any

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Event, Thread

from src.utils.logger_config import get_logger, log_exception


logger = get_logger(__name__)


class FileMonitorService:
    """
    Сервис мониторинга файлов базы данных GeoOffice.
    
    Использует watchdog для отслеживания изменений в файле базы данных
    и реагирования на события, связанные с файлом geo_office.db.
    """
    
    def __init__(self, action_func: Any, database_path: str | Path) -> None:
        """
        Инициализация сервиса мониторинга файлов.
        
        Args:
            action_func: Сервис для синхронизации данных между базой данных и файловой системой
            database_path: Сервис для работы с базой данных
        """
        self.action_func = action_func
        # Путь к файлу базы данных
        self.database_path = Path(database_path)
        
        # Наблюдатель за файловой системой
        self.observer: Optional[Observer] = None
        self.monitored_path: Optional[Path] = None
        self.is_monitoring = False
        
        # События для управления мониторингом
        self._stop_event = Event()
        self._monitoring_thread: Optional[Thread] = None
        
        # Обработчик файловых событий
        self.file_handler: Optional['FileHandler'] = None

    @log_exception
    def start_monitoring(self) -> bool:
        """
        Запуск мониторинга файла базы данных.
        
        Returns:
            bool: True если мониторинг успешно запущен, False иначе
        """
        try:
            if self.is_monitoring:
                logger.info("Мониторинг файла базы данных уже запущен")
                return True
            
            # Получение пути к файлу базы данных для мониторинга
            self.monitored_path = self._get_monitored_path()
            if not self.monitored_path:
                logger.error("Не удалось получить путь к файлу базы данных для мониторинга")
                return False
            
            # Проверяем существование файла или его родительской директории
            if not self.monitored_path.exists() and not self.monitored_path.parent.exists():
                logger.warning(f"Файл базы данных и его родительская директория не существуют: {self.monitored_path}")
                return False
            
            # Настройка наблюдателя
            if not self._setup_observer():
                return False
            
            # Запуск мониторинга в отдельном потоке
            self._monitoring_thread = Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
            
            self.is_monitoring = True
            logger.info(f"Мониторинг файла базы данных запущен для пути: {self.monitored_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при запуске мониторинга файла базы данных: {e}")
            return False

    @log_exception
    def stop_monitoring(self) -> bool:
        """
        Остановка мониторинга файла базы данных.
        
        Returns:
            bool: True если мониторинг успешно остановлен, False иначе
        """
        try:
            if not self.is_monitoring:
                logger.info("Мониторинг файла базы данных не запущен")
                return True
            
            # Устанавливаем событие остановки
            self._stop_event.set()
            
            # Останавливаем наблюдателя
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
                if self.observer.is_alive():
                    logger.warning("Наблюдатель не остановился в течение таймаута")
                else:
                    logger.info("Наблюдатель успешно остановлен")
            
            # Ожидаем завершения потока мониторинга
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=3)
                if self._monitoring_thread.is_alive():
                    logger.warning("Поток мониторинга не завершился в течение таймаута")
            
            # Очистка ресурсов
            self._cleanup()
            
            self.is_monitoring = False
            logger.info("Мониторинг файла базы данных остановлен")
            return True
            
        except Exception:
            logger.error(f"Ошибка при остановке мониторинга файла базы данных: {traceback.format_exc()}")
            return False

    @log_exception
    def _get_monitored_path(self) -> Optional[Path]:
        """
        Получение пути к файлу базы данных для мониторинга.
        
        Returns:
            Optional[Path]: Путь к файлу базы данных или None если не найден
        """
        try:
            if self.database_path:
                return self.database_path
            else:
                logger.error(f"Путь к файлу базы данных не получен.")
                return None
        except Exception:
            logger.error(f"Ошибка при получении пути к файлу базы данных: {traceback.format_exc()}")
            return None

    @log_exception
    def _setup_observer(self) -> bool:
        """
        Настройка наблюдателя за файлом базы данных.
        
        Returns:
            bool: True если настройка успешна, False иначе
        """
        try:
            if not self.monitored_path:
                logger.error("Путь к файлу базы данных для мониторинга не установлен")
                return False
            
            # Создаем наблюдателя
            self.observer = Observer()
            
            # Создаем обработчик файловых событий
            self.file_handler = FileHandler(service=self)
            
            # Добавляем наблюдение за директорией, содержащей файл базы данных
            # Наблюдаем за родительской директорией для отслеживания создания/удаления файла БД
            monitor_dir = self.monitored_path.parent if self.monitored_path.is_file() else self.monitored_path
            self.observer.schedule(
                self.file_handler,
                str(monitor_dir),
                recursive=False  # Не нужен рекурсивный мониторинг для файла БД
            )
            
            # Запускаем наблюдателя
            self.observer.start()
            
            logger.info(f"Наблюдатель настроен для директории: {monitor_dir}")
            return True
            
        except Exception:
            logger.error(f"Ошибка при настройке наблюдателя: {traceback.format_exc()}")
            return False

    @log_exception
    def _cleanup(self):
        """Очистка ресурсов."""
        try:
            if self.observer:
                self.observer = None
            if self.file_handler:
                self.file_handler = None
            self.monitored_path = None
            self._monitoring_thread = None
            
        except Exception:
            logger.error(f"Ошибка при очистке ресурсов: {traceback.format_exc()}")

    @log_exception
    def _monitoring_loop(self):
        """Основной цикл мониторинга файла базы данных в отдельном потоке."""
        try:
            logger.info("Запущен цикл мониторинга файла базы данных")
            
            while not self._stop_event.is_set():
                # Проверяем состояние наблюдателя
                if self.observer and not self.observer.is_alive():
                    logger.warning("Наблюдатель остановился, перезапуск...")
                    try:
                        self.observer.join(timeout=1)
                        if not self._stop_event.is_set():
                            self._setup_observer()
                    except Exception:
                        logger.error(f"Ошибка при перезапуске наблюдателя: {traceback.format_exc()}")
                        break
                
                # Небольшая задержка для снижения нагрузки на CPU
                self._stop_event.wait(timeout=1)
            
            logger.info("Цикл мониторинга файла базы данных завершен")
            
        except Exception:
            logger.error(f"Критическая ошибка в цикле мониторинга: {traceback.format_exc()}")
        finally:
            self.is_monitoring = False

    @log_exception
    def handle_database_changed(self, file_path: Path) -> None:
        """
        Обработка события изменения файла базы данных.
        
        Args:
            file_path: Путь к файлу базы данных
        """
        try:
            # Проверяем, что измененный файл является файлом базы данных
            if file_path == self.database_path:
                logger.info(f"Обнаружено изменение файла базы данных: `{file_path}`")
                self.action_func()
        except Exception:
            logger.error(f"Ошибка при обработке изменения файла базы данных `{file_path}`: "
                         f"{traceback.format_exc()}")


class FileHandler(FileSystemEventHandler):
    """
    Обработчик файловых событий для файла базы данных GeoOffice.
    
    Перехватывает события файловой системы и делегирует обработку
    соответствующим методам FileMonitorService.
    """
    
    def __init__(self, service: 'FileMonitorService'):
        """
        Инициализация обработчика файловых событий.
        
        Args:
            service: Сервис мониторинга файлов
        """
        self.service = service
        super().__init__()

    @log_exception
    def on_modified(self, event):
        """Обработка события изменения файла."""
        logger.debug(f"Событие изменения: `{event.src_path}`")
        self.service.handle_database_changed(Path(event.src_path))
