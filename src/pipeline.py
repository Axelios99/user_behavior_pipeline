import pandas as pd
import logging
from time import time
from datetime import timedelta
from utils import setup_logger, load_json_lines, load_csv_lines
from config import PRINTS_FILE, TAPS_FILE, PAYS_FILE, PRINTS_LOG, TAPS_LOG, PAYS_LOG
from typing import Tuple

def preprocess_prints(df: pd.DataFrame) -> pd.DataFrame:
    # Renombrar columnas anidadas si vienen como event_data.*
    df = df.rename(columns={
        'event_data.position': 'position',
        'event_data.value_prop': 'value_prop'
    })

    # Conversión de tipos
    df['day'] = pd.to_datetime(df['day'], errors='coerce')  # NaT si hay errores
    df['user_id'] = df['user_id'].astype('string')
    df['value_prop'] = df['value_prop'].astype('string')
    df['position'] = pd.to_numeric(df['position'], errors='coerce').astype('Int64')

    # Eliminar registros incompletos
    df = df.dropna(subset=['day', 'user_id', 'value_prop', 'position'])

    return df

def preprocess_taps(taps: pd.DataFrame) -> pd.DataFrame:
    # Renombrar columnas anidadas si vienen como event_data.*
    df = df.rename(columns={
        'event_data.position': 'position',
        'event_data.value_prop': 'value_prop'
    })

    # Conversión de tipos
    df['day'] = pd.to_datetime(df['day'], errors='coerce')  # NaT si hay errores
    df['user_id'] = df['user_id'].astype('string')
    df['value_prop'] = df['value_prop'].astype('string')
    df['position'] = pd.to_numeric(df['position'], errors='coerce').astype('Int64')

    # Eliminar registros incompletos
    df = df.dropna(subset=['day', 'user_id', 'value_prop', 'position'])

    return df

def preprocess_pays(pays: pd.DataFrame) -> pd.DataFrame:
    pays["pay_date"] = pd.to_datetime(pays["pay_date"])
    pays["total"] = pd.to_numeric(pays["total"], errors="coerce")
    pays = pays.rename(columns={"pay_date": "day"})
    return pays


#Funcion de carga de la data (llama a las funciones de carga de cada archivo).
def load_data_to_process(pipeline_logger: logging.Logger) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Loggers individuales
    prints_logger = setup_logger("prints", PRINTS_LOG)
    taps_logger = setup_logger("taps", TAPS_LOG)
    pays_logger = setup_logger("pays", PAYS_LOG)

    # Prints
    start = time()
    prints = load_json_lines(PRINTS_FILE, prints_logger)
    duration = time() - start
    pipeline_logger.info(f"""
Dataset: PRINTS
- Columnas: {list(prints.columns)}
- Registros: {len(prints)}
- Tiempo de carga: {duration:.2f} seg
""")
    if prints.empty:
        pipeline_logger.warning("El dataset 'prints' está vacío.")

    # Taps
    start = time()
    taps = load_json_lines(TAPS_FILE, taps_logger)
    duration = time() - start
    pipeline_logger.info(f"""
Dataset: TAPS
- Columnas: {list(taps.columns)}
- Registros: {len(taps)}
- Tiempo de carga: {duration:.2f} seg
""")
    if taps.empty:
        pipeline_logger.warning("El dataset 'taps' está vacío.")

    # Pays
    start = time()
    pays = load_csv_lines(PAYS_FILE, pays_logger)
    duration = time() - start
    pipeline_logger.info(f"""
Dataset: PAYS
- Columnas: {list(pays.columns)}
- Registros: {len(pays)}
- Tiempo de carga: {duration:.2f} seg
""")
    if pays.empty:
        pipeline_logger.warning("El dataset 'pays' está vacío.")

    # Resumen final
    pipeline_logger.info("Resumen general de carga de datos:")
    pipeline_logger.info(f"PRINTS: {len(prints)} filas | {prints.shape[1]} columnas")
    pipeline_logger.info(f"TAPS:   {len(taps)} filas | {taps.shape[1]} columnas")
    pipeline_logger.info(f"PAYS:   {len(pays)} filas | {pays.shape[1]} columnas")

    return prints, taps, pays

#Preprocess data
def preprocess_data(prints: pd.DataFrame, taps: pd.DataFrame, pays: pd.DataFrame, pipeline_logger: logging.Logger) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Preprocesar prints
    start = time()
    prints = preprocess_prints(prints)
    duration = time() - start
    pipeline_logger.info(f"Tiempo de preprocesamiento de PRINTS: {timedelta(seconds=duration)}")

    # Preprocesar taps
    start = time()
    taps = preprocess_taps(taps)
    duration = time() - start
    pipeline_logger.info(f"Tiempo de preprocesamiento de TAPS: {timedelta(seconds=duration)}")

    # Preprocesar pays
    start = time()
    pays = preprocess_pays(pays)
    duration = time() - start
    pipeline_logger.info(f"Tiempo de preprocesamiento de PAYS: {timedelta(seconds=duration)}")

    return prints, taps, pays