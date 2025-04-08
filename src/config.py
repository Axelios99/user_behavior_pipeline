from pathlib import Path

# Rutas
DATA_PATH = Path("data")
LOG_PATH = Path("logs")
OUTPUT_PATH = Path("output")

# Logs generales
PIPELINE_LOG = LOG_PATH / "pipeline.log"

# Archivos de datos
PRINTS_FILE = DATA_PATH / "prints.json"
TAPS_FILE = DATA_PATH / "taps.json"
PAYS_FILE = DATA_PATH / "pays.csv"

# Logs individuales
PRINTS_LOG = LOG_PATH / "prints_load_errors.log"
TAPS_LOG = LOG_PATH / "taps_load_errors.log"
PAYS_LOG = LOG_PATH / "pays_load_errors.log"

# Ventanas de tiempo para el modelo
DAYS_WEEK_WINDOW_DAYS = 6 # Última semana → 7 días (día actual + 6 días atrás)
HISTORICAL_WINDOW_DAYS = 21 # Historial → 3 semanas hacia atrás desde el inicio de esa última semana

# Output
ENRICH_DATA = OUTPUT_PATH / "data_enrich.csv"