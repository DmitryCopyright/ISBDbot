import logging

def setup_logging(level=logging.INFO):
    # Настраиваем логирование
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=level)

def log_error(error, description=""):
    # Логгируем ошибки
    logging.error(f"Произошла ошибка: {description} | Exception: {error}")
