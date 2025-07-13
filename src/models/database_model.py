from datetime import datetime
from pathlib import Path
from typing import Any

from pony.orm import Database as PonyDatabase
from pony.orm import PrimaryKey, Required, Optional, Set, db_session, select


class Database:
    def __init__(self, db: PonyDatabase):
        """
        Инициализация моделей базы данных.
        :param db: Экземпляр базы данных Pony ORM
        """
        self.db = db
        self.models = self._define_models()

    def _define_models(self) -> Any:
        """Определение моделей таблиц базы данных"""
        class ProjectTable(self.db.Entity):
            """
            Модель таблицы проектов.
            Основная таблица для хранения информации о проектах.
            """
            _table_ = "Объекты"
            id = PrimaryKey(int, auto=True)
            number = Required(str)  # Номер проекта
            name = Required(str)  # Название проекта
            customer = Required(str)  # Заказчик
            chief_engineer = Required(str)  # Главный инженер проекта
            status = Required(str)  # Статус проекта (active, completed, archived)
            address = Required(str)  # Адрес объекта
            path = Required(str)  # Путь к папке проекта
            created_date = Required(datetime, default=datetime.now)
            modified_date = Required(datetime, default=datetime.now)

            def __str__(self):
                return f"Project(id={self.id}, number='{self.number}', name='{self.name}')"

            def to_dict(self) -> dict:
                """Конвертация в словарь"""
                return {
                    'id': self.id,
                    'number': self.number,
                    'name': self.name,
                    'customer': self.customer,
                    'chief_engineer': self.chief_engineer,
                    'status': self.status,
                    'address': self.address,
                    'path': self.path,
                    'created_date': self.created_date.isoformat(),
                    'modified_date': self.modified_date.isoformat()
                }

        class Models:
            Project = ProjectTable

        return Models
