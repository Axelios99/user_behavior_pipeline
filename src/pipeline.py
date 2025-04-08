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

def build_dataset_enrich(
    df_prints: pd.DataFrame,
    df_taps: pd.DataFrame,
    df_pays: pd.DataFrame,
    pipeline_logger: logging.Logger
) -> pd.DataFrame:
    """
    Enriquecimiento optimizado del dataset de prints con métricas históricas, usando operaciones groupby.

    Parámetros:
    - df_prints: DataFrame con historial de prints
    - df_taps: DataFrame con historial de taps
    - df_pays: DataFrame con historial de pagos
    - pipeline_logger: Logger para registrar información del proceso

    Retorna:
    - DataFrame enriquecido
    """

    start = time()

    # Calcular fechas clave
    last_day = df_prints['day'].max()
    date_init_last_week = last_day - pd.Timedelta(days=DAYS_WEEK_WINDOW_DAYS)
    date_init_historical = date_init_last_week - pd.Timedelta(days=HISTORICAL_WINDOW_DAYS)

    pipeline_logger.info(f"Último día disponible: {last_day}")
    pipeline_logger.info(f"Ventana de última semana: {date_init_last_week.date()} → {last_day.date()}")
    pipeline_logger.info(f"Ventana histórica: {date_init_historical.date()} → {(date_init_last_week - pd.Timedelta(days=1)).date()}")

    # 1. Obtener los prints de la última semana (target del modelo)
    df_prints_last_week = df_prints[
        df_prints['day'].between(date_init_last_week, last_day)
    ].copy()

    # 2. Filtrar datos históricos para métricas agregadas
    historical_prints = df_prints[
        df_prints['day'].between(date_init_historical, date_init_last_week - pd.Timedelta(days=1))
    ]
    historical_taps = df_taps[
        df_taps['day'].between(date_init_historical, date_init_last_week - pd.Timedelta(days=1))
    ]
    historical_pays = df_pays[
        df_pays['pay_date'].between(date_init_historical, date_init_last_week - pd.Timedelta(days=1))
    ]

    # 3. Calcular métricas históricas (cuenta cuantas veces se vio cada value_prop por user_id y value_prop)), para pays tambien suma su valor.

    # 3.1 Agrupa historical_prints por user_id y value_prop y cuenta cuantas veces se vio cada value_prop en las 3 semanas previas (resultado: df con user_id, value_prop y past_prints_count).
    prints_count = historical_prints.groupby(['user_id', 'value_prop']).size().reset_index(name='past_prints_count')
    # 3.2 Agrupa historical_taps por user_id y value_prop y cuenta cuantas veces se vio cada value_prop en las 3 semanas previas (resultado: df con user_id, value_prop y past_taps_count).
    taps_count = historical_taps.groupby(['user_id', 'value_prop']).size().reset_index(name='past_taps_count')
    # 3.3 Agrupa historical_pays por user_id y value_prop y agrega la cantidad de pagos que realizo, asi como el total del valor de los pagos.
    pays_count = historical_pays.groupby(['user_id', 'value_prop']).agg(
        past_pays_count=('pay_date', 'count'),
        past_total_amount=('total', 'sum')
    ).reset_index()

    # 4. Detectar si hubo tap el mismo día del print (clicked)
    taps_same_day = df_taps[['user_id', 'value_prop', 'day']].copy()
    taps_same_day['clicked'] = 1

    # 5. Realizar merges para enriquecer el dataset de prints de la última semana
    df_enriched = df_prints_last_week.merge(
        taps_same_day, on=['user_id', 'value_prop', 'day'], how='left'
    ).merge(
        prints_count, on=['user_id', 'value_prop'], how='left'
    ).merge(
        taps_count, on=['user_id', 'value_prop'], how='left'
    ).merge(
        pays_count, on=['user_id', 'value_prop'], how='left'
    )

    # 6. Rellenar valores nulos con ceros donde no hay historial previo
    df_enriched['clicked'] = df_enriched['clicked'].fillna(0).astype(int)
    df_enriched['past_prints_count'] = df_enriched['past_prints_count'].fillna(0).astype(int)
    df_enriched['past_taps_count'] = df_enriched['past_taps_count'].fillna(0).astype(int)
    df_enriched['past_pays_count'] = df_enriched['past_pays_count'].fillna(0).astype(int)
    df_enriched['past_total_amount'] = df_enriched['past_total_amount'].fillna(0.0)

    duration = time() - start
    pipeline_logger.info(f"Enriquecimiento finalizado en: {timedelta(seconds=duration)}")

    return df_enriched