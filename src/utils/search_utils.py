import os
import threading
import json
import socket
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.analysis import StemmingAnalyzer
from whoosh.writing import AsyncWriter
from whoosh.query import FuzzyTerm

import shutil

INDEX_DIR = "storage/whoosh_index"
index_lock = threading.Lock()
META_PATH = os.path.join(INDEX_DIR, "whoosh_index.meta.json")

schema = Schema(
    path=ID(stored=True, unique=True),
    name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    content=TEXT(stored=False, analyzer=StemmingAnalyzer())
)

def get_user_index_dir():
    """
    Возвращает путь к пользовательской директории индекса Whoosh для текущего компьютера.
    :return: Строка с путем к индексу
    """
    computer_name = socket.gethostname()
    return os.path.join("storage", "users", computer_name, "whoosh_index")

def get_user_meta_path():
    """
    Возвращает путь к файлу метаданных индекса Whoosh для текущего пользователя.
    :return: Строка с путем к файлу метаданных
    """
    computer_name = socket.gethostname()
    return os.path.join("storage", "users", computer_name, "whoosh_index.meta.json")

def create_or_open_index():
    """
    Создает или открывает индекс Whoosh для текущего пользователя.
    :return: Объект индекса Whoosh
    """
    with index_lock:
        index_dir = get_user_index_dir()
        os.makedirs(index_dir, exist_ok=True)
        try:
            if not index.exists_in(index_dir):
                return index.create_in(index_dir, schema)
            else:
                return index.open_dir(index_dir)
        except Exception:
            shutil.rmtree(index_dir)
            os.makedirs(index_dir, exist_ok=True)
            return index.create_in(index_dir, schema)

def clear_index():
    """
    Очищает индекс Whoosh для текущего пользователя (удаляет директорию индекса).
    """
    index_dir = get_user_index_dir()
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)

def get_latest_mtime(root_path):
    """
    Возвращает время последнего изменения любого файла/папки в директории.
    :param root_path: Путь к директории
    :return: Время последнего изменения (timestamp)
    """
    latest = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        for name in dirnames + filenames:
            full_path = os.path.join(dirpath, name)
            try:
                mtime = os.path.getmtime(full_path)
                if mtime > latest:
                    latest = mtime
            except Exception:
                pass
    return latest

def save_index_meta(root_path):
    """
    Сохраняет метаданные индекса Whoosh (путь и время последней индексации).
    :param root_path: Путь к директории
    """
    meta_path = get_user_meta_path()
    meta = {
        "root_path": root_path,
        "last_indexed_at": get_latest_mtime(root_path)
    }
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

def load_index_meta():
    """
    Загружает метаданные индекса Whoosh для текущего пользователя.
    :return: Словарь с метаданными или None
    """
    meta_path = get_user_meta_path()
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_reindex_needed(root_path):
    """
    Проверяет, требуется ли переиндексация директории (по времени изменения файлов).
    :param root_path: Путь к директории
    :return: True, если требуется переиндексация, иначе False
    """
    meta = load_index_meta()
    if not meta:
        return True
    last_indexed_at = meta.get("last_indexed_at", 0)
    latest_mtime = get_latest_mtime(root_path)
    return latest_mtime > last_indexed_at

def index_directory(root_path, progress_callback=None):
    """
    Индексирует директорию для поиска с помощью Whoosh.
    :param root_path: Путь к директории
    :param progress_callback: Функция для обновления прогресса (count, total)
    """
    ix = create_or_open_index()
    writer = AsyncWriter(ix)
    # Подсчёт общего количества
    total = 0
    for _, dirnames, filenames in os.walk(root_path):
        total += len(dirnames) + len(filenames)
    if total == 0:
        total = 1
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        for name in dirnames + filenames:
            full_path = os.path.join(dirpath, name)
            try:
                writer.update_document(
                    path=full_path,
                    name=name,
                    content=full_path
                )
            except Exception as e:
                pass
            count += 1
            if progress_callback:
                progress_callback(count, total)
    writer.commit()
    save_index_meta(root_path)

def search(query, limit=20):
    """
    Выполняет морфологический (fuzzy) поиск по имени файла/папки с помощью Whoosh.
    :param query: Поисковый запрос
    :param limit: Максимальное количество результатов
    :return: Список кортежей (путь, имя)
    """
    try:
        ix = create_or_open_index()
        with ix.searcher() as searcher:
            parser = MultifieldParser(["name"], schema=ix.schema)  # Только по имени
            parser.add_plugin(FuzzyTermPlugin())
            fuzzy_query = " ".join(f"{w}~2" for w in query.split())
            q = parser.parse(fuzzy_query)
            results = searcher.search(q, limit=limit)
            return [(hit["path"], hit["name"]) for hit in results]
    except Exception as e:
        clear_index()
        create_or_open_index()
        return []

__all__ = ["get_user_index_dir", "get_user_meta_path", "create_or_open_index", "clear_index", "index_directory", "search", "is_reindex_needed"] 