import pandas as pd
import logging
from pathlib import Path
from datetime import timedelta

# Creacion del logger
def setup_logger(name, log_file, level=logging.INFO):
    Path("logs").mkdir(exist_ok=True)  # Crea carpeta si no existe
    handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler.setFormatter(formatter)

    # Evita handlers duplicados si ya está creado
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger

#Carga un archivo Json y maneja errores.
def load_json_lines(path, logger):
    valid_rows = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                try:
                    row = pd.read_json(line, lines=True)
                    valid_rows.append(row)
                except Exception as e:
                    logger.warning(f"Error en línea {i}: {str(e)}")
        if valid_rows:
            return pd.concat(valid_rows, ignore_index=True)
        else:
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"No se pudo abrir el archivo: {str(e)}")
        return pd.DataFrame()

#Carga un archivo CSV y maneja errores.
def load_csv(path, logger):
    """Carga un archivo CSV con manejo de errores."""
    try:
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Error al leer CSV: {str(e)}")
        return pd.DataFrame()