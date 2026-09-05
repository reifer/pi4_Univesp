import os
import sys
import subprocess
from pyspark.sql import SparkSession
from downloader import ingest_legacy_years, unify_recent_years

def run_ingestion_phase():
    """Executa exclusivamente a fase de ingestão e limpeza dos dados."""
    print("==================================================")
    print(" 📥 INICIANDO ETAPA DE INGESTÃO (2021-2025) ")
    print("==================================================")
    
    spark_tmp_dir = os.path.abspath("data/.spark_tmp")
    os.makedirs(spark_tmp_dir, exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    spark = SparkSession.builder \
        .appName("EnemIngestionPipeline") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.local.dir", spark_tmp_dir) \
        .config("spark.sql.shuffle.partitions", "32") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    try:
        # Processa anos legados (2021 a 2023)
        for ano in [2021, 2022, 2023]:
            ingest_legacy_years(ano, spark)
            
        # Processa anos recentes (2024 e 2025)
        for ano in [2024, 2025]:
            unify_recent_years(ano, spark)
    finally:
        spark.stop()
        print("🧹 Sessão Spark de ingestão encerrada e memória liberada.")

def main():
    print("==================================================")
    print(" 🚀 ORQUESTRADOR MESTRE: INICIANDO PIPELINE ")
    print("==================================================")

    try:
        # 1. Executa a Ingestão própria
        run_ingestion_phase()
        print("✅ Ingestão finalizada com sucesso [OK].\n")

        # 2. Delega para o Transform e aguarda o retorno
        print("🔄 Acionando pipeline de Transformação...")
        subprocess.run([sys.executable, "src/data_pipeline/transform.py"], check=True)
        print("✅ Transformação finalizada com sucesso [OK].\n")

        # 3. Delega para o Report/ML e aguarda o retorno
        print("🤖 Acionando geração de Relatório e Machine Learning...")
        subprocess.run([sys.executable, "src/data_pipeline/report_or_ml.py"], check=True)
        print("✅ Relatório de ML gerado com sucesso [OK].\n")

        print("==================================================")
        print("🎉 PIPELINE COMPLETO EXECUTADO COM STATUS: [OK]")
        print("==================================================")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO CRÍTICO NO PIPELINE: O subprocesso falhou com código {e.returncode} [NOK].")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO NO ORQUESTRADOR: {e} [NOK].")
        sys.exit(1)

if __name__ == "__main__":
    main()