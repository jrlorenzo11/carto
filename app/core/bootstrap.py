from app.core.config import settings


def init_dirs():
    for path in [
        settings.ENTRADA_DIR,
        settings.SALIDA_DIR,
        settings.LOG_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
