import os
from pyspark.sql import SparkSession
from downloader import ingest_legacy_years, unify_recent_years

def run_full_ingestion():
    print("==================================================")
    print(" INICIANDO PIPELINE DE INGESTÃO GERAL (2021-2025) ")
    print("==================================================")
    
    spark_tmp_dir = os.path.abspath("data/.spark_tmp")
    os.makedirs(spark_tmp_dir, exist_ok=True)
    
    spark = SparkSession.builder \
        .appName("EnemIngestionMasterPipeline") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.local.dir", spark_tmp_dir) \
        .config("spark.sql.shuffle.partitions", "32") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    os.makedirs("data/processed", exist_ok=True)
    
    # 1. Processa anos legados (2021 a 2023)
    for ano in [2021, 2022, 2023]:
        ingest_legacy_years(ano, spark)
        
    # 2. Processa anos recentes fragmentados (2024 e 2025)
    for ano in [2024, 2025]:
        unify_recent_years(ano, spark)
        
    print("\n==================================================")
    print("🎉 TODAS AS ETAPAS DE INGESTÃO CONCLUÍDAS COM SUCESSO!")
    print("==================================================")
    
    spark.stop()

if __name__ == "__main__":
    run_full_ingestion()