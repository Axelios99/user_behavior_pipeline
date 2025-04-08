from pipeline import load_data_to_process
from utils import setup_logger
from config import PIPELINE_LOG

if __name__ == "__main__":
    # Inicia el logger general
    pipeline_logger = setup_logger("pipeline", PIPELINE_LOG)
    pipeline_logger.info("Iniciando el pipeline de carga de datos...")
    
    #Carga de datos
    prints, taps, pays = load_data_to_process(pipeline_logger = pipeline_logger)
    pipeline_logger.info("Carga de datos completada.")
    