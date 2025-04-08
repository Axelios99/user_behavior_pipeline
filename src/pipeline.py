import pandas as pd
import logging
from time import time
from datetime import timedelta
from utils import setup_logger, load_json_lines, load_csv_lines
from config import PRINTS_FILE, TAPS_FILE, PAYS_FILE, PRINTS_LOG, TAPS_LOG, PAYS_LOG, DAYS_WEEK_WINDOW_DAYS, HISTORICAL_WINDOW_DAYS
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

def preprocess_taps(df: pd.DataFrame) -> pd.DataFrame:
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

def preprocess_pays(df: pd.DataFrame) -> pd.DataFrame:
    # Renombrar columnas anidadas si vienen como event_data.*
    df["pay_date"] = pd.to_datetime(df["pay_date"])
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df['user_id'] = df['user_id'].astype('string')
    df['value_prop'] = df['value_prop'].astype('string')
    return df


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

def build_dataset_enrich(df_prints: pd.DataFrame, df_taps: pd.DataFrame, df_pays: pd.DataFrame, pipeline_logger: logging.Logger) -> pd.DataFrame:
    
    start = time()
    #Fecha mas reciente en prints
    last_day_print = df_prints['day'].max()
    #Fecha del dia de inicio de la ultima semana.
    date_init_last_week = last_day_print - pd.Timedelta(days=DAYS_WEEK_WINDOW_DAYS)

    #Extraemos el dataset de la ultima semana (prints).
    df_prints_last_week = df_prints[
        df_prints['day'].between(date_init_last_week, last_day_print)
    ].copy()

    # Aplicamos enrich_print_row fila por fila al DataFrame filtrado
    df_enriched = df_prints_last_week.copy()

    #Pasamos cada fila 1 a 1 (apply) a la funcion enrich_print_row y la unión se hace mediante indice.
    df_enriched = df_enriched.join(
        df_enriched.apply(lambda row: enrich_print_row(row, df_prints, df_taps, df_pays), axis=1)
    )

    duration = time() - start
    pipeline_logger.info(f"Tiempo de enrequecimiento de data: {timedelta(seconds=duration)}")

    return df_enriched


def enrich_print_row(row, df_prints, df_taps, df_pays) -> pd.Series:
    # Extraer los datos clave de la fila actual de prints
    user_id = row['user_id']
    value_prop = row['value_prop']
    print_day = row['day']  # Fecha del print actual

    # Definir la ventana de análisis: 3 semanas antes del print (excluyendo el mismo día)
    window_start = print_day - pd.Timedelta(days=HISTORICAL_WINDOW_DAYS)  # Día inicial del rango histórico
    window_end = print_day - pd.Timedelta(days=1)     # Día final del rango histórico

    # 1. Saber si el usuario hizo click (tap) ese mismo día en esa value_prop
    clicked = df_taps[
        (df_taps['user_id'] == user_id) &
        (df_taps['value_prop'] == value_prop) &
        (df_taps['day'] == print_day)
    ].shape[0] > 0  # Si hay al menos 1 fila, hubo tap ese día

    # 2. Contar cuántas veces el usuario vio esa value_prop en los 21 días anteriores
    past_prints_count = df_prints[
        (df_prints['user_id'] == user_id) &
        (df_prints['value_prop'] == value_prop) &
        (df_prints['day'].between(window_start, window_end))
    ].shape[0]

    # 3. Contar cuántas veces el usuario clickeó (tap) esa value_prop en ese mismo rango

    past_taps_count = df_taps[
        (df_taps['user_id'] == user_id) &
        (df_taps['value_prop'] == value_prop) &
        (df_taps['day'].between(window_start, window_end))
    ].shape[0]

    # 4. Filtrar pagos hechos por el usuario en esa value_prop durante ese rango

    past_pays = df_pays[
        (df_pays['user_id'] == user_id) &
        (df_pays['value_prop'] == value_prop) &
        (df_pays['pay_date'].between(window_start, window_end))
    ]

    # 4.a Contar cuántos pagos hizo en esa value_prop en el rango
    past_pays_count = past_pays.shape[0]

    # 4.b Sumar cuánto gastó en total en esos pagos
    past_total_amount = past_pays['total'].sum()


    # 5. Devolver todas las métricas en una serie para agregarlas al DataFrame original

    return pd.Series({
        'clicked': int(clicked),  # Convertimos True/False a 1/0
        'past_prints_count': past_prints_count,
        'past_taps_count': past_taps_count,
        'past_pays_count': past_pays_count,
        'past_total_amount': past_total_amount
    })
