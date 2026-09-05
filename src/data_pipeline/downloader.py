import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window

def ingest_legacy_years(year: int, spark: SparkSession):
    print(f"\n📂 [Legado] Processando microdados do ENEM {year} (Arquivo Único)...")
    
    base_dirs = [
        f"data/raw/microdados_enem_{year}/DADOS",
        f"data/raw/enem_{year}/DADOS",
        f"data/raw",
        "."
    ]
    
    target_file = f"MICRODADOS_ENEM_{year}.csv"
    microdados_csv = None
    
    for d in base_dirs:
        path = os.path.join(d, target_file)
        if os.path.exists(path):
            microdados_csv = path
            break
            
    if not microdados_csv:
        print(f"⚠️ Aviso: Arquivo {target_file} não encontrado para o ano {year}.")
        return

    print(f"📥 Lendo {microdados_csv}...")
    df_microdados = spark.read.csv(
        microdados_csv, 
        header=True, 
        sep=";", 
        encoding="ISO-8859-1", 
        inferSchema=True
    )
    
    output_parquet = f"data/processed/enem_{year}_cleaned_parquet"
    print(f"💾 Salvando base padronizada do ano {year} em '{output_parquet}'...")
    
    df_microdados.write.mode("overwrite").parquet(output_parquet)
    print(f"✅ ENEM {year} processado com sucesso!")


def add_consecutive_index(df, index_col="row_id"):
    """
    Atribui um índice sequencial consecutivo e contíguo (0 a N-1) a cada linha do DataFrame,
    independente da quantidade ou tamanho das partições geradas pelo Spark, sem causar shuffle global.
    """
    df_with_parts = df.withColumn("_part_id", F.spark_partition_id()) \
                      .withColumn("_mono_id", F.monotonically_increasing_id())
    
    w = Window.partitionBy("_part_id").orderBy("_mono_id")
    df_indexed = df_with_parts.withColumn("_row_in_part", F.row_number().over(w) - 1)
    
    part_counts = df_with_parts.groupBy("_part_id").count().collect()
    cum_offset = {}
    curr = 0
    for r in sorted(part_counts, key=lambda x: x["_part_id"]):
        cum_offset[r["_part_id"]] = curr
        curr += r["count"]
    
    mapping_expr = F.create_map([F.lit(x) for kv in cum_offset.items() for x in kv])
    
    return df_indexed.withColumn(index_col, F.col("_row_in_part") + mapping_expr[F.col("_part_id")]) \
                     .drop("_part_id", "_mono_id", "_row_in_part")


def unify_recent_years(year: int, spark: SparkSession):
    print(f"\n🚀 [Recente] Unificando dados fragmentados do ENEM {year}...")
    
    participantes_path = f"data/raw/PARTICIPANTES_{year}.csv"
    resultados_path = f"data/raw/RESULTADOS_{year}.csv"
    
    if not os.path.exists(participantes_path) or not os.path.exists(resultados_path):
        print(f"⚠️ Aviso: Arquivos brutos de Participantes ou Resultados de {year} não encontrados em data/raw/.")
        return

    print(f"📂 Lendo particionados de {year} com encoding ISO-8859-1...")
    df_part = spark.read.option("header", "true") \
                        .option("delimiter", ";") \
                        .option("encoding", "ISO-8859-1") \
                        .option("inferSchema", "true") \
                        .csv(participantes_path)
    df_res = spark.read.option("header", "true") \
                       .option("delimiter", ";") \
                       .option("encoding", "ISO-8859-1") \
                       .option("inferSchema", "true") \
                       .csv(resultados_path)
    
    print("🔄 Alinhando bases de Participantes e Resultados via índice sequencial contíguo...")
    df_part_indexed = add_consecutive_index(df_part, "row_id")
    df_res_indexed = add_consecutive_index(df_res, "row_id")
    
    df_unified = df_part_indexed.join(df_res_indexed, on="row_id", how="left")
    
    df_standardized = df_unified.select(
        df_part_indexed["NU_INSCRICAO"],
        F.lit(year).alias("NU_ANO"),
        df_part_indexed["TP_FAIXA_ETARIA"],
        df_part_indexed["TP_SEXO"],
        df_part_indexed["TP_ESTADO_CIVIL"],
        df_part_indexed["TP_COR_RACA"],
        df_part_indexed["TP_NACIONALIDADE"],
        df_part_indexed["TP_ST_CONCLUSAO"],
        df_part_indexed["TP_ANO_CONCLUIU"],
        df_part_indexed["TP_ESCOLA"] if "TP_ESCOLA" in df_part.columns else F.lit(None).alias("TP_ESCOLA"),
        df_part_indexed["TP_ENSINO"],
        df_part_indexed["IN_TREINEIRO"],
        df_res_indexed["CO_MUNICIPIO_ESC"],
        df_res_indexed["NO_MUNICIPIO_ESC"],
        df_res_indexed["CO_UF_ESC"],
        df_res_indexed["SG_UF_ESC"],
        df_res_indexed["TP_DEPENDENCIA_ADM_ESC"],
        df_res_indexed["TP_LOCALIZACAO_ESC"],
        df_res_indexed["TP_SIT_FUNC_ESC"],
        df_part_indexed["CO_MUNICIPIO_PROVA"],
        df_part_indexed["NO_MUNICIPIO_PROVA"],
        df_part_indexed["CO_UF_PROVA"],
        df_part_indexed["SG_UF_PROVA"],
        df_res_indexed["TP_PRESENCA_CN"],
        df_res_indexed["TP_PRESENCA_CH"],
        df_res_indexed["TP_PRESENCA_LC"],
        df_res_indexed["TP_PRESENCA_MT"],
        df_res_indexed["CO_PROVA_CN"],
        df_res_indexed["CO_PROVA_CH"],
        df_res_indexed["CO_PROVA_LC"],
        df_res_indexed["CO_PROVA_MT"],
        df_res_indexed["NU_NOTA_CN"],
        df_res_indexed["NU_NOTA_CH"],
        df_res_indexed["NU_NOTA_LC"],
        df_res_indexed["NU_NOTA_MT"],
        df_res_indexed["TX_RESPOSTAS_CN"],
        df_res_indexed["TX_RESPOSTAS_CH"],
        df_res_indexed["TX_RESPOSTAS_LC"],
        df_res_indexed["TX_RESPOSTAS_MT"],
        df_res_indexed["TP_LINGUA"],
        df_res_indexed["TX_GABARITO_CN"],
        df_res_indexed["TX_GABARITO_CH"],
        df_res_indexed["TX_GABARITO_LC"],
        df_res_indexed["TX_GABARITO_MT"],
        df_res_indexed["TP_STATUS_REDACAO"],
        df_res_indexed["NU_NOTA_COMP1"],
        df_res_indexed["NU_NOTA_COMP2"],
        df_res_indexed["NU_NOTA_COMP3"],
        df_res_indexed["NU_NOTA_COMP4"],
        df_res_indexed["NU_NOTA_COMP5"],
        df_res_indexed["NU_NOTA_REDACAO"],
        *[df_part_indexed[c] for c in sorted(df_part.columns) if c.startswith("Q") and len(c) == 4 and c[1:].isdigit()]
    )
    
    output_path = f"data/processed/enem_{year}_cleaned_parquet"
    print(f"💾 Salvando base unificada padronizada em Parquet: {output_path}")
    
    df_standardized.write.mode("overwrite").parquet(output_path)
    print(f"✅ ENEM {year} unificado e padronizado com sucesso!")