from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class Project:
    """
    Модель данных проекта.
    :param number: Номер проекта
    :param name: Название проекта
    :param customer: Заказчик
    :param status: Статус проекта (active, completed, archived)
    :param path: Путь к папке проекта
    :param created_date: Дата создания проекта
    :param modified_date: Дата последнего изменения
    """
    id: int
    number: str
    name: str
    customer: str
    chief_engineer: str     # Главный инженер проекта
    status: str     # active, completed, archived
    address: str
    path: str
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Автоматическая инициализация после создания объекта"""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Создать из словаря"""
        return cls(**data)

    def get_path(self, projects_path: str | Path) -> Path:
        return Path(projects_path) / self.path
