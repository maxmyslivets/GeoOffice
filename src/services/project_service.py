import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from models.project_model import Project
from services.database_service import DatabaseService
from utils.file_utils import FileUtils
from utils.logger_config import log_exception, get_logger

logger = get_logger("services.project_service")


class ProjectService:
    """
    Сервис для работы с проектами.
    Обеспечивает загрузку, сохранение, поиск и управление данными проектов.
    """
    
    def __init__(self, database_service: DatabaseService):
        """Инициализация сервиса проектов"""
        self.database_service = database_service
        logger.info(f"Инициализирован сервис проектов.")

    @log_exception
    def get_project(self, project_id: int) -> Optional[Project]:
        """
        Получить проект по id.
        :param project_id: id проекта
        :return: Данные проекта или None если не найден
        """
        project_data = self.database_service.get_project_from_id(project_id).to_dict()
        project_data['created_date'] = datetime.fromisoformat(project_data['created_date'])
        project_data['modified_date'] = datetime.fromisoformat(project_data['modified_date'])
        return Project(**project_data)

    @log_exception
    def diff_projects(self, projects_dirpath: str | Path) -> dict[str, list[str]]:
        """
        Сканирование директории проектов и определение наличия проектов в базе данных.
        :return: ...
        """

        projects_in_files = []

        if not isinstance(projects_dirpath, Path):
            projects_dirpath = Path(projects_dirpath)

        for item in projects_dirpath.rglob(".geo_office_project"):
            projects_in_files.append(item.parent.relative_to(projects_dirpath))

        projects_in_files = set([str(path) for path in projects_in_files])
        projects_in_database = set(p.path for p in list(self.database_service.get_all_projects()))

        return {
            "only_in_files": list(projects_in_files - projects_in_database),
            "only_in_database": list(projects_in_database - projects_in_files),
            "in_files_and_database": list(projects_in_files & projects_in_database)
        }

    @log_exception
    def diff_projects_with_progress(self, projects_dirpath: str | Path,
                                    progress, stop_event) -> dict[str, list[str]] | None:
        """
        То же, что diff_projects, но с поддержкой прогресса и отмены.
        :param projects_dirpath: Корень каталога проектов
        :param progress: Callable(value: float [0..1], message: Optional[str])
        :param stop_event: threading.Event для отмены
        :return: словарь с результатами или None, если отменено
        """
        if not isinstance(projects_dirpath, Path):
            projects_dirpath = Path(projects_dirpath)

        progress(0.0, "Сканирование файловой системы...")

        # Подсчёт общего количества файлов-маркеров для корректного прогресса
        total = 0
        for _ in projects_dirpath.rglob(".geo_office_project"):
            total += 1
        if total == 0:
            progress(0.4, "В файловой системе ничего не найдено")

        # Сканирование с обновлением прогресса
        projects_in_files_list = []
        seen = 0
        for item in projects_dirpath.rglob(".geo_office_project"):
            if stop_event is not None and stop_event.is_set():
                return None
            projects_in_files_list.append(item.parent.relative_to(projects_dirpath))
            seen += 1
            if total > 0 and (seen % 50 == 0):
                progress(min(0.5, 0.1 + 0.4 * (seen / total)), f"Сканирование... {seen}/{total}")

        progress(0.6, "Загрузка проектов из базы данных...")
        projects_in_files = set([str(path) for path in projects_in_files_list])
        projects_in_database = set(p.path for p in list(self.database_service.get_all_projects()))

        only_in_files = list(projects_in_files - projects_in_database)
        only_in_database = list(projects_in_database - projects_in_files)
        in_both = list(projects_in_files & projects_in_database)

        progress(1.0, "Готово")
        return {
            "only_in_files": only_in_files,
            "only_in_database": only_in_database,
            "in_files_and_database": in_both,
        }

    @log_exception
    def create_project(self, number: str, name: str, customer: str = "") -> Project:
        """
        Создать новый проект.
        :param number: Номер проекта
        :param name: Название проекта
        :param customer: Заказчик
        :return: Созданный проект
        """
        pass

    @log_exception
    def update_project(self, number: str, **kwargs) -> bool:
        """
        Обновить данные проекта.
        :param number: Номер проекта
        :param kwargs: Поля для обновления
        :return: True если проект обновлен, False если не найден
        """
        pass

    @log_exception
    def delete_project(self, project_id: int) -> bool:
        """
        Удалить проект.
        :param project_id: id проекта
        :return: True если проект удален, False если не найден
        """
        pass

    @log_exception
    def get_project_path(self, project_id: int) -> bool:
        """
        Добавить документ к проекту.
        :param project_id: id проекта
        :return: True если документ добавлен, False если проект не найден
        """
        pass

    @log_exception
    def get_project_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по проектам.
        :return: Словарь со статистикой
        """
        total_projects = 274
        active_projects = 7
        completed_projects = 257
        archived_projects = 262
        promising_projects = 23

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "archived_projects": archived_projects,
            "promising_projects": promising_projects,
        }
