import os
import subprocess
import traceback
from pathlib import Path
from typing import Any

from pony.orm import Database as PonyDatabase, select
from pony.orm import db_session

from models.database_model import Database
from utils.file_utils import FileUtils
from utils.logger_config import log_exception, get_logger

logger = get_logger("services.database_service")


class DatabaseService:
    """
    Сервис для работы с базой данных проектов.
    Содержит методы для работы с таблицами, определенными в DataBaseProjects.
    """
    @log_exception
    def __init__(self, path: Path | str) -> None:
        """
        Инициализация сервиса базы данных.
        :param path: Путь к файлу базы данных
        """
        self._path = Path(path)
        self.db: PonyDatabase | None = None
        self.models: Any = None
        self.connected = False

    @log_exception
    @db_session
    def connection(self) -> None:
        logger.info(f"Инициализация базы данных: {self._path}")
        self.db = PonyDatabase()
        self.db.bind(provider='sqlite', filename=str(self._path))
        # Инициализация моделей
        self.models = Database(self.db).models
        # Генерируем схемы таблиц
        self.db.generate_mapping()
        self.connected = True
        logger.info("База данных успешно инициализирована")

    @log_exception
    @db_session
    def create_project(self, number: str, name: str, customer: str,
                       chief_engineer: str, status: str, address: str, path: str) -> Any:
        """
        Создание нового проекта.
        :param number: Номер проекта
        :param name: Название проекта
        :param customer: Заказчик
        :param chief_engineer: Главный инженер
        :param status: Статус проекта
        :param address: Адрес объекта
        :param path: Путь к папке проекта
        :return: Созданный проект
        """

        project = self.models.Project(
            number=number,
            name=name,
            customer=customer,
            chief_engineer=chief_engineer,
            status=status,
            address=address,
            path=path
        )
        logger.debug(f"Создан новый проект: {project}")
        return project

    @log_exception
    @db_session
    def get_project_from_id(self, project_id: int) -> Any:
        logger.debug(f"Получение проекта по id: id={project_id}")
        return self.models.Project[project_id]

    @log_exception
    @db_session
    def get_project_from_path(self, path: str | Path) -> Any:
        logger.debug(f"Получение проекта по пути: path={path}")
        return self.models.Project.select_by_sql("SELECT * FROM Объекты WHERE path = $path")[0]

    @log_exception
    @db_session
    def get_all_projects(self) -> list[Any]:
        logger.debug(f"Получение всех проектов")
        return self.models.Project.select()[:]

    @log_exception
    @db_session
    def search_project(self, query: str):
        """
        Поиск проектов по названию.
        :param query: Поисковой запрос
        :return: Список кортежей
        """
        query = query.lower()
        # result = self.models.Project.select(lambda p: query in p.name)[:]
        # return [(p.id, p.number, p.name, p.customer) for p in result_projects]
        result = select(
            (p.id, p.number, p.name, p.customer) for p in self.models.Project
            if query in " ".join(p.number, p.name, p.customer)
        )
