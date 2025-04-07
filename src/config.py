from pathlib import Path

# Rutas
DATA_PATH = Path("data")
LOG_PATH = Path("logs")
OUTPUT_PATH = Path("output")

# Logs generales
PIPELINE_LOG = LOG_PATH / "pipeline.log"

# Archivos específicos
PRINTS_FILE = DATA_PATH / "prints.json"
TAPS_FILE = DATA_PATH / "taps.json"
PAYS_FILE = DATA_PATH / "pays.csv"

# Logs individuales
PRINTS_LOG = LOG_PATH / "prints_load.log"
TAPS_LOG = LOG_PATH / "taps_load.log"
PAYS_LOG = LOG_PATH / "pays_load.log"

# Otros parámetros del pipeline
PRINT_WINDOW_DAYS = 7
HISTORICAL_WINDOW_DAYS = 21