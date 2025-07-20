from dataclasses import dataclass, asdict
from typing import Literal, Any


@dataclass
class Interface:
    """
    Модель настроек интерфейса.
    :param theme: Тема приложения (light, dark, system)
    :param last_page: Последняя страница приложения
    :param width: Ширина окна
    :param height: Высота окна
    """
    theme: Literal['light', 'dark', 'system']
    is_last_page: bool
    last_page: str
    width: int
    height: int
    left: int
    top: int


@dataclass
class Paths:
    """
    Модель настроек путей.
    :param file_server: Путь к файловому серверу
    :param projects_folder: Путь к папке проектов (относительно файлового сервера)
    :param favorite_folders: Пути к закрепленным папкам
    :param database_path: Путь к базе данных проектов (относительно файлового сервера)
    """
    file_server: str
    projects_folder: str
    favorite_folders: list[list[str]]
    database_path: str


@dataclass
class Settings:
    """
    Модель настроек.
    :param data: Словарь настроек из JSON
    :param interface: Настройки интерфейса
    :param paths: Настройки путей
    """
    data: dict[str, Any] | None
    interface: Interface | None = None
    paths: Paths | None = None

    def __post_init__(self):
        """Автоматическая инициализация после создания объекта"""
        if self.data is None:
            self.init_default_settings()
        else:
            self.load()

    def load(self) -> None:
        """
        Инициализация настроек.
        """
        try:
            interface = Interface(**self.data['interface'])
            paths = Paths(**self.data['paths'])
            self.interface = interface
            self.paths = paths
        except Exception as e:
            raise Warning(f"Не удалось загрузить настройки, используются настройки по умолчанию.\nОшибка:\n{e}")

    def to_dict(self) -> dict:
        """
        Конвертирует настройки в словарь, используя dataclasses.asdict().
        :return: Словарь настроек
        """
        return {
            'interface': asdict(self.interface),
            'paths': asdict(self.paths),
        }

    def init_default_settings(self) -> None:
        """Инициализация настроек по умолчанию"""
        file_server = r'\\server-r\igi'

        self.interface = Interface(
            theme='light',
            last_page='HomePage',
            is_last_page=True,
            width=800,
            height=1000,
            left=10,
            top=10,
        )
        self.paths = Paths(
            file_server=file_server,
            projects_folder='Work\\Объекты',
            favorite_folders=[
                ['сервер IGI', file_server],
                ['сервер NFVGP', r'\\server\Объекты'],
                ['NF', file_server + '\\NF'],
                ['Запись', 'D:\\Запись'],
                ['Scan', 'D:\\scan'],
            ],
            database_path=file_server+'\\geo_office.db'
        )

    def add_favorite_folder(self, name: str, path: str) -> None:
        """Добавляет папку в избранное"""
        self.paths.favorite_folders.append([name, path])

    def remove_favorite_folder(self, name: str, path: str) -> None:
        """Удаляет папку из избранного"""
        self.paths.favorite_folders = [
            [n, p] for n, p in self.paths.favorite_folders
            if not (n == name and p == path)
        ]

    def edit_favorite_folder(self, old: list[str], new: list[str]) -> None:
        """Изменяет папку из избранного"""
        old_name, old_path = old
        new_name, new_path = new
        for i in range(len(self.paths.favorite_folders)):
            _name, _path = self.paths.favorite_folders[i]
            if _name == old_name and _path == old_path:
                self.paths.favorite_folders[i] = [new_name, new_path]
                break
