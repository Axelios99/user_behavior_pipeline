import pandas as pd
import logging
import csv
from pathlib import Path
from config import PRINTS_FILE, TAPS_FILE, PAYS_FILE, PRINTS_LOG, TAPS_LOG, PAYS_LOG

# Mejorado: Crear logger con protección contra handlers duplicados
def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Solo añadir handler si no hay uno de tipo FileHandler
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Cargar json genericos
def load_json_lines(path: str, logger: logging.Logger) -> pd.DataFrame:
    valid_rows = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                try:
                    row = pd.read_json(line, lines=True)
                    for col in row.columns:
                        if isinstance(row.at[0, col], dict):
                            nested_df = row[col].apply(pd.Series)
                            nested_df.columns = [f"{col}_{subcol}" for subcol in nested_df.columns]
                            row = pd.concat([row.drop(columns=[col]), nested_df], axis=1)
                    valid_rows.append(row)
                except Exception as e:
                    logger.warning(f"Error en línea {i}: {str(e)} | Línea: {line.strip()}")
        if valid_rows:
            return pd.concat(valid_rows, ignore_index=True)
        else:
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"No se pudo abrir el archivo: {str(e)}")
        return pd.DataFrame()

# Cargar csv genericos
def load_csv_lines(path: str, logger: logging.Logger) -> pd.DataFrame:
    valid_rows = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                logger.warning("Archivo CSV vacío")
                return pd.DataFrame()

            for i, line in enumerate(reader, start=2):
                try:
                    if len(line) != len(headers):
                        raise ValueError("Cantidad de campos no coincide con el encabezado")
                    row_dict = dict(zip(headers, line))
                    valid_rows.append(row_dict)
                except Exception as e:
                    logger.warning(f"Error en línea {i}: {str(e)} | Línea: {','.join(map(str, line)).strip()}")
        if valid_rows:
            return pd.DataFrame(valid_rows)
        else:
            return pd.DataFrame(columns=headers)
    except Exception as e:
        logger.error(f"No se pudo abrir el archivo: {str(e)}")
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
    pays = load_csv_lines(PAYS_FILE, pays_logger)

    # Retorna los dataframes cargados.
    return prints, taps, pays