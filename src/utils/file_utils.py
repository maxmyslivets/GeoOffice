import os
import json
import subprocess
import platform
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
    def save_json(data: Dict[str, Any], filename: str | Path) -> bool:
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
    def load_json(filename: str | Path) -> Optional[Dict[str, Any]]:
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

    @staticmethod
    @log_exception
    def open_in_explorer(path):
        """
        Открывает указанный путь в проводнике/файловом менеджере ОС.
        :param path: str
        """
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer /select,"{path}"')
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-R", path])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(path)])

    @staticmethod
    @log_exception
    def open_folder(path):
        """
        Открывает указанный путь в проводнике/файловом менеджере ОС.
        :param path: str
        """
        subprocess.Popen(f'explorer "{path}"')

    @staticmethod
    @log_exception
    def manage_file_attributes(file_path: str, action: str = "show") -> Dict[str, Any]:
        """
        Управление атрибутами файла в Windows.
        :param file_path: Путь к файлу
        :param action: Действие ("show", "hide", "protect", "unprotect")
        :return: Словарь с результатом
        """
        path = Path(file_path)
        result = {
            'file_path': str(path),
            'exists': path.exists(),
            'action': action,
            'success': False,
            'attributes_before': None,
            'attributes_after': None,
            'error': None
        }

        if not path.exists():
            result['error'] = "Файл не существует"
            return result

        try:
            # Получаем атрибуты до изменения
            attrib_result = subprocess.run(['attrib', str(path)],
                                           capture_output=True, text=True, check=True)
            result['attributes_before'] = attrib_result.stdout.strip()

            # Выполняем действие
            if action == "show":
                # Сделать видимым (снять скрытый и системный)
                subprocess.run(['attrib', '-h', '-s', str(path)], check=True)
                result['message'] = "Файл сделан видимым"

            elif action == "hide":
                # Сделать скрытым
                subprocess.run(['attrib', '+h', str(path)], check=True)
                result['message'] = "Файл скрыт"

            elif action == "protect":
                # Защитить (скрытый + системный)
                subprocess.run(['attrib', '+h', '+s', str(path)], check=True)
                result['message'] = "Файл защищен"

            elif action == "unprotect":
                # Снять защиту
                subprocess.run(['attrib', '-h', '-s', '-r', str(path)], check=True)
                result['message'] = "Защита снята"

            # Получаем атрибуты после изменения
            attrib_result = subprocess.run(['attrib', str(path)],
                                           capture_output=True, text=True, check=True)
            result['attributes_after'] = attrib_result.stdout.strip()
            result['success'] = True

        except subprocess.CalledProcessError as e:
            result['error'] = f"Ошибка выполнения команды: {e}"
        except Exception as e:
            result['error'] = f"Неожиданная ошибка: {e}"

        return result
