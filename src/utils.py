import os
import pandas as pd
import logging
import csv
import json
from pathlib import Path


# Creacion de logger
def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    #Limpiar handlers previos
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

# Cargar json genericos
def load_json_lines(path: str, logger: logging.Logger) -> pd.DataFrame:
    valid_rows = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, start=1):
                try:
                    row_dict = json.loads(line)
                    valid_rows.append(row_dict)
                except Exception as e:
                    logger.warning(f"Error en línea {i}: {str(e)} | Línea: {line.strip()}")

        if valid_rows:
            df = pd.json_normalize(valid_rows)
            return df
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

#   Exportar csv
def export_to_csv(df: pd.DataFrame, output_path: str, logger: logging.Logger) -> None:
    try:
        # Crear carpeta destino si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Exportar a CSV
        df.to_csv(output_path, index=False, encoding='utf-8')

        # Confirmar éxito
        logger.info(f"CSV exportado correctamente en: {output_path}")

    except Exception as e:
        # Log de error si ocurre una excepción
        logger.error(f"Error al exportar el CSV a '{output_path}': {str(e)}", exc_info=True)
