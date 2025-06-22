import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import socket

MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
INDEX_PATH = 'storage/faiss_index.bin'
PATHS_PATH = 'storage/faiss_paths.npy'
META_PATH = 'storage/faiss_index.meta.json'
N_DIM = 384  # Размерность эмбеддинга для выбранной модели

def get_user_faiss_paths():
    computer_name = socket.gethostname()
    base = os.path.join("storage", "users", computer_name)
    return {
        "index": os.path.join(base, "faiss_index.bin"),
        "paths": os.path.join(base, "faiss_paths.npy"),
        "meta": os.path.join(base, "faiss_index.meta.json"),
    }

class SemanticSearchService:
    """
    Сервис для семантического поиска файлов и папок с использованием SentenceTransformer и FAISS.
    Позволяет индексировать директории, выполнять быстрый поиск по эмбеддингам и получать результаты с оценкой схожести.
    """
    def __init__(self):
        """
        Инициализация сервиса семантического поиска. Загружает модель и индекс.
        """
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = None
        self.paths = []
        self._load_index()

    def _load_index(self):
        """
        Загружает индекс FAISS и список путей для текущего пользователя.
        """
        faiss_paths = get_user_faiss_paths()
        if os.path.exists(faiss_paths["index"]) and os.path.exists(faiss_paths["paths"]):
            self.index = faiss.read_index(faiss_paths["index"])
            self.paths = np.load(faiss_paths["paths"], allow_pickle=True).tolist()
        else:
            self.index = faiss.IndexFlatL2(N_DIM)
            self.paths = []

    def index_directory(self, root_path, progress_callback=None):
        """
        Индексирует директорию для семантического поиска.
        :param root_path: str - путь к директории
        :param progress_callback: callable - функция для обновления прогресса
        """
        faiss_paths = get_user_faiss_paths()
        paths = []
        names = []
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
                paths.append(full_path)
                names.append(name)
                count += 1
                if progress_callback:
                    progress_callback(count, total)
        texts = [os.path.basename(p) for p in paths]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        self.index = faiss.IndexFlatL2(N_DIM)
        self.index.add(np.array(embeddings, dtype=np.float32))
        self.paths = paths
        os.makedirs(os.path.dirname(faiss_paths["index"]), exist_ok=True)
        faiss.write_index(self.index, faiss_paths["index"])
        np.save(faiss_paths["paths"], np.array(self.paths))
        save_index_meta(root_path)

    def search(self, query, limit=20):
        """
        Выполняет семантический поиск по запросу.
        :param query: str - поисковый запрос
        :param limit: int - максимальное количество результатов
        :return: list[str] - найденные пути
        """
        faiss_paths = get_user_faiss_paths()
        if self.index is None or len(self.paths) == 0:
            return []
        emb = self.model.encode([query])
        D, I = self.index.search(np.array(emb, dtype=np.float32), limit)
        results = []
        for idx in I[0]:
            if idx < len(self.paths):
                results.append(self.paths[idx])
        return results

    def search_with_scores(self, query, limit=20):
        """
        Выполняет семантический поиск с возвращением оценок схожести.
        :param query: str - поисковый запрос
        :param limit: int - максимальное количество результатов
        :return: list[tuple[str, float]] - найденные пути и расстояния (чем меньше, тем ближе)
        """
        faiss_paths = get_user_faiss_paths()
        if self.index is None or len(self.paths) == 0:
            return []
        emb = self.model.encode([query])
        D, I = self.index.search(np.array(emb, dtype=np.float32), limit)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.paths):
                results.append((self.paths[idx], dist))
        results.sort(key=lambda x: x[1])
        return results

def get_latest_mtime(root_path):
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
    faiss_paths = get_user_faiss_paths()
    meta_path = faiss_paths["meta"]
    meta = {
        "root_path": root_path,
        "last_indexed_at": get_latest_mtime(root_path)
    }
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

def load_index_meta():
    faiss_paths = get_user_faiss_paths()
    meta_path = faiss_paths["meta"]
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_reindex_needed(root_path):
    meta = load_index_meta()
    if not meta:
        return True
    last_indexed_at = meta.get("last_indexed_at", 0)
    latest_mtime = get_latest_mtime(root_path)
    return latest_mtime > last_indexed_at 