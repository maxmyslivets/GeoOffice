import pystray
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
            data = {"server_path": self.server_path}
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
                    self._sync_projects()
                except Exception as e:
                    logging.exception("Ошибка во время синхронизации проектов")

                # Ждём указанное количество минут
                if not self._stop_event.wait(self.sync_period * 60):
                    continue
                else:
                    break

        self._sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self._sync_thread.start()

    def _sync_projects(self):
        """Заглушка для процесса синхронизации (сюда добавить реальную логику)."""
        if not self.server_path:
            logging.warning("Сервер не задан. Синхронизация пропущена.")
            return

        logging.info(f"Выполняется синхронизация с сервером: {self.server_path}")
        # Здесь будет логика синхронизации проектов
        time.sleep(2)  # TODO: эмуляция процесса
        logging.info("Синхронизация завершена успешно.")

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


# --- Точка входа -----------------------------------------------------------

if __name__ == '__main__':
    app = GeoOfficeProjectSyncTrayApp()
    app.run()
