from typing import Optional

from src.models.project_model import Project
from src.utils.logger_config import log_exception, get_logger

logger = get_logger("services.link_folder_service")


class LinkFolderService:
    """
    Сервис для работы с закрепленными ссылками на директории.
    Обеспечивает чтение и запись списка ссылок в файл настроек.
    """

    def __init__(self):
        """Инициализация сервиса проектов"""
        logger.info(f"Инициализирован сервис проектов.")

    @log_exception
    def get_project(self, project_id: int) -> Optional[Project]:
        """
        Получить проект по id.
        :param project_id: id проекта
        :return: Данные проекта или None если не найден
        """
        # TODO: обращение к БД и вытягивание данных проекта по его id
        logger.warning(f"Получение данных объекта не реализовано. Используется заглушка.")
        project = Project(id=project_id,
                          number="50.25",
                          name="Реконструкция спортзала по адресу ул.Молодежная 26 в г.Новополоцк",
                          customer="Новополоцкий городской исполнительный комитет",
                          chief_engineer="Богданова Екатерина Александровна",
                          status="активный",
                          address="ул.Молодежная 26 в г.Новополоцк")
        return project
