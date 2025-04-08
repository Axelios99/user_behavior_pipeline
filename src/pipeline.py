import pandas as pd
from datetime import timedelta
from utils import setup_logger, load_json_lines, load_csv_lines
from config import PRINTS_FILE, TAPS_FILE, PAYS_FILE, PRINTS_LOG, TAPS_LOG, PAYS_LOG

def preprocess_prints(prints: pd.DataFrame) -> pd.DataFrame:
    prints["day"] = pd.to_datetime(prints["day"])
    return prints

def preprocess_taps(taps: pd.DataFrame) -> pd.DataFrame:
    taps["day"] = pd.to_datetime(taps["day"])
    return taps

def preprocess_pays(pays: pd.DataFrame) -> pd.DataFrame:
    pays["pay_date"] = pd.to_datetime(pays["pay_date"])
    pays["total"] = pd.to_numeric(pays["total"], errors="coerce")
    pays = pays.rename(columns={"pay_date": "day"})
    return pays


#Funcion de carga de la data (llama a las funciones de carga de cada archivo).
def load_data_to_process():

    # Iniciar los loggers de la carga de datos.
    prints_logger = setup_logger("prints", PRINTS_LOG)
    taps_logger = setup_logger("taps", TAPS_LOG)
    pays_logger = setup_logger("pays", PAYS_LOG)
    print("logger creado")

    # Carga los datos de cada archivo.
    print("Cargando prints...")
    prints = load_json_lines(PRINTS_FILE, prints_logger)
    print("Cargando taps...")
    taps = load_json_lines(TAPS_FILE, taps_logger)
    print("Cargando pays...")
    pays = load_csv_lines(PAYS_FILE, pays_logger)

    # Retorna los dataframes cargados.
    return prints , taps, pays