import os
import re
import shutil
import uuid
import warnings
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from models.project_model import ProjectModel
from models.settings_model import Settings
from services.database_service import DatabaseService
from utils.file_utils import FileUtils
from utils.logger_config import log_exception, get_logger

logger = get_logger("services.project_service")


class ProjectService:
    """
    Сервис для работы с проектами.
    Обеспечивает загрузку, сохранение, поиск и управление данными проектов.
    """
    
    def __init__(self, database_service: DatabaseService, settings: Settings):
        """Инициализация сервиса проектов"""
        self.database_service = database_service
        self.app_settings = settings
        logger.info(f"Инициализирован сервис проектов.")

    @log_exception
    def get_project(self, project_id: int) -> Optional[ProjectModel]:
        """
        Получить проект по id.
        :param project_id: id проекта
        :return: Данные проекта или None если не найден
        """
        project_data = self.database_service.get_project_from_id(project_id).to_dict()
        project_data['created_date'] = datetime.fromisoformat(project_data['created_date'])
        project_data['modified_date'] = datetime.fromisoformat(project_data['modified_date'])
        return ProjectModel(**project_data)

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
    def create_project(self, name: str | None, path: str|Path, exists: bool = False) -> ProjectModel:
        """
        Создать проект.
        :param name: Название проекта
        :type name: str
        :param path: Путь
        :type path: str
        :param exists: Если папка объекта уже создана
        :type exists: bool
        :return: Проект к папке проекта
        :rtype: Project
        """
        projects_dir = self.app_settings.paths.get_projects_pathdir()
        if exists:
            project_path = projects_dir / path
            project_name = project_path.name
        else:
            project_path = projects_dir / path / name
            project_name = name
            template_dir = projects_dir / self.app_settings.paths.project_template_dir
            shutil.copytree(template_dir, project_path)
        geo_office_project_filepath = project_path / ".geo_office_project"
        uid = self._set_uuid(geo_office_project_filepath)
        project = self.database_service.get_project_from_uid(uid)
        if project is not None:
            raise Warning(f"Объект '{project_name}' ранее уже был добавлен под названием "
                          f"'{project.number} {project.name}'")
        project = self.database_service.create_project(name=project_name, path=str(project_path), uid=uid)
        project_data = project.to_dict()
        project_data['created_date'] = datetime.fromisoformat(project_data['created_date'])
        project_data['modified_date'] = datetime.fromisoformat(project_data['modified_date'])
        return ProjectModel(**project_data)

    @log_exception
    def create_file_project(self, path: str|Path) -> Path:
        """
        Создает в указанной папке пустой файл ``.geo_office_project``.
        :param path: Путь к существующей папке, в которой нужно создать файл.
        :type path: str | Path
        :return: Путь к созданному файлу ``.geo_office_project``.
        :rtype: Path
        :raises FileNotFoundError: Если указанная папка не существует.
        :raises NotADirectoryError: Если указанный путь существует, но не является папкой.
        :raises FileExistsError: Если файл ``.geo_office_project`` уже существует в указанной папке.
        """
        path = Path(path)
        if not path.is_dir():
            raise FileNotFoundError(f"Каталог {path} не существует")
        file_path = path / ".geo_office_project"
        if not file_path.is_file():
            raise PermissionError(f"'{file_path}' не является файлом")
        file_path.touch(exist_ok=False)
        return file_path

    @log_exception
    def _set_uuid(self, path: str|Path) -> str:
        """
        Добавляет в файл ``.geo_office_project`` уникальный идентификатор.
        :param path: Путь к файлу ``.geo_office_project``.
        :type path: str | Path
        :return: Уникальный идентификатор
        :rtype: str
        :raises FileExistsError: Если файл скрыт или защищен от записи.
        :raises PermissionError: Если файл скрыт или защищен от записи.
        """
        path = Path(path)
        if path.exists():
            if not path.is_dir():
                with path.open("r", encoding="utf-8") as f:
                    text = f.read()
                    if len(text) > 0:
                        try:
                            uid = uuid.UUID("{" + f"{text}" + "}")
                            warnings.warn(f"В файле уже записан uuid: {str(uid)}")
                            return str(uid)
                        except ValueError:
                            with open(str(path) + ".bak", "w", encoding="utf-8") as f_bak:
                                f_bak.write(text)
                            warnings.warn(f"В файле уже было записано содержимое, не являющееся uuid. "
                                          f"Копия содержимого сохранена в файле {str(path) + ".bak"}.")
            else:
                raise PermissionError(f"'{path}' не является файлом")
        uid = uuid.uuid4()
        try:
            with path.open("w", encoding="utf-8") as f:
                f.write(str(uid))
        except PermissionError:
            raise PermissionError("Файл скрыт или защищен от записи")
        # protect_result = FileUtils.manage_file_attributes(path, "protect")
        # if protect_result["error"] is not None:
        #     warnings.warn(f"Не удалось установить защиту на файл проекта.\n{protect_result['error']}")
        return str(uid)

    @log_exception
    def delete_project(self, project_id: int) -> bool:
        """
        Удалить проект.
        :param project_id: id проекта
        :return: True если проект удален, False если не найден
        """
        pass

    @log_exception
    def update_project_in_database(self, project_model: ProjectModel) -> ProjectModel:
        """
        Изменить проект.
        :return: True если документ добавлен, False если проект не найден
        """
        project_db = self.database_service.update_project(project_model)
        return ProjectModel(**project_db.to_dict())

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
