from pathlib import Path
from app.core.paths import ENTRADA_DIR

def resolve_entrada(path_str: str) -> Path:
    """
    Convierte 'entrada/archivo.csv' o 'archivo.csv'
    en un Path absoluto seguro.
    """
    path = Path(path_str).name  # elimina carpetas peligrosas
    full_path = ENTRADA_DIR / path

    if not full_path.exists():
        raise FileNotFoundError(f"No existe: {full_path}")

    return full_path
