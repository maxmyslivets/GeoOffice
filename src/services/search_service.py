import os
import difflib
from src.utils import search_utils
from src.services.semantic_search_service import SemanticSearchService
import logging

logger = logging.getLogger("search_service")
logger.setLevel(logging.DEBUG)

class SearchService:
    """
    Сервис для поиска файлов и папок: классический, морфологический, семантический режимы.
    Позволяет индексировать директории, выполнять поиск и проверять совпадения по разным алгоритмам.
    """

    def __init__(self):
        """
        Инициализация сервиса поиска. Загружает необходимые модели и сервисы.
        """
        self.semantic_service = SemanticSearchService()

    def index_directory(self, root_path, mode="classic", progress_callback=None):
        """
        Индексирует директорию для выбранного режима поиска (только для семантического).
        :param root_path: str - путь к директории
        :param mode: str - режим поиска ('classic', 'morph', 'semantic')
        :param progress_callback: callable - функция для обновления прогресса
        """
        logger.debug(f"[index_directory] mode={mode}, root_path={root_path}")
        if mode == "semantic":
            self.semantic_service.index_directory(root_path, progress_callback)
        elif mode == "morph":
            logger.debug("[index_directory] Морфологический поиск не требует индексации")
            pass
        else:
            logger.debug("[index_directory] Классический поиск не требует индексации")
            pass

    def is_reindex_needed(self, root_path, mode="classic"):
        """
        Проверяет, требуется ли переиндексация для выбранного режима поиска.
        :param root_path: str
        :param mode: str
        :return: bool
        """
        logger.debug(f"[is_reindex_needed] mode={mode}, root_path={root_path}")
        if mode == "semantic":
            from src.services.semantic_search_service import is_reindex_needed as sem_is_reindex_needed
            return sem_is_reindex_needed(root_path)
        elif mode == "morph":
            return False
        else:
            return False

    def clear_index(self, mode="classic"):
        """
        Очищает индекс для выбранного режима поиска (если применимо).
        :param mode: str
        """
        logger.debug(f"[clear_index] mode={mode}")
        if mode == "semantic":
            pass
        elif mode == "morph":
            pass
        else:
            pass

    def project_search(self, query, limit=50) -> list[tuple[str, str]]:
        """
        Выполняет поиск объектов по запросу в базе данных.
        :param query: str - поисковый запрос
        :param limit: int - максимальное количество результатов
        :return: list - список объектов [(номер, название), ...]
        """
        logger.debug(f"[search], query='{query}', limit={limit}")
        results = []

        # WARNING: Заглушка
        for i in range(1, limit):
            results.append((f"{i}.25", "Название объекта"))
        # TODO: Поиск в базе данных
        # results.append((number, name))

        if len(results) >= limit:
            logger.debug(f"[search] classic results (truncated): {results}")
            return results
        logger.debug(f"[search] classic results: {results}")
        return results

    def morph_search(self, query, root_path):
        """
        Выполняет морфологический поиск файлов и папок по директории.
        :param query: str
        :param root_path: str
        :return: list[str]
        """
        logger.debug(f"[morph_search] query='{query}', root_path={root_path}")
        matches = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            for d in dirnames:
                if self.is_morph_match(d, query):
                    matches.append(os.path.join(dirpath, d))
            for f in filenames:
                if self.is_morph_match(f, query):
                    matches.append(os.path.join(dirpath, f))
        logger.debug(f"[morph_search] matches: {matches}")
        return matches

    def is_morph_match(self, name, query):
        """
        Проверяет морфологическое совпадение имени с запросом.
        :param name: str
        :param query: str
        :return: bool
        """
        ratio = difflib.SequenceMatcher(None, name.lower(), query.lower()).ratio()
        result = ratio > 0.6 or query.lower() in name.lower()
        logger.debug(f"[is_morph_match] name='{name}', query='{query}', ratio={ratio}, result={result}")
        return result 