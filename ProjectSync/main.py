import uuid
from datetime import datetime
from typing import Any

import pystray
from pony.orm import Database as PonyDatabase
from pony.orm import PrimaryKey, Optional, Required, db_session
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import ttk, filedialog
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import threading
import time
import json


class GeoOfficeProjectSyncTrayApp:
    """Класс приложения для трея GeoOffice_ProjectSync с логированием, ротацией и периодической синхронизацией."""

    def __init__(self):
        self.is_running = False
        self.server_path = ""
        self.database_path = ""
        self.sync_period = 5  # временно фиксированное значение, позже будет читаться из базы
        self._sync_thread = None
        self._stop_event = threading.Event()

        # Настройка путей
        self.documents_path = Path(os.path.expanduser("~/Documents"))
        self.geooffice_dir = self.documents_path / "GeoOffice"
        self.geooffice_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.geooffice_dir / "settings.json"

        # Настраиваем логирование
        self._setup_logging()

        # Загружаем сохранённые настройки (если есть)
        self._load_settings()

        # Создаем иконку
        self.icon = pystray.Icon(
            name='GeoOffice_ProjectSync',
            title='GeoOffice Синхронизация проектов',
            icon=self._draw_icon(),
            menu=self._create_menu()
        )

    # --- Логирование --------------------------------------------------------

    def _setup_logging(self):
        """Настройка логирования в файл и консоль с ротацией (до 5 архивов по 5 МБ)."""
        try:
            log_file = self.geooffice_dir / "GeoOffice_ProjectSync.log"

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5 МБ
                backupCount=5,             # до 5 архивов
                encoding='utf-8'
            )

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                handlers=[file_handler, console_handler]
            )

            logging.info("Приложение GeoOffice_ProjectSync запущено.")
        except Exception as e:
            print(f"Ошибка при настройке логирования: {e}")

    # --- Методы работы с настройками ---------------------------------------

    def _save_settings(self):
        """Сохраняет настройки (только путь к серверу) в JSON файл."""
        try:
            data = {"server_path": self.server_path, "database_path": self.database_path}
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Настройки сохранены в {self.settings_file}")
        except Exception as e:
            logging.exception("Ошибка при сохранении настроек")

    def _load_settings(self):
        """Загружает настройки (если файл существует)."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.server_path = data.get("server_path", "")
                self.database_path = data.get("database_path", "")
                logging.info(f"Настройки загружены: сервер = {self.server_path or 'не задан'}")
            else:
                logging.info("Файл настроек не найден, используется конфигурация по умолчанию.")
        except Exception as e:
            logging.exception("Ошибка при загрузке настроек")

    # --- Методы действий ----------------------------------------------------

    def start_action(self, icon, menu_item):
        try:
            if not self.is_running:
                logging.info(f"Синхронизация запущена (сервер: {self.server_path or 'не задан'}, период: {self.sync_period} мин)")
                self.is_running = True
                self._stop_event.clear()
                self._start_sync_loop()
                self._update_menu()
                self.icon.title = 'GeoOffice Синхронизация проектов запущена'
        except Exception as e:
            logging.exception("Ошибка при запуске синхронизации")

    def stop_action(self, icon, menu_item):
        try:
            if self.is_running:
                logging.info("Синхронизация остановлена пользователем.")
                self.is_running = False
                self._stop_event.set()
                self._update_menu()
                self.icon.title = 'GeoOffice Синхронизация проектов остановлена'
        except Exception as e:
            logging.exception("Ошибка при остановке синхронизации")

    def settings_action(self, icon, menu_item):
        """Открывает окно настроек."""
        try:
            self._open_settings_window()
        except Exception as e:
            logging.exception("Ошибка при открытии окна настроек")

    def exit_action(self, icon, menu_item):
        try:
            logging.info("Выход из приложения...")
            self._stop_event.set()
            self.icon.stop()
        except Exception as e:
            logging.exception("Ошибка при выходе из приложения")

    # --- Цикл синхронизации -------------------------------------------------

    def _start_sync_loop(self):
        """Запускает фоновый поток для периодической синхронизации."""
        def sync_loop():
            while not self._stop_event.is_set():
                try:
                    self._run_sync_projects()
                except Exception as e:
                    logging.exception("Ошибка во время синхронизации проектов")
                # Ждём указанное количество минут
                if not self._stop_event.wait(self.sync_period * 60):
                    continue
                else:
                    break

        self._sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self._sync_thread.start()

    def _run_sync_projects(self):
        """Заглушка для процесса синхронизации (сюда добавить реальную логику)."""
        if not self.server_path:
            logging.warning("Сервер не задан. Синхронизация пропущена.")
            return

        logging.info(f"Выполняется синхронизация с сервером: {self.server_path}")
        # Здесь будет логика синхронизации проектов
        db = Database(Path(self.server_path) / self.database_path)
        self.sync_period = db.get_period()
        projects_from_db = db.get_all_projects()
        projects_from_fs = self._scan_files(path=Path(self.server_path) / db.get_project_dir(),
                                            template_exc_path=db.get_template_dir())
        self._sync_projects(projects_from_db, projects_from_fs)
        logging.info("Синхронизация завершена успешно.")

    def _scan_files(self, path: Path|str, template_exc_path: Path|str) -> dict[str, str]:
        result = {}
        for file in path.rglob(".geo_office_project"):
            if file.parent == path / template_exc_path:
                continue
            with file.open("r", encoding="utf-8") as f:
                data = f.read()
            result[str(file.parent.relative_to(path))] = data
        return result

    def _is_uid(self, uid: str) -> bool:
        try:
            uuid.UUID("{" + f"{uid}" + "}")
            return True
        except ValueError:
            return False

    def _add_uid_to_file(self, path: str, uid: str) -> None:
        """Добавляет UID в файл .geo_office_project."""
        try:
            # Получаем путь к папке проектов из настроек БД
            db = Database(Path(self.server_path) / self.database_path)
            project_dir = db.get_project_dir()
            project_path = Path(self.server_path) / project_dir / path / ".geo_office_project"
            
            with project_path.open("w", encoding="utf-8") as f:
                f.write(uid)
            logging.debug(f"UID {uid} записан в файл {project_path}")
        except Exception as e:
            logging.exception(f"Ошибка при записи UID в файл {path}: {e}")
            raise

    def _get_uid_from_file(self, path: str) -> str:
        """Получает UID из файла .geo_office_project."""
        try:
            # Получаем путь к папке проектов из настроек БД
            db = Database(Path(self.server_path) / self.database_path)
            project_dir = db.get_project_dir()
            project_path = Path(self.server_path) / project_dir / path / ".geo_office_project"
            
            if project_path.exists():
                with project_path.open("r", encoding="utf-8") as f:
                    uid = f.read().strip()
                return uid
            return ""
        except Exception as e:
            logging.exception(f"Ошибка при чтении UID из файла {path}: {e}")
            return ""

    def _find_file_by_uid(self, uid: str) -> str:
        """Находит путь к файлу проекта по UID."""
        try:
            db = Database(Path(self.server_path) / self.database_path)
            project_dir = db.get_project_dir()
            projects_path = Path(self.server_path) / project_dir
            
            for file in projects_path.rglob(".geo_office_project"):
                with file.open("r", encoding="utf-8") as f:
                    file_uid = f.read().strip()
                if file_uid == uid:
                    return str(file.parent.relative_to(projects_path))
            return ""
        except Exception as e:
            logging.exception(f"Ошибка при поиске файла по UID {uid}: {e}")
            return ""

    def _sync_projects(self, in_database: dict[str: str], in_files: dict[str: str]) -> None:
        """
        Синхронизирует проекты между базой данных и файловой системой на основе UID.
        
        Новая логика синхронизации:
        1. Собираем все UID из БД и файлов
        2. Для каждого UID проверяем:
           - Если UID есть в БД и в файлах - проверяем соответствие путей
           - Если UID есть только в БД - ищем файл по UID, если не найден - удаляем из БД
           - Если UID есть только в файлах - добавляем в БД
        3. Для файлов без UID - создаем новый проект с новым UID
        """
        db = Database(Path(self.server_path) / self.database_path)
        
        # Собираем все UID из БД и файлов
        db_uids = set()
        file_uids = set()
        
        # UID из БД
        for path, uid in in_database.items():
            if self._is_uid(uid):
                db_uids.add(uid)
        
        # UID из файлов
        for path, uid in in_files.items():
            if self._is_uid(uid):
                file_uids.add(uid)
        
        # Обрабатываем UID, которые есть и в БД, и в файлах
        common_uids = db_uids & file_uids
        for uid in common_uids:
            try:
                # Находим путь в БД и в файлах для этого UID
                db_path = None
                file_path = None
                
                for path, path_uid in in_database.items():
                    if path_uid == uid:
                        db_path = path
                        break
                
                for path, path_uid in in_files.items():
                    if path_uid == uid:
                        file_path = path
                        break
                
                if db_path and file_path:
                    if db_path != file_path:
                        # Пути не совпадают - обновляем путь в БД
                        db.update_project_path(uid, file_path)
                        logging.info(f"Обновлен путь проекта {uid}: {db_path} -> {file_path}")
                    else:
                        # Всё синхронизировано
                        logging.debug(f"Проект {uid} уже синхронизирован")
                        
            except Exception as e:
                logging.exception(f"Ошибка при синхронизации UID {uid}: {e}")
                continue
        
        # Обрабатываем UID, которые есть только в БД
        db_only_uids = db_uids - file_uids
        for uid in db_only_uids:
            try:
                # Ищем файл по UID
                found_file_path = self._find_file_by_uid(uid)
                if found_file_path:
                    # Файл найден - обновляем путь в БД
                    db.update_project_path(uid, found_file_path)
                    logging.info(f"Найден файл для UID {uid}, обновлен путь: {found_file_path}")
                else:
                    # Файл не найден - удаляем из БД
                    db.delete_project_by_uid(uid)
                    logging.info(f"Удален проект из БД (файл не найден): {uid}")
                    
            except Exception as e:
                logging.exception(f"Ошибка при обработке UID только в БД {uid}: {e}")
                continue
        
        # Обрабатываем UID, которые есть только в файлах
        file_only_uids = file_uids - db_uids
        for uid in file_only_uids:
            try:
                # Находим путь к файлу
                file_path = None
                for path, path_uid in in_files.items():
                    if path_uid == uid:
                        file_path = path
                        break
                
                if file_path:
                    # Добавляем в БД
                    db.create_project(file_path, uid)
                    logging.info(f"Добавлен новый проект в БД: {file_path} (UID: {uid})")
                    
            except Exception as e:
                logging.exception(f"Ошибка при обработке UID только в файлах {uid}: {e}")
                continue
        
        # Обрабатываем файлы без UID
        for path, uid in in_files.items():
            if not self._is_uid(uid):
                try:
                    # Создаем новый UID и добавляем в файл и БД
                    new_uid = str(uuid.uuid4())
                    self._add_uid_to_file(path, new_uid)
                    db.create_project(path, new_uid)
                    logging.info(f"Создан новый проект: {path} (UID: {new_uid})")
                    
                except Exception as e:
                    logging.exception(f"Ошибка при создании нового проекта {path}: {e}")
                    continue

    # --- Интерфейс ----------------------------------------------------------

    def _create_menu(self):
        return (
            item('Старт', self.start_action, enabled=not self.is_running),
            item('Стоп', self.stop_action, enabled=self.is_running),
            item('Настройки', self.settings_action),
            item('Выход', self.exit_action)
        )

    def _update_menu(self):
        self.icon.menu = pystray.Menu(*self._create_menu())
        self.icon.update_menu()

    # --- Окно настроек ------------------------------------------------------

    def _open_settings_window(self):
        """Создает и показывает окно настроек."""
        def browse_folder():
            path = filedialog.askdirectory(title="Выберите папку с проектами")
            if path:
                server_var.set(path)

        def save_settings():
            try:
                self.server_path = server_var.get().strip()
                self.database_path = database_var.get().strip()
                self._save_settings()
                settings_win.destroy()
            except Exception as e:
                logging.exception("Ошибка при сохранении настроек")

        settings_win = tk.Tk()
        settings_win.title("Настройки синхронизации")
        settings_win.geometry("400x180")
        settings_win.resizable(False, False)

        tk.Label(settings_win, text="Путь к файловому серверу:").pack(anchor='w', padx=10, pady=(10, 0))
        server_var = tk.StringVar(value=self.server_path)
        path_frame = tk.Frame(settings_win)
        path_frame.pack(fill='x', padx=10)
        tk.Entry(path_frame, textvariable=server_var).pack(side='left', fill='x', expand=True)
        ttk.Button(path_frame, text="Обзор...", command=browse_folder).pack(side='right', padx=5)

        # Период синхронизации
        tk.Label(settings_win, text="Имя базы данных:").pack(anchor='w', padx=10, pady=(10, 0))
        database_var = tk.StringVar(value=str(self.database_path))
        ttk.Entry(settings_win, textvariable=database_var, width=30).pack(padx=10, anchor='w')

        ttk.Button(settings_win, text="Сохранить", command=save_settings).pack(pady=20)
        settings_win.mainloop()

    # --- Отрисовка иконки --------------------------------------------------

    def _draw_icon(self) -> Image:
        img = Image.new('RGB', (64, 64), '#ffffff')
        draw = ImageDraw.Draw(img)

        for y in range(64):
            r = int(0x42 + (0x7e - 0x42) * y / 64)
            g = int(0xa5 + (0x57 - 0xa5) * y / 64)
            b = int(0xf5 + (0xc2 - 0xf5) * y / 64)
            draw.line([(0, y), (64, y)], fill=(r, g, b))

        draw.rounded_rectangle([2, 2, 62, 62], radius=6, outline="#00796b", width=1)
        draw.line([(12, 32), (52, 32)], fill="#004d40", width=1)
        draw.line([(32, 12), (32, 52)], fill="#004d40", width=1)
        draw.ellipse([22, 22, 42, 42], outline="#004d40", width=1)
        draw.line([(26, 15), (32, 5), (38, 15)], fill="#ff7043", width=1)
        draw.line([(28, 10), (36, 10)], fill="#ff7043", width=1)
        draw.arc([24, 24, 40, 40], start=200, end=340, fill="#ff7043", width=1)
        draw.arc([16, 16, 48, 48], start=160, end=300, fill="#ff7043", width=2)
        draw.polygon([(16, 28), (20, 24), (20, 30)], fill="#ff7043")
        draw.arc([16, 16, 48, 48], start=-20, end=120, fill="#ff7043", width=2)
        draw.polygon([(48, 36), (44, 40), (44, 34)], fill="#ff7043")
        return img

    # --- Запуск -------------------------------------------------------------

    def run(self, detached: bool = True):
        try:
            if detached:
                self.icon.run_detached()
            else:
                self.icon.run()
            self.start_action(None, None)
        except Exception as e:
            logging.exception("Ошибка при запуске приложения")


class Database:
    def __init__(self, path: Path|str):
        """
        Инициализация моделей базы данных.
        :param db: Экземпляр базы данных Pony ORM
        """
        self.db = PonyDatabase()
        self.db.bind(provider='sqlite', filename=str(path))
        self.models = self._define_models()
        self.db.generate_mapping(check_tables=True, create_tables=True)

    def _define_models(self) -> Any:
        """Определение моделей таблиц базы данных"""
        class ProjectTable(self.db.Entity):
            """
            Модель таблицы проектов.
            Основная таблица для хранения информации о проектах.
            """
            _table_ = "Объекты"
            id = PrimaryKey(int, auto=True)
            name = Required(str)  # Название проекта
            path = Required(str)    # Путь к папке проекта
            uid = Required(str)     # Уникальный идентификатор
            created_date = Required(datetime, default=datetime.now)
            modified_date = Required(datetime, default=datetime.now)

        class SettingsTable(self.db.Entity):
            """
            Модель таблицы настроек.
            """
            _table_ = "Настройки"
            id = PrimaryKey(int, auto=True)
            project_dir = Optional(str, nullable=False)     # путь к папке объектов относительно файлового сервера
            template_project_dir = Optional(str, nullable=False)    # путь к папке шаблона объектов относительно
                                                                    # файлового сервера
            period_sync_project = Optional(int, nullable=True)  # период синхронизации в минутах

        class Models:
            Project = ProjectTable
            Settings = SettingsTable

        return Models

    @db_session
    def get_period(self) -> int:
        return self.models.Settings[1].period_sync_project

    @db_session
    def get_project_dir(self) -> str:
        return self.models.Settings[1].project_dir

    @db_session
    def get_template_dir(self) -> str:
        return self.models.Settings[1].template_project_dir

    @db_session
    def get_all_projects(self) -> dict[str: str]:
        projects = self.models.Project.select()[:]
        result = {}
        for project in projects:
            result[project.path] = project.uid
        return result

    @db_session
    def create_project(self, path: Path | str, uid: str) -> Any:
        path = str(path)
        name = path.split("/")[-1]
        path = path[:-len(name)]
        project = self.models.Project(name=name, path=path, uid=uid)
        return project

    @db_session
    def update_project_uid(self, path: str, uid: str) -> None:
        """Обновляет UID проекта в базе данных."""
        project = self.models.Project.get(path=path)
        if project:
            project.uid = uid
            project.modified_date = datetime.now()
            logging.debug(f"Обновлен UID проекта {path}: {uid}")
        else:
            logging.warning(f"Проект {path} не найден в БД для обновления UID")

    @db_session
    def delete_project(self, path: str) -> None:
        """Удаляет проект из базы данных."""
        project = self.models.Project.get(path=path)
        if project:
            project.delete()
            logging.debug(f"Проект {path} удален из БД")
        else:
            logging.warning(f"Проект {path} не найден в БД для удаления")

    @db_session
    def get_project_by_uid(self, uid: str) -> Any:
        """Находит проект в БД по UID."""
        return self.models.Project.get(uid=uid)

    @db_session
    def update_project_path(self, uid: str, new_path: str) -> None:
        """Обновляет путь проекта в базе данных по UID."""
        project = self.models.Project.get(uid=uid)
        if project:
            project.path = new_path
            project.modified_date = datetime.now()
            logging.debug(f"Обновлен путь проекта {uid}: {new_path}")
        else:
            logging.warning(f"Проект с UID {uid} не найден в БД для обновления пути")

    @db_session
    def delete_project_by_uid(self, uid: str) -> None:
        """Удаляет проект из базы данных по UID."""
        project = self.models.Project.get(uid=uid)
        if project:
            project.delete()
            logging.debug(f"Проект с UID {uid} удален из БД")
        else:
            logging.warning(f"Проект с UID {uid} не найден в БД для удаления")


# --- Точка входа -----------------------------------------------------------

if __name__ == '__main__':
    app = GeoOfficeProjectSyncTrayApp()
    app.run()
