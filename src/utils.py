import pandas as pd
import logging
from pathlib import Path
from datetime import timedelta
from config import PRINTS_FILE, TAPS_FILE, PAYS_FILE, PRINTS_LOG, TAPS_LOG, PAYS_LOG

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

#Carga un archivo Json y maneja errores de carga.
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

#Carga un archivo CSV y maneja errores de carga.
def load_csv(path, logger):
    try:
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Error al leer CSV: {str(e)}")
        return pd.DataFrame()


#Funcion de carga de la data (llama a las funciones de carga de cada archivo).
def load_data():

    # Iniciar los loggers de la carga de datos.
    prints_logger = setup_logger("prints", PRINTS_LOG)
    taps_logger = setup_logger("taps", TAPS_LOG)
    pays_logger = setup_logger("pays", PAYS_LOG)

    # Carga los datos de cada archivo.
    prints = load_json_lines(PRINTS_FILE, prints_logger)
    taps = load_json_lines(TAPS_FILE, taps_logger)
    pays = load_csv(PAYS_FILE, pays_logger)

    # Retorna los dataframes cargados.
    return prints, taps, pays