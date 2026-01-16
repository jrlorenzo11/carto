import logging
from app.core.config import settings

def setup_logger():
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("app/log/app.log"),
            logging.StreamHandler()
        ]
    )

setup_logger()
