import argparse
from pyspark.sql import SparkSession
from parser import process_enrichment_and_aggregations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de Transformação ENEM Plurianual")
    parser.add_argument("--year", type=int, default=None, help="Ano específico para processar (ex: 2025)")
    parser.add_argument("--dict_path", type=str, default="data/dictionary/enem_2025_dict.json", help="Caminho do Dicionário JSON")
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("ENEM_Plurianual_Transform") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.sql.shuffle.partitions", "32") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.memory.fraction", "0.6") \
        .config("spark.memory.storageFraction", "0.3") \
        .config("spark.local.dir", "data/tmp_spill") \
        .getOrCreate()

    target_years = [args.year] if args.year else [2021, 2022, 2023, 2024, 2025]

    try:
        for y in target_years:
            process_enrichment_and_aggregations(spark, year=y, dict_path=args.dict_path)
            
        print("================================================================")
        print("🎉 Pipeline de transformação concluído com sucesso!")
        print("📊 Série histórica consolidada (2021 a 2025) pronta para o painel.")
        print("================================================================")
    finally:
        spark.stop()