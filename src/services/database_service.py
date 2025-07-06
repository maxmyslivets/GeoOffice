import os
import subprocess
from pathlib import Path
from typing import Any

from pony.orm import Database, db_session

from src.models.database_model import DataBaseProjects
from src.models.project_model import Project
from src.utils.file_utils import FileUtils
from src.utils.logger_config import log_exception, get_logger

logger = get_logger("services.database_service")


class DataBaseProjectService:
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
        self.db = Database()

        try:
            logger.info(f"Инициализация базы данных: {self._path}")

            # Привязываем базу данных
            self.db.bind(provider='sqlite', filename=str(self._path), create_db=True)

            # Ставим защиту на файл (скрываем)
            FileUtils.manage_file_attributes(file_path=str(self._path), action="protect")

            # Инициализация моделей
            self.models = DataBaseProjects(self.db).models

            # Генерируем схемы таблиц
            self.db.generate_mapping(create_tables=True)

            logger.info("База данных успешно инициализирована")

        except Exception as e:
            logger.error(f"Ошибка при инициализации/создании базы данных: {e}")

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
    def get_project(self, project_id: int) -> Any:
        logger.debug(f"Получение проекта по id: id={project_id}")
        return self.models.Project[project_id]

    @log_exception
    @db_session
    def get_all_projects(self) -> list[Any]:
        logger.debug(f"Получение всех проектов")
        return self.models.Project.select()[:]
