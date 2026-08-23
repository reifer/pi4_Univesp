"""
Transformation and Enrichment Pipeline (PySpark) for ENEM 2025 data.

Joins PARTICIPANTES and RESULTADOS datasets, enriches categorical columns
using human-readable descriptions from data/dictionary/enem_2025_dict.json,
and generates aggregated statistical views for states and income tiers.
"""

import json

import os
from itertools import chain
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    avg, col, count, create_map, lit, coalesce,
    monotonically_increasing_id, round as spark_round, when
)


def enrich_dataframe_with_dictionary(
    df: DataFrame,
    dict_path: str = "data/dictionary/enem_2025_dict.json"
) -> DataFrame:
    """
    Enriches a PySpark DataFrame with human-readable label columns (_DESC)
    based on the JSON dictionary mapping.

    Args:
        df: Input PySpark DataFrame.
        dict_path: Path to the JSON dictionary file.

    Returns:
        DataFrame: Enriched PySpark DataFrame with new descriptive columns.
    """
    if not os.path.exists(dict_path):
        print(f"Warning: Dictionary JSON not found at '{dict_path}'. Skipping dictionary enrichment.")
        return df

    try:
        with open(dict_path, "r", encoding="utf-8") as f:
            dictionary = json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load dictionary JSON from '{dict_path}'. Error: {e}")
        return df

    print(f"Loaded dictionary from '{dict_path}' with {len(dictionary)} variables.")
    enriched_cols = []

    for col_name in df.columns:
        if col_name in dictionary and dictionary[col_name]:
            mapping = dictionary[col_name]
            try:
                # Flatten dictionary key-value items into alternating literal expressions for create_map
                kv_literals = [lit(str(x)) for x in chain(*mapping.items())]
                map_expr = create_map(kv_literals)
                
                desc_col_name = f"{col_name}_DESC"
                # Map column value to readable label; fallback to original string if unmapped
                df = df.withColumn(desc_col_name, coalesce(map_expr[col(col_name)], col(col_name)))
                enriched_cols.append(desc_col_name)
            except Exception as ex:
                print(f"Warning: Could not enrich column '{col_name}'. Error: {ex}")

    print(f"Successfully enriched {len(enriched_cols)} columns with readable descriptions.")
    if enriched_cols:
        print(f"Enriched columns created: {', '.join(sorted(enriched_cols[:10]))}...")

    return df


def transform_enem_data():
    """
    Realiza o Join entre PARTICIPANTES e RESULTADOS (Notas) por NU_INSCRICAO/row_id,
    aplica o enriquecimento com o dicionário de dados (enem_2025_dict.json),
    gera o dataset enriquecido (enem_2025_enriched_parquet) e as visões agregadas.
    """
    spark = SparkSession.builder \
        .appName("EnemDataTransformation") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
        .getOrCreate()

    part_input_path = "data/processed/enem_2025_cleaned_parquet"
    res_input_path = "data/processed/enem_2025_resultados_parquet"
    
    enriched_output_path = "data/processed/enem_2025_enriched_parquet"
    output_uf_path = "data/processed/enem_2025_agg_uf_parquet"
    output_renda_path = "data/processed/enem_2025_agg_renda_uf_parquet"
    output_notas_uf_path = "data/processed/enem_2025_agg_notas_uf_parquet"
    output_notas_renda_path = "data/processed/enem_2025_agg_notas_renda_parquet"

    print(f"Lendo dataset de participantes: {part_input_path}...")
    df_part = spark.read.parquet(part_input_path)

    print(f"Lendo dataset de resultados (notas): {res_input_path}...")
    df_res = spark.read.parquet(res_input_path)

    # 1. Alinhamento e Join entre PARTICIPANTES e RESULTADOS
    print("Realizando Join entre PARTICIPANTES e RESULTADOS por chave de inscrição/sequencial...")
    score_cols = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
    res_select_cols = [c for c in score_cols if c in df_res.columns]

    if 'NU_INSCRICAO' in df_res.columns:
        df_res_sub = df_res.select(['NU_INSCRICAO'] + res_select_cols)
        df_joined = df_part.join(df_res_sub, on="NU_INSCRICAO", how="inner")
    else:
        df_part_indexed = df_part.withColumn("row_id", monotonically_increasing_id())
        df_res_indexed = df_res.select(res_select_cols).withColumn("row_id", monotonically_increasing_id())
        df_joined = df_part_indexed.join(df_res_indexed, on="row_id", how="inner").drop("row_id")

    # Conversão das colunas de notas para tipo Numérico (Double)
    for score_col in score_cols:
        if score_col in df_joined.columns:
            df_joined = df_joined.withColumn(score_col, col(score_col).cast("double"))

    total_records = df_joined.count()
    print(f"Dataset unificado (Join) concluído com sucesso. Total de registros: {total_records}")

    # 2. Enriquecimento dos Dados usando o Dicionário JSON
    print("Aplicando enriquecimento de dicionário com nomes descritivos (_DESC)...")
    df_joined = enrich_dataframe_with_dictionary(df_joined)

    # Salva o dataset enriquecido consolidado em Parquet
    print(f"Salvando dataset enriquecido em: {enriched_output_path}...")
    df_joined.write.mode("overwrite").parquet(enriched_output_path)

    # 3. Agregação Geral Demográfica por Estado (UF)
    print("Calculando agregações estatísticas por Estado (UF)...")
    agg_uf = df_joined.groupBy("SG_UF_PROVA").agg(
        count("*").alias("total_inscritos"),
        count(when(col("IN_TREINEIRO") == "1", 1)).alias("total_treineiros"),
        count(when(col("TP_SEXO") == "F", 1)).alias("total_feminino"),
        count(when(col("TP_SEXO") == "M", 1)).alias("total_masculino")
    ).withColumn(
        "pct_treineiros",
        spark_round((col("total_treineiros") / col("total_inscritos")) * 100, 2)
    ).orderBy(col("total_inscritos").desc())

    agg_uf.write.mode("overwrite").parquet(output_uf_path)

    # 4. Agregação Socioeconômica por UF e Faixa de Renda (Q006)
    print("Calculando agregações por Faixa de Renda (Q006) e Estado...")
    agg_renda_uf = df_joined.groupBy("SG_UF_PROVA", "Q006").agg(
        count("*").alias("total_inscritos")
    ).orderBy("SG_UF_PROVA", "Q006")

    agg_renda_uf.write.mode("overwrite").parquet(output_renda_path)

    # 5. Agregação de Médias de Notas por Estado e Status de Treineiro
    print("Calculando médias de notas por Estado e Status de Treineiro...")
    agg_notas_uf = df_joined.groupBy("SG_UF_PROVA", "IN_TREINEIRO").agg(
        count("*").alias("total_candidatos"),
        spark_round(avg("NU_NOTA_CN"), 2).alias("media_cn"),
        spark_round(avg("NU_NOTA_CH"), 2).alias("media_ch"),
        spark_round(avg("NU_NOTA_LC"), 2).alias("media_lc"),
        spark_round(avg("NU_NOTA_MT"), 2).alias("media_mt"),
        spark_round(avg("NU_NOTA_REDACAO"), 2).alias("media_redacao")
    ).orderBy("SG_UF_PROVA", "IN_TREINEIRO")

    print(f"Salvando médias de notas por UF em: {output_notas_uf_path}...")
    agg_notas_uf.write.mode("overwrite").parquet(output_notas_uf_path)

    # 6. Agregação de Médias de Notas por Faixa de Renda (Q006) e Status de Treineiro
    print("Calculando médias de notas por Faixa de Renda (Q006)...")
    agg_notas_renda = df_joined.groupBy("Q006", "IN_TREINEIRO").agg(
        count("*").alias("total_candidatos"),
        spark_round(avg("NU_NOTA_CN"), 2).alias("media_cn"),
        spark_round(avg("NU_NOTA_CH"), 2).alias("media_ch"),
        spark_round(avg("NU_NOTA_LC"), 2).alias("media_lc"),
        spark_round(avg("NU_NOTA_MT"), 2).alias("media_mt"),
        spark_round(avg("NU_NOTA_REDACAO"), 2).alias("media_redacao")
    ).orderBy("Q006", "IN_TREINEIRO")

    print(f"Salvando médias de notas por Renda em: {output_notas_renda_path}...")
    agg_notas_renda.write.mode("overwrite").parquet(output_notas_renda_path)

    print("Pipeline de transformação, enriquecimento e agregados concluído com sucesso!")


if __name__ == "__main__":
    transform_enem_data()
