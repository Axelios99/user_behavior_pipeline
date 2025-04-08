from pipeline import load_data_to_process, preprocess_data, build_dataset_enrich
from utils import setup_logger, export_to_csv
from config import PIPELINE_LOG, ENRICH_DATA

if __name__ == "__main__":
    # Inicia el logger general
    pipeline_logger = setup_logger("pipeline", PIPELINE_LOG)
    pipeline_logger.info("Iniciando el pipeline de carga de datos...")
    
    #Carga de datos
    prints, taps, pays = load_data_to_process(pipeline_logger = pipeline_logger)
    pipeline_logger.info("Carga de datos completada.")

    #Preprocesamiento de datos
    prints, taps, pays = preprocess_data(prints= prints, 
                                         taps= taps, 
                                         pays= pays, 
                                         pipeline_logger = pipeline_logger)
    pipeline_logger.info("Preprocesamiento de datos completado.")

    #Enriquecimiento de datos
    df_enriched = build_dataset_enrich(df_prints= prints, 
                                        df_taps= taps, 
                                        df_pays= pays, 
                                        pipeline_logger = pipeline_logger)
    
    pipeline_logger.info("Enriquecimiento de datos completado.")

    pipeline_logger.info(f"Exportando datos enriquecidos a {ENRICH_DATA}...")
    export_to_csv(df = df_enriched, 
                  output_path= ENRICH_DATA, 
                  logger= pipeline_logger)
    pipeline_logger.info("Exportación completada.")
    pipeline_logger.info("Pipeline de carga de datos finalizado.")