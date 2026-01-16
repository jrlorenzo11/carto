from pathlib import Path

# raíz del proyecto (carto/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
ENTRADA_DIR = DATA_DIR / "entrada"
SALIDA_DIR = DATA_DIR / "salida"

# asegurar que existan
ENTRADA_DIR.mkdir(parents=True, exist_ok=True)
SALIDA_DIR.mkdir(parents=True, exist_ok=True)
