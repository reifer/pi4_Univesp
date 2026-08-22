import os
from pyspark.sql import SparkSession

def ingest_enem_data():
    # Inicializa a sessão Spark com alocação otimizada de memória
    spark = SparkSession.builder \
        .appName("EnemIngestion") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

    # Caminhos para os datasets de Participantes e Resultados
    participantes_input = "data/raw/PARTICIPANTES_2025.csv"
    participantes_output = "data/processed/enem_2025_parquet"

    resultados_input = "data/raw/RESULTADOS_2025.csv"
    resultados_output = "data/processed/enem_2025_resultados_parquet"

    # 1. Ingestão do arquivo de PARTICIPANTES (se necessário ou para atualização)
    if os.path.exists(participantes_input):
        print(f"Iniciando leitura do dataset de Participantes ({participantes_input})...")
        df_part = spark.read.csv(participantes_input, header=True, sep=";", encoding="ISO-8859-1")
        df_part.write.mode("overwrite").parquet(participantes_output)
        print(f"Participantes salvos com sucesso em: {participantes_output}")
    else:
        print(f"Aviso: Arquivo {participantes_input} não encontrado. Pulando etapa.")

    # 2. Ingestão do arquivo de RESULTADOS (Notas) - Fase 1
    if os.path.exists(resultados_input):
        print(f"Iniciando leitura do dataset de Resultados ({resultados_input})...")
        df_res = spark.read.csv(resultados_input, header=True, sep=";", encoding="ISO-8859-1")
        df_res.write.mode("overwrite").parquet(resultados_output)
        print(f"Resultados salvos com sucesso em: {resultados_output}")
    else:
        print(f"Erro: Arquivo {resultados_input} não encontrado em data/raw/!")

    print("Pipeline de Ingestão (Fase 1) concluído com sucesso!")

if __name__ == "__main__":
    ingest_enem_data()