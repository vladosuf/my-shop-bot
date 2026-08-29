import logging
import sys
from datetime import datetime
from pathlib import Path

# Создаём папку для логов, если её нет
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Настройка логирования
def setup_logger():
    """Настраивает логирование в файл и консоль"""
    
    # Создаём логгер
    logger = logging.getLogger("bot_logger")
    logger.setLevel(logging.INFO)
    
    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Логи в файл (ежедневные файлы)
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/bot_{today}.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Логи в консоль (для Render)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики в логгер
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаём экземпляр логгера
logger = setup_logger()