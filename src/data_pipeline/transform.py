import os
import argparse
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import DoubleType

def run_transformation(spark: SparkSession, year: int = 2025, dict_path: str = None):
    print(f"Iniciando pipeline de transformação e enriquecimento de dados para {year}...")

    part_input_path = f"data/processed/enem_{year}_cleaned_parquet"
    res_input_path = f"data/processed/enem_{year}_resultados_parquet"
    
    enriched_output_path = f"data/processed/enem_{year}_enriched_parquet"
    output_rede_path = f"data/processed/enem_{year}_agg_rede_ensino_parquet"

    if not os.path.exists(part_input_path):
        raise FileNotFoundError(f"Dataset de participantes não encontrado em: {part_input_path}. Execute o ingest.py primeiro.")

    print(f"Lendo dataset de participantes: {part_input_path}...")
    df_part = spark.read.parquet(part_input_path)

    df_res = None
    if os.path.exists(res_input_path):
        print(f"Lendo dataset de resultados (notas): {res_input_path}...")
        df_res = spark.read.parquet(res_input_path)
    else:
        raise FileNotFoundError(f"Dataset de resultados não encontrado em {res_input_path}. As notas são obrigatórias para este gráfico.")

    # Converte notas para Double
    nota_cols = ['NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC']
    for c in nota_cols:
        if c in df_res.columns:
            df_res = df_res.withColumn(c, F.col(c).cast(DoubleType()))

    # MAPEAMENTO DINÂMICO DE CHAVES
    left_key = "NU_INSCRICAO" if "NU_INSCRICAO" in df_part.columns else "NU_SEQUENCIAL"
    right_key = "NU_SEQUENCIAL" if "NU_SEQUENCIAL" in df_res.columns else "NU_INSCRICAO"

    if left_key not in df_part.columns or right_key not in df_res.columns:
        raise ValueError(f"Erro crítico: Não foi possível identificar as chaves de cruzamento compatíveis entre os datasets.")

    print(f"Realizando join utilizando chaves compatíveis -> Participantes ({left_key}) <-> Resultados ({right_key})")
    
    if left_key != right_key:
        df_res = df_res.withColumnRenamed(right_key, left_key)
        join_key = left_key
    else:
        join_key = left_key

    res_cols = [join_key] + [c for c in nota_cols if c in df_res.columns]
    
    df_joined = df_part.join(df_res.select(*res_cols), on=join_key, how="left")
    df_joined = df_joined.repartition(32)

    # Descrições textuais padrão para variáveis categóricas
    if "TP_SEXO" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "TP_SEXO_DESC",
            F.when(F.col("TP_SEXO") == "M", "Masculino")
             .when(F.col("TP_SEXO") == "F", "Feminino")
             .otherwise("Não Informado")
        )

    if "IN_TREINEIRO" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "IN_TREINEIRO_DESC",
            F.when(F.col("IN_TREINEIRO") == 1, "Treineiro")
             .otherwise("Não Treineiro")
        )

    # Identificação dinâmica e segura da coluna de dependência administrativa / tipo de escola
    colunas_upper = [c.upper().strip() for c in df_joined.columns]
    dep_col = None
    tipo_mapeamento = None
    
    potential_cols = ["TP_ESCOLA", "TP_DEPENDENCIA_ADM_ESC", "TP_DEPENDENCIA_ADM"]
    for p in potential_cols:
        if p in colunas_upper:
            dep_col = df_joined.columns[colunas_upper.index(p)]
            tipo_mapeamento = "tp_escola" if p == "TP_ESCOLA" else "tp_dependencia"
            break

    if dep_col:
        print(f"\n[SUCESSO] Coluna de rede/escola identificada: '{dep_col}' (Tipo: {tipo_mapeamento})")
        if tipo_mapeamento == "tp_escola":
            df_joined = df_joined.withColumn(
                "TP_DEPENDENCIA_ADM_ESC_DESC",
                F.when(F.col(dep_col).isin(2, "2", 2.0), "Pública")
                 .when(F.col(dep_col).isin(3, "3", 3.0), "Privada")
                 .otherwise("Não Informado")
            )
        else:
            df_joined = df_joined.withColumn(
                "TP_DEPENDENCIA_ADM_ESC_DESC",
                F.when(F.col(dep_col).isin(1, "1", 1.0), "Federal")
                 .when(F.col(dep_col).isin(2, "2", 2.0), "Estadual")
                 .when(F.col(dep_col).isin(3, "3", 3.0), "Municipal")
                 .when(F.col(dep_col).isin(4, "4", 4.0), "Privada")
                 .otherwise("Não Informado")
            )
    else:
        print(f"\n[ALERTA CRÍTICO] Nenhuma coluna de escola encontrada nas colunas: {df_joined.columns}")
        df_joined = df_joined.withColumn("TP_DEPENDENCIA_ADM_ESC_DESC", F.lit("Não Informado"))

    # === FASE 5.2: ENRIQUECIMENTO SOCIOECONÔMICO AVANÇADO (Q006 x Q007 x Escola) ===
    print("Aplicando mapeamento avançado para Renda (Q006) e Trabalho/Autonomia (Q007)...")
    
    if "Q006" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "Q006_DESC",
            F.when(F.col("Q006") == "A", "Nenhuma renda")
             .when(F.col("Q006") == "B", "Até R$ 1.518,00")
             .when(F.col("Q006") == "C", "De R$ 1.518,01 até R$ 2.277,00")
             .when(F.col("Q006") == "D", "De R$ 2.277,01 até R$ 3.036,00")
             .when(F.col("Q006") == "E", "De R$ 3.036,01 até R$ 3.795,00")
             .when(F.col("Q006") == "F", "De R$ 3.795,01 até R$ 4.554,00")
             .when(F.col("Q006") == "G", "De R$ 4.554,01 até R$ 6.072,00")
             .when(F.col("Q006") == "H", "De R$ 6.072,01 até R$ 7.590,00")
             .when(F.col("Q006") == "I", "De R$ 7.590,01 até R$ 9.108,00")
             .when(F.col("Q006") == "J", "De R$ 9.108,01 até R$ 10.626,00")
             .when(F.col("Q006") == "K", "De R$ 10.626,01 até R$ 12.144,00")
             .when(F.col("Q006") == "L", "De R$ 12.144,01 até R$ 13.662,00")
             .when(F.col("Q006") == "M", "De R$ 13.662,01 até R$ 15.180,00")
             .when(F.col("Q006") == "N", "De R$ 15.180,01 até R$ 18.216,00")
             .when(F.col("Q006") == "O", "De R$ 18.216,01 até R$ 22.770,00")
             .when(F.col("Q006") == "P", "De R$ 22.770,01 até R$ 30.360,00")
             .when(F.col("Q006") == "Q", "Acima de R$ 30.360,00")
             .otherwise("Não Informado")
        )
    else:
        df_joined = df_joined.withColumn("Q006_DESC", F.lit("Não Informado"))

    if "Q007" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "Q007_DESC",
            F.when(F.col("Q007") == "A", "Não")
             .when(F.col("Q007") == "B", "Sim, um ou dois dias por semana")
             .when(F.col("Q007") == "C", "Sim, três ou quatro dias por semana")
             .when(F.col("Q007") == "D", "Sim, pelo menos cinco dias por semana")
             .otherwise("Não Informado")
        )
    else:
        df_joined = df_joined.withColumn("Q007_DESC", F.lit("Não Informado"))

    print(f"Salvando dataset enriquecido em: {enriched_output_path}...")
    df_joined.write.mode("overwrite").parquet(enriched_output_path)

    # Agregação por Rede de Ensino
    print("Gerando tabelas agregadas por rede de ensino...")
    agg_rede = df_joined.groupBy("TP_DEPENDENCIA_ADM_ESC_DESC").agg(
        F.count("*").alias("total_candidatos"),
        F.avg("NU_NOTA_MT").alias("media_matematica"),
        F.avg("NU_NOTA_REDACAO").alias("media_redacao")
    )
    agg_rede.write.mode("overwrite").parquet(output_rede_path)
    print(f"Salvando agregação por Rede de Ensino em: {output_rede_path}...")

    # Agregação Avançada da Fase 5.2
    output_socio_escola_path = f"data/processed/enem_{year}_agg_socio_escola_parquet"
    print("Gerando agregação avançada (Fase 5.2): Renda (Q006_DESC) x Autonomia (Q007_DESC) x Escola...")
    agg_socio_escola = df_joined.groupBy(
        "TP_DEPENDENCIA_ADM_ESC_DESC", 
        "Q006_DESC", 
        "Q007_DESC"
    ).agg(
        F.count("*").alias("total_candidatos"),
        F.avg("NU_NOTA_MT").alias("media_matematica"),
        F.avg("NU_NOTA_REDACAO").alias("media_redacao"),
        F.avg("NU_NOTA_CN").alias("media_cn"),
        F.avg("NU_NOTA_CH").alias("media_ch"),
        F.avg("NU_NOTA_LC").alias("media_lc")
    )
    agg_socio_escola.write.mode("overwrite").parquet(output_socio_escola_path)
    print(f"Salvando agregação avançada socioeconômica em: {output_socio_escola_path}...")

    print("Pipeline de transformação executado com sucesso!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform script for ENEM 2025 pipeline")
    parser.add_argument("--dict_path", type=str, default="enem_2025_dict.json", help="Path to dictionary JSON")
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("ENEM_2025_Transform") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.sql.shuffle.partitions", "32") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.memory.fraction", "0.6") \
        .config("spark.memory.storageFraction", "0.3") \
        .config("spark.local.dir", "data/tmp_spill") \
        .getOrCreate()

    try:
        for target_year in [2024, 2025]:
            run_transformation(spark, year=target_year, dict_path=args.dict_path)
    finally:
        spark.stop()