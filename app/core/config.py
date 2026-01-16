from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict


class Settings(BaseSettings):
    # ======================
    # App
    # ======================
    app_name: str = "Carto API"
    env: str = "dev"
    debug: bool = False

    # ======================
    # CRS
    # ======================
    crs_local: str = "EPSG:22195"
    crs_wgs84: str = "EPSG:4326"

    # ======================
    # OSM
    # ======================
    osm_default_radius: int = 300
    osm_timeout: int = 60

    # ======================
    # Paths base
    # ======================
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    ENTRADA_DIR: Path = DATA_DIR / "entrada"
    SALIDA_DIR: Path = DATA_DIR / "salida"
    LOG_DIR: Path = PROJECT_ROOT / "log"

    # ======================
    # Pydantic v2 config
    # ======================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        arbitrary_types_allowed=True,
    )


settings = Settings()

# ======================
# asegurar directorios
# ======================
settings.ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
settings.SALIDA_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
