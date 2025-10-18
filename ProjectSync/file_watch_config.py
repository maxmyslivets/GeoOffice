"""
Конфигурация для мониторинга файловой системы.
Содержит настройки по умолчанию и паттерны фильтрации.
"""

from typing import Set, Dict, Any

# Паттерны файлов для игнорирования
DEFAULT_IGNORED_PATTERNS: Set[str] = {
    # Временные файлы
    '*.tmp', '*.temp', '*.swp', '*.~*', '*.lock', '*.pid',
    
    # Системные файлы
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    
    # Файлы версионного контроля
    '.git', '.svn', '.hg', '.bzr',
    
    # Кэш и временные директории
    '__pycache__', 'node_modules', '.pytest_cache',
    '.mypy_cache', '.coverage', '.tox',
    
    # Скомпилированные файлы
    '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe',
    
    # Логи и резервные копии
    '*.log', '*.bak', '*.backup', '*.old',
    
    # Сокеты и именованные каналы
    '*.sock', '*.socket', '*.fifo',
    
    # Медиа файлы (если не нужны для проектов)
    '*.mp4', '*.avi', '*.mov', '*.wmv', '*.flv',
    '*.mp3', '*.wav', '*.flac', '*.aac',
    '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff',
    
    # Архивы (если не нужны для проектов)
    '*.zip', '*.rar', '*.7z', '*.tar', '*.gz', '*.bz2',
}

# Расширения файлов проектов GeoOffice
PROJECT_FILE_EXTENSIONS: Set[str] = {
    '.geo_office_project'
}

# Настройки производительности по умолчанию
DEFAULT_PERFORMANCE_SETTINGS: Dict[str, Any] = {
    'debounce_time': 2.0,  # секунды
    'max_events_per_second': 10,
    'max_pending_events': 100,
    'event_cleanup_interval': 60.0,  # секунды
}

# Настройки логирования
LOGGING_SETTINGS: Dict[str, Any] = {
    'log_file_events': True,
    'log_ignored_events': False,
    'log_performance_stats': True,
    'log_rate_limiting': True,
}

# Настройки мониторинга по умолчанию
DEFAULT_WATCH_SETTINGS: Dict[str, Any] = {
    'recursive': True,
    'ignore_directories': True,
    'case_sensitive': True,
    'follow_symlinks': False,
}