import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from src.utils.logger_config import get_logger, log_exception

logger = get_logger("utils.files")


class FileUtils:
    """
    Утилиты для работы с файлами: сохранение, загрузка, проверка, создание директорий и получение информации о файлах.
    """
    
    @staticmethod
    @log_exception
    def save_json(data: Dict[str, Any], filename: str) -> bool:
        """
        Сохраняет данные в JSON-файл.
        :param data: Словарь с данными
        :param filename: Имя файла для сохранения
        :return: True, если успешно, иначе False
        """
        logger.debug(f"💾 Сохранение JSON файла: {filename}")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ JSON файл сохранен: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения файла {filename}: {str(e)}")
            return False
    
    @staticmethod
    @log_exception
    def load_json(filename: str) -> Optional[Dict[str, Any]]:
        """
        Загружает данные из JSON-файла.
        :param filename: Имя файла для загрузки
        :return: Словарь с данными или None, если ошибка
        """
        """Загрузка данных из JSON файла"""
        logger.debug(f"📂 Загрузка JSON файла: {filename}")
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"✅ JSON файл загружен: {filename}")
                    return data
            else:
                logger.warning(f"⚠️ Файл не найден: {filename}")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON файла {filename}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки файла {filename}: {str(e)}")
            return None
    
    @staticmethod
    @log_exception
    def ensure_directory(path: str) -> bool:
        """Создание директории, если она не существует"""
        logger.debug(f"📁 Проверка/создание директории: {path}")
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            logger.debug(f"✅ Директория готова: {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка создания директории {path}: {str(e)}")
            return False
    
    @staticmethod
    @log_exception
    def get_file_extension(filename: str) -> str:
        """Получение расширения файла"""
        ext = os.path.splitext(filename)[1].lower()
        logger.debug(f"🔍 Получение расширения файла {filename}: {ext}")
        return ext
    
    @staticmethod
    @log_exception
    def is_valid_file(filename: str, allowed_extensions: list) -> bool:
        """Проверка валидности файла по расширению"""
        ext = FileUtils.get_file_extension(filename)
        logger.debug(f"🔍 Проверка валидности файла {filename} по расширению: {ext in allowed_extensions}")
        return ext in allowed_extensions
    
    @staticmethod
    @log_exception
    def file_exists(file_path: str) -> bool:
        """Проверка существования файла"""
        exists = os.path.exists(file_path)
        logger.debug(f"🔍 Проверка файла {file_path}: {'существует' if exists else 'не существует'}")
        return exists
    
    @staticmethod
    @log_exception
    def get_file_size(file_path: str) -> int:
        """Получение размера файла в байтах"""
        try:
            size = os.path.getsize(file_path)
            logger.debug(f"📏 Размер файла {file_path}: {size} байт")
            return size
        except Exception as e:
            logger.error(f"❌ Ошибка получения размера файла {file_path}: {str(e)}")
            return 0 