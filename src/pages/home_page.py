import flet as ft
from .base_page import BasePage
import os
import difflib
import threading
import re
import sys
sys.path.append("..")
from ..utils import search_utils
from ..services.semantic_search_service import SemanticSearchService
import time
import socket
from src.services.search_service import SearchService

from ..utils.logger_config import log_exception


class HomePage(BasePage):
    """Главная страница приложения GeoOffice. Содержит UI и логику поиска файлов."""
    
    def __init__(self, app):
        """
        Инициализация главной страницы, создание всех UI-компонентов и переменных состояния.
        :param app: Экземпляр основного приложения
        """
        super().__init__(app)
        self.search_query = ""
        self.search_path = ""
        self.use_default_path = False
        self.search_results = []
        self.results_container = None
        self.path_field = None
        self.checkbox = None
        self.smart_checkbox = None
        self.page = None
        self.default_path_key = "geooffice_default_search_path"
        self.loading_indicator = None
        self.search_field = None
        self.use_smart_search = False
        self.use_morph_search = False
        self.search_service = SearchService()
        # Для индексации
        self.indexed_files = None
        self.indexed_path = None
        self.indexing_in_progress = False
        self.index_progress = 0.0
        self.index_status_text = ft.Text("Путь не проиндексирован", color=ft.Colors.GREY_500, size=12)
        self.index_progress_bar = ft.ProgressBar(width=300, value=0, visible=False)
        # Группа радиокнопок для выбора режима поиска
        self.search_mode_group = ft.RadioGroup(
            value="classic",
            on_change=self.on_search_mode_change,
            content=ft.Column([
                ft.Radio(label="Классический поиск", value="classic",
                         fill_color=ft.Colors.BLUE),
                ft.Radio(label="Морфологический поиск (примерное совпадение)", value="morph",
                         fill_color=ft.Colors.BLUE),
                ft.Radio(label="Семантический поиск (Sentence-BERT + FAISS)", value="semantic",
                         fill_color=ft.Colors.BLUE),
            ], spacing=0)
        )
        self.save_default_button = ft.ElevatedButton(
            text="Запомнить",
            on_click=self.on_save_default_click,
            icon=ft.Icons.SAVE
        )

    @staticmethod
    def get_user_default_path_file():
        """
        Получить путь к файлу, где хранится путь поиска по умолчанию для текущего пользователя.
        :return: str - путь к файлу
        """
        computer_name = socket.gethostname()
        return os.path.join("storage", "users", computer_name, "default_path.txt")

    def get_content(self):
        """
        Формирует и возвращает содержимое главной страницы (UI-компоненты Flet).
        :return: Flet Column с элементами интерфейса
        """
        self.page = self.app.page
        # Загружаем путь по умолчанию из файла пользователя только при первом запуске
        default_path_file = self.get_user_default_path_file()
        default_path = None
        if os.path.exists(default_path_file):
            with open(default_path_file, "r", encoding="utf-8") as f:
                default_path = f.read().strip()
        else:
            default_path = self.page.client_storage.get(self.default_path_key)
        # Создаём поля поиска
        self.search_field = ft.TextField(
            hint_text="Поиск файлов и папок...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_query_change,
            border_radius=20,
            text_size=14,
            height=40,
            expand=True
        )
        self.path_field = ft.TextField(
            label="Путь поиска",
            hint_text="Например, D:/Projects/Objects",
            expand=True,
            on_change=self.on_path_change,
        )
        self.checkbox = ft.Checkbox(
            label="По умолчанию",
            value=False,
            on_change=self.on_checkbox_change,
        )
        self.smart_checkbox = ft.Checkbox(
            label="Семантический поиск (Sentence-BERT + FAISS)",
            value=False,
            on_change=self.on_smart_checkbox_change,
        )
        self.loading_indicator = ft.ProgressRing(visible=False, width=30, height=30)
        self.results_container = ft.Container(
            content=ft.Text("Результаты поиска появятся здесь...", color=ft.Colors.GREY_500),
            padding=10,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8,
            margin=ft.margin.only(top=10)
        )
        if default_path and not self.search_path:
            self.search_path = default_path
            self.path_field.value = default_path
        return ft.Column([
            ft.Row([
                ft.Image(src="icon.png", height=64),
                ft.Column([
                    ft.Text("Добро пожаловать в GeoOffice", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Ведение геодезической документации и расчетов", size=16, color=ft.Colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
            ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=40),
            
            ft.Text("Обзор системы", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                self.create_info_card("Документы", "Создание геодезической документации",
                                      ft.Icons.DESCRIPTION, ft.Colors.BLUE, self.show_documents),
                self.create_info_card("Приложения", "Вычисление координат и масштабов, конвертация файлов",
                                      ft.Icons.EXPLORE, ft.Colors.GREEN, self.show_geodetic_works),
                self.create_info_card("Специализированные инструменты",
                                      "Плагины AutoCAD и Metashape, таксационные расчеты",
                                      ft.Icons.BUILD, ft.Colors.ORANGE, self.show_specialized_tools),
            ], wrap=True),
            
            ft.Divider(height=40),
            
            ft.Text("Быстрый поиск", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        self.search_field,
                        self.loading_indicator
                    ], spacing=10, expand=True),
                    ft.Row([
                        ft.Container(self.path_field, expand=True),
                        self.save_default_button
                    ], spacing=10, expand=True),
                    self.search_mode_group,
                    ft.Row([
                        self.index_progress_bar,
                        self.index_status_text
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.results_container
                ]),
                padding=20,
                bgcolor=ft.Colors.GREY_100,
                border_radius=8,
                margin=ft.margin.only(top=10, bottom=10),
                expand=True
            ),
        ])

    def create_info_card(self, title, description, icon, color, on_click=None):
        """
        Создаёт информационную карточку для раздела.
        :param title: Заголовок
        :param description: Описание
        :param icon: Иконка Flet
        :param color: Цвет иконки
        :param on_click: Обработчик клика
        :return: Flet Card
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=12, color=ft.Colors.GREY_600),
                ], horizontal_alignment=ft.CrossAxisAlignment.START),
                padding=20,
                width=250,
                height=180,
                alignment=ft.alignment.top_left,
                on_click=on_click,
                ink=True,
                border_radius=8
            )
        )
    
    def show_documents(self, e=None):
        """
        Показать раздел документов. Вызывает уведомление и может переключить страницу.
        """
        self.show_snack_bar("Переход к документам...")
        # Можно добавить переход к первой функции из категории
        # self.app.show_page('documents')
    
    def show_geodetic_works(self, e=None):
        """
        Показать раздел геодезических работ. Вызывает уведомление и может переключить страницу.
        """
        self.show_snack_bar("Переход к геодезическим работам...")
        # Можно добавить переход к первой функции из категории
        # self.app.show_page('coordinates')
    
    def show_specialized_tools(self, e=None):
        """
        Показать раздел специализированных инструментов. Вызывает уведомление и может переключить страницу.
        """
        self.show_snack_bar("Переход к специализированным инструментам...")
        # Можно добавить переход к первой функции из категории
        # self.app.show_page('autocad')

    def on_smart_checkbox_change(self, e):
        """
        Обработчик смены чекбокса семантического поиска. Сбрасывает морфологический режим и обновляет UI.
        """
        self.use_smart_search = e.control.value
        if self.use_smart_search:
            self.use_morph_search = False
            self.page.update()
        self.indexed_files = None
        self.indexed_path = None
        self.index_status_text.value = "Путь не проиндексирован"
        self.index_status_text.color = ft.Colors.GREY_500
        self.page.update()

    def on_search_mode_change(self, e):
        """
        Обработчик смены режима поиска (радиокнопки). Запускает поиск, если есть запрос и путь.
        """
        mode = self.search_mode_group.value
        self.use_smart_search = mode == "semantic"
        self.use_morph_search = mode == "morph"
        self.page.update()
        # Автоматически запускаем поиск при смене метода, если есть запрос и путь
        if self.search_query and self.search_path:
            threading.Thread(target=self.threaded_search, daemon=True).start()

    def on_query_change(self, e):
        """
        Обработчик изменения строки поиска. Запускает индексацию и поиск при необходимости.
        """
        self.search_query = e.control.value
        if self.search_path and not self.indexing_in_progress:
            self.results_container.content = ft.Text("Индексация файлов...", color=ft.Colors.GREY_500)
            self.loading_indicator.visible = True
            self.index_progress_bar.visible = True
            self.index_progress_bar.value = 0
            self.index_status_text.value = "Индексация..."
            self.index_status_text.color = ft.Colors.BLUE
            self.page.update()
            threading.Thread(target=self._index_files, daemon=True).start()
        if self.search_query and self.search_path:
            self.results_container.content = ft.Text("Поиск...", color=ft.Colors.GREY_500)
            self.loading_indicator.visible = True
            self.page.update()
            threading.Thread(target=self.threaded_search, daemon=True).start()

    def on_path_change(self, e):
        """
        Обработчик изменения пути поиска. Сбрасывает индексацию и запускает поиск по новому пути.
        """
        self.search_path = e.control.value
        # Сброс индекса при смене пути
        self.indexed_files = None
        self.indexed_path = None
        self.index_progress_bar.visible = False
        self.index_status_text.value = "Путь не проиндексирован"
        self.index_status_text.color = ft.Colors.GREY_500
        self.page.update()
        # Автоматически запускаем поиск по новому пути, если есть запрос
        if self.search_query and self.search_path:
            threading.Thread(target=self.threaded_search, daemon=True).start()

    def on_checkbox_change(self, e):
        self.use_default_path = e.control.value
        default_path_file = self.get_user_default_path_file()
        if self.use_default_path and self.search_path:
            # Сохраняем путь по умолчанию в файл пользователя
            os.makedirs(os.path.dirname(default_path_file), exist_ok=True)
            with open(default_path_file, "w", encoding="utf-8") as f:
                f.write(self.search_path)
            self.page.client_storage.set(self.default_path_key, self.search_path)
        elif not self.use_default_path:
            # Удаляем путь по умолчанию
            if os.path.exists(default_path_file):
                os.remove(default_path_file)
            self.page.client_storage.remove(self.default_path_key)

    def update_results(self, all_paths_sorted):
        """
        Обновляет контейнер с результатами поиска (кликабельные пути).
        :param all_paths_sorted: Список путей
        """
        # Создаём кликабельные элементы для перехода к файлу/папке
        items = [
            ft.TextButton(
                text=res,
                on_click=lambda e, p=res: self.open_in_explorer(p),
                style=ft.ButtonStyle(padding=ft.padding.all(0), alignment=ft.alignment.top_left),
            ) for res in all_paths_sorted
        ]
        self.results_container.content = ft.Column(items, scroll=ft.ScrollMode.AUTO, height=250)
        self.page.update()

    def _index_files(self):
        """
        Индексирует файлы для выбранного режима поиска (если требуется).
        """
        self.indexing_in_progress = True
        start_time = time.time()
        def progress_callback(count, total):
            self.index_progress = count / total
            self.index_progress_bar.value = self.index_progress
            elapsed = time.time() - start_time
            speed = count / elapsed if elapsed > 0 else 0
            eta = (total - count) / speed if speed > 0 else 0
            if count > 5 and eta > 1:
                eta_str = f" (осталось ~{int(eta)} сек)"
            else:
                eta_str = ""
            self.index_status_text.value = f"Индексация... {int(self.index_progress*100)}%{eta_str}"
            self.index_status_text.color = ft.Colors.BLUE
            self.index_progress_bar.visible = True
            self.page.update()
        mode = self.get_search_mode()
        if self.search_service.is_reindex_needed(self.search_path, mode=mode):
            self.search_service.clear_index(mode=mode)
            self.search_service.index_directory(self.search_path, mode=mode, progress_callback=progress_callback)
        self.indexed_path = self.search_path
        self.indexing_in_progress = False
        self.index_progress_bar.visible = False
        self.index_status_text.value = "Путь проиндексирован"
        self.index_status_text.color = ft.Colors.GREEN
        self.loading_indicator.visible = False
        self.page.update()

    def get_search_mode(self):
        """
        Возвращает текущий режим поиска ('classic', 'morph', 'semantic').
        :return: str
        """
        if self.use_smart_search:
            return "semantic"
        elif self.use_morph_search:
            return "morph"
        else:
            return "classic"

    def threaded_search(self):
        """
        Запускает поиск файлов в отдельном потоке и обновляет UI с результатами.
        """
        mode = self.get_search_mode()
        results = self.search_service.search(self.search_query, self.search_path, mode=mode, limit=20)
        items = []
        import re
        query_text = self.search_query.strip()
        highlight_re = re.compile(re.escape(query_text), re.IGNORECASE)
        if mode == "semantic":
            for path, score in results:
                correct_path = os.path.normpath(path)
                name = os.path.basename(correct_path)
                icon = ft.Icons.FOLDER if os.path.isdir(correct_path) else ft.Icons.DESCRIPTION
                display_name = []
                last = 0
                for m in highlight_re.finditer(name):
                    if m.start() > last:
                        display_name.append(ft.Text(name[last:m.start()]))
                    display_name.append(ft.Text(name[m.start():m.end()], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE))
                    last = m.end()
                if last < len(name):
                    display_name.append(ft.Text(name[last:]))
                if not display_name:
                    display_name = [ft.Text(name)]
                items.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=ft.Colors.BLUE if os.path.isdir(correct_path) else ft.Colors.GREY_700),
                        title=ft.Row(display_name, spacing=0),
                        subtitle=ft.Text(f"{correct_path}\nСходство: {1-score:.2f}", size=11, color=ft.Colors.GREY_500),
                        on_click=lambda e, p=correct_path: self.open_in_explorer(p),
                        dense=True,
                    )
                )
        elif mode == "morph":
            for path in results:
                correct_path = os.path.normpath(path)
                name = os.path.basename(correct_path)
                icon = ft.Icons.FOLDER if os.path.isdir(correct_path) else ft.Icons.DESCRIPTION
                display_name = []
                last = 0
                for m in highlight_re.finditer(name):
                    if m.start() > last:
                        display_name.append(ft.Text(name[last:m.start()]))
                    display_name.append(ft.Text(name[m.start():m.end()], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE))
                    last = m.end()
                if last < len(name):
                    display_name.append(ft.Text(name[last:]))
                if not display_name:
                    display_name = [ft.Text(name)]
                items.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=ft.Colors.BLUE if os.path.isdir(correct_path) else ft.Colors.GREY_700),
                        title=ft.Row(display_name, spacing=0),
                        subtitle=ft.Text(correct_path, size=11, color=ft.Colors.GREY_500),
                        on_click=lambda e, p=correct_path: self.open_in_explorer(p),
                        dense=True,
                    )
                )
        else:  # classic
            for path, name in results:
                correct_path = os.path.normpath(path)
                icon = ft.Icons.FOLDER if os.path.isdir(correct_path) else ft.Icons.DESCRIPTION
                display_name = []
                last = 0
                for m in highlight_re.finditer(name):
                    if m.start() > last:
                        display_name.append(ft.Text(name[last:m.start()]))
                    display_name.append(ft.Text(name[m.start():m.end()], weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE))
                    last = m.end()
                if last < len(name):
                    display_name.append(ft.Text(name[last:]))
                if not display_name:
                    display_name = [ft.Text(name)]
                items.append(
                    ft.ListTile(
                        leading=ft.Icon(icon, color=ft.Colors.BLUE if os.path.isdir(correct_path) else ft.Colors.GREY_700),
                        title=ft.Row(display_name, spacing=0),
                        subtitle=ft.Text(correct_path, size=11, color=ft.Colors.GREY_500),
                        on_click=lambda e, p=correct_path: self.open_in_explorer(p),
                        dense=True,
                    )
                )
        if not items:
            self.results_container.content = ft.Text("Ничего не найдено", color=ft.Colors.GREY_500)
        else:
            self.results_container.content = ft.Column(items, scroll=ft.ScrollMode.AUTO, height=350)
        self.loading_indicator.visible = False
        self.page.update()

    def search_files_and_dirs(self, root_path, query):
        """
        Выполняет морфологический поиск файлов и папок по директории.
        :param root_path: str - путь к директории
        :param query: str - поисковый запрос
        :return: list[str] - найденные пути
        """
        matches = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Проверяем папки
            for d in dirnames:
                if self.is_morph_match(d, query):
                    matches.append(os.path.join(dirpath, d))
            # Проверяем файлы
            for f in filenames:
                if self.is_morph_match(f, query):
                    matches.append(os.path.join(dirpath, f))
        return matches

    def is_morph_match(self, name, query):
        """
        Проверяет морфологическое совпадение имени с запросом.
        :param name: str
        :param query: str
        :return: bool
        """
        # Морфологическое (примерное) совпадение через SequenceMatcher
        name_low = name.lower()
        query_low = query.lower()
        ratio = difflib.SequenceMatcher(None, name_low, query_low).ratio()
        return ratio > 0.6 or query_low in name_low

    def open_in_explorer(self, path):
        """
        Открывает указанный путь в проводнике/файловом менеджере ОС.
        :param path: str
        """
        import platform
        import subprocess
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer /select,"{path}"')
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-R", path])
        else:
            subprocess.Popen(["xdg-open", os.path.dirname(path)])

    def on_save_default_click(self, e):
        """
        Сохраняет текущий путь как путь поиска по умолчанию для пользователя.
        """
        # Сохраняем путь по умолчанию
        default_path_file = self.get_user_default_path_file()
        if self.search_path:
            os.makedirs(os.path.dirname(default_path_file), exist_ok=True)
            with open(default_path_file, "w", encoding="utf-8") as f:
                f.write(self.search_path)
            self.page.client_storage.set(self.default_path_key, self.search_path)
            self.show_snack_bar("Путь сохранён как путь по умолчанию")
        else:
            self.show_snack_bar("Сначала укажите путь поиска", color=ft.Colors.RED)
