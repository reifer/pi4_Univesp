import os
from pyspark.sql import SparkSession

def ingest_enem_data_by_year(year: int):
    spark = SparkSession.builder \
        .appName(f"EnemIngestion_{year}") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

    base_dirs = [
        f"data/raw/microdados_enem_{year}/DADOS",
        f"data/raw/enem_{year}/DADOS",
        f"data/raw/DADOS",
        f"/home/reifer/Downloads/microdados_enem_{year}/DADOS",
        f"data/raw"
    ]
    
    # Nomes possíveis para o arquivo unificado oficial do INEP nos anos recentes
    target_filenames = [f"MICRODADOS_ENEM_{year}.csv", f"PARTICIPANTES_{year}.csv"]
    
    data_dir = None
    target_file = None
    for d in base_dirs:
        for fname in target_filenames:
            if os.path.exists(os.path.join(d, fname)):
                data_dir = d
                target_file = fname
                break
        if data_dir:
            break

    if not data_dir or not target_file:
        print(f"Aviso crítico: Arquivo de microdados para o ano {year} não encontrado.")
        spark.stop()
        return

    microdados_csv = os.path.join(data_dir, target_file)
    output_parquet = f"data/processed/enem_{year}_cleaned_parquet"
    resultados_output = f"data/processed/enem_{year}_resultados_parquet"

    print(f"Iniciando leitura dos microdados do ENEM {year} em '{microdados_csv}'...")

    if os.path.exists(microdados_csv):
        df_microdados = spark.read.csv(
            microdados_csv, 
            header=True, 
            sep=";", 
            encoding="ISO-8859-1", 
            inferSchema=False
        )

        print(f"Gravando dataset limpo e unificado para {year} em '{output_parquet}'...")
        df_microdados.write.mode("overwrite").parquet(output_parquet)
        
        # Como o arquivo unificado do INEP já possui as notas e dados de escola, 
        # gravamos uma cópia também no caminho de resultados para manter compatibilidade total com o transform.py
        df_microdados.write.mode("overwrite").parquet(resultados_output)
        
        print(f"Pipeline de Ingestão para o ano {year} concluído com sucesso!")
    else:
        print(f"Erro: Arquivo {microdados_csv} não encontrado!")

    spark.stop()

if __name__ == "__main__":
    for target_year in [2024, 2025]:
        ingest_enem_data_by_year(target_year)