from dataclasses import dataclass
from pathlib import Path


@dataclass
class Parameters:
    """
    Модель параметров вычисления отходов древесины.
    :param root_percentage_wood: Процент корневой системы у дерева
    :param root_percentage_shrub: Процент корневой системы у кустарника
    """
    root_percentage_wood: float
    root_percentage_shrub: float

@dataclass
class Project:
    """
    Модель проекта.
    :param dxf_files: DXF файлы
    :param xls_files: XLSX файлы
    :param out_files: Выходные XLSX файлы
    """
    project_path: Path
    dxf_files: list[Path]
    xls_files: list[Path]
    out_files: list[Path]
