import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from src.models.project_model import Project
from src.services.database_service import DatabaseService
from src.utils.file_utils import FileUtils
from src.utils.logger_config import log_exception, get_logger

logger = get_logger("services.project_service")


class ProjectService:
    """
    Сервис для работы с проектами.
    Обеспечивает загрузку, сохранение, поиск и управление данными проектов.
    """
    
    def __init__(self, database_project_service: DatabaseService):
        """Инициализация сервиса проектов"""
        self.database_service = database_project_service
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
    def search_projects(self, query: str, return_all: bool = False, limit: int = 50) -> list[tuple[int, str, str, str]]:
        """
        Поиск проектов по запросу.
        :param query: Поисковый запрос
        :param return_all: Вернуть все проекты
        :param limit: Максимальное количество результатов
        :return: Список кортежей (id, номер, название, заказчик)
        """
        #FIXME: При появлении пробела в запросе, сервис не выдает результаты

        projects_data: List[Project] = self.database_service.get_all_projects()

        query_lower = query.lower()
        results = []

        if return_all:
            projects_edit_datetime = [(projects_data[idx].modified_date, idx) for idx in range(len(projects_data))]
            projects_edit_datetime.sort(key=lambda x: x[0], reverse=True)
            for _, idx in projects_edit_datetime:
                project = projects_data[idx]
                results.append((project.id, project.number, project.name, project.customer))
                if len(results) >= limit:
                    break
        else:
            for project in projects_data:
                if (query_lower in project.number.lower()
                        or query_lower in project.name.lower()
                        or query_lower in project.customer.lower()):
                    results.append((project.id, project.number, project.name, project.customer))

        return results

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
