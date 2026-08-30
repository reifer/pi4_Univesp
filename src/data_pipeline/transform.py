import os
import argparse
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.sql.window import Window

def run_transformation(spark: SparkSession, year: int = 2025, dict_path: str | None = None):
    print(f"\n=======================================================")
    print(f" Iniciando pipeline de transformação ENEM {year} (Fase 5.1)")
    print(f"=======================================================")

    enriched_output_path = f"data/processed/enem_{year}_enriched_parquet"
    output_rede_path = f"data/processed/enem_{year}_agg_rede_ensino_parquet"
    output_socio_escola_path = f"data/processed/enem_{year}_agg_socio_escola_parquet"
    output_notas_uf_path = f"data/processed/enem_{year}_agg_notas_uf_parquet"
    output_notas_renda_path = f"data/processed/enem_{year}_agg_notas_renda_parquet"

    # Leitura unificada padrão para toda a série histórica (2021-2025)
    input_path = f"data/processed/enem_{year}_cleaned_parquet"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset limpo não encontrado em: {input_path}. Execute o ingest.py / ingest_21_23.py primeiro.")
    
    print(f"Lendo dataset unificado de {year}: {input_path}...")
    df_joined = spark.read.parquet(input_path)

    # Reparticionamento para otimizar o processamento no Spark
    df_joined = df_joined.repartition(32)

    # Blindagem Dinâmica: Assegura que todas as colunas de notas existam no DataFrame (se faltarem, cria como nulas)
    nota_cols = ['NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC']
    for c in nota_cols:
        if c in df_joined.columns:
            df_joined = df_joined.withColumn(c, F.col(c).cast(DoubleType()))
        else:
            df_joined = df_joined.withColumn(c, F.lit(None).cast(DoubleType()))

    # Assegura coluna de Ano (NU_ANO)
    df_joined = df_joined.withColumn("NU_ANO", F.lit(year))

    # Mapeamento Categórico Descritivo das Variáveis Sociodemográficas
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
            F.when(F.col("IN_TREINEIRO").isin(1, "1", 1.0), "Treineiro")
             .otherwise("Não Treineiro")
        )

    if "TP_COR_RACA" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "TP_COR_RACA_DESC",
            F.when(F.col("TP_COR_RACA").isin(0, "0"), "Não declarado")
             .when(F.col("TP_COR_RACA").isin(1, "1"), "Branca")
             .when(F.col("TP_COR_RACA").isin(2, "2"), "Preta")
             .when(F.col("TP_COR_RACA").isin(3, "3"), "Parda")
             .when(F.col("TP_COR_RACA").isin(4, "4"), "Amarela")
             .when(F.col("TP_COR_RACA").isin(5, "5"), "Indígena")
             .otherwise("Não Informado")
        )

    if "TP_ST_CONCLUSAO" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "TP_ST_CONCLUSAO_DESC",
            F.when(F.col("TP_ST_CONCLUSAO").isin(1, "1"), "Já concluí o Ensino Médio")
             .when(F.col("TP_ST_CONCLUSAO").isin(2, "2"), "Estou cursando e concluirei no ano")
             .when(F.col("TP_ST_CONCLUSAO").isin(3, "3"), "Estou cursando e concluirei após o ano")
             .when(F.col("TP_ST_CONCLUSAO").isin(4, "4"), "Não concluí e não estou cursando")
             .otherwise("Não Informado")
        )

    # Mapeamento Rigoroso da Fase 5.1: Granularidade por TP_DEPENDENCIA_ADM_ESC
    print("Mapeando TP_DEPENDENCIA_ADM_ESC conforme o Dicionário Oficial do ENEM...")
    if "TP_DEPENDENCIA_ADM_ESC" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "TP_DEPENDENCIA_ADM_ESC_DESC",
            F.when(F.col("TP_DEPENDENCIA_ADM_ESC").isin(1, "1", 1.0), "Federal")
             .when(F.col("TP_DEPENDENCIA_ADM_ESC").isin(2, "2", 2.0), "Estadual")
             .when(F.col("TP_DEPENDENCIA_ADM_ESC").isin(3, "3", 3.0), "Municipal")
             .when(F.col("TP_DEPENDENCIA_ADM_ESC").isin(4, "4", 4.0), "Privada")
             .otherwise("Não Informado")
        )
    elif "TP_ESCOLA" in df_joined.columns:
        print("[Aviso] Fallback para TP_ESCOLA (Pública vs Privada)...")
        df_joined = df_joined.withColumn(
            "TP_DEPENDENCIA_ADM_ESC_DESC",
            F.when(F.col("TP_ESCOLA").isin(2, "2", 2.0), "Pública")
             .when(F.col("TP_ESCOLA").isin(3, "3", 3.0), "Privada")
             .otherwise("Não Informado")
        )
    else:
        df_joined = df_joined.withColumn("TP_DEPENDENCIA_ADM_ESC_DESC", F.lit("Não Informado"))

    # Adiciona classificação macro de Rede (Pública vs Privada)
    df_joined = df_joined.withColumn(
        "TP_REDE_MACRO_DESC",
        F.when(F.col("TP_DEPENDENCIA_ADM_ESC_DESC").isin("Federal", "Estadual", "Municipal"), "Pública")
         .when(F.col("TP_DEPENDENCIA_ADM_ESC_DESC") == "Privada", "Privada")
         .otherwise("Não Informado")
    )

    # Mapeamento Socioeconômico Avançado (Q006 e Q007)
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
             .when(F.col("Q007") == "B", "Sim, 1 ou 2 dias/semana")
             .when(F.col("Q007") == "C", "Sim, 3 ou 4 dias/semana")
             .when(F.col("Q007") == "D", "Sim, 5+ dias/semana")
             .otherwise("Não Informado")
        )
    else:
        df_joined = df_joined.withColumn("Q007_DESC", F.lit("Não Informado"))

    # Gravação do Dataset Enriquecido
    print(f"Salvando dataset enriquecido em: {enriched_output_path}...")
    df_joined.write.mode("overwrite").parquet(enriched_output_path)

    # Agregação Estatística da Fase 5.1: Volumetria e Desempenho por Ano, UF e Rede de Ensino
    print(f"Gerando agregação da Fase 5.1 (NU_ANO x SG_UF_PROVA x TP_DEPENDENCIA_ADM_ESC_DESC)...")
    uf_col = "SG_UF_PROVA" if "SG_UF_PROVA" in df_joined.columns else "CO_UF_PROVA"

    agg_rede = df_joined.groupBy(
        "NU_ANO",
        uf_col,
        "TP_DEPENDENCIA_ADM_ESC_DESC"
    ).agg(
        F.count("*").alias("total_candidatos"),
        F.round(F.avg("NU_NOTA_CN"), 2).alias("media_cn"),
        F.round(F.avg("NU_NOTA_CH"), 2).alias("media_ch"),
        F.round(F.avg("NU_NOTA_LC"), 2).alias("media_lc"),
        F.round(F.avg("NU_NOTA_MT"), 2).alias("media_mt"),
        F.round(F.avg("NU_NOTA_REDACAO"), 2).alias("media_redacao")
    )

    # Cálculo da Média Geral das 5 áreas
    agg_rede = agg_rede.withColumn(
        "media_geral",
        F.round(
            (F.coalesce(F.col("media_cn"), F.lit(0.0)) +
             F.coalesce(F.col("media_ch"), F.lit(0.0)) +
             F.coalesce(F.col("media_lc"), F.lit(0.0)) +
             F.coalesce(F.col("media_mt"), F.lit(0.0)) +
             F.coalesce(F.col("media_redacao"), F.lit(0.0))) / 5.0, 2
        )
    )

    # Cálculo do percentual de alunos na UF/Ano
    w_uf_ano = Window.partitionBy("NU_ANO", uf_col)
    agg_rede = agg_rede.withColumn(
        "total_uf_ano", F.sum("total_candidatos").over(w_uf_ano)
    ).withColumn(
        "percentual_alunos",
        F.round((F.col("total_candidatos") / F.col("total_uf_ano")) * 100.0, 2)
    ).drop("total_uf_ano")

    print(f"Salvando agregação de Redes de Ensino em: {output_rede_path}...")
    agg_rede.write.mode("overwrite").parquet(output_rede_path)

    # Agregação Avançada da Fase 5.2 (Socioeconômico x Escola)
    print("Gerando agregação avançada (Fase 5.2): Renda (Q006_DESC) x Trabalho (Q007_DESC) x Rede...")
    agg_socio_escola = df_joined.groupBy(
        "NU_ANO",
        "TP_DEPENDENCIA_ADM_ESC_DESC", 
        "Q006_DESC", 
        "Q007_DESC"
    ).agg(
        F.count("*").alias("total_candidatos"),
        F.round(F.avg("NU_NOTA_CN"), 2).alias("media_cn"),
        F.round(F.avg("NU_NOTA_CH"), 2).alias("media_ch"),
        F.round(F.avg("NU_NOTA_LC"), 2).alias("media_lc"),
        F.round(F.avg("NU_NOTA_MT"), 2).alias("media_matematica"),
        F.round(F.avg("NU_NOTA_REDACAO"), 2).alias("media_redacao")
    )
    agg_socio_escola.write.mode("overwrite").parquet(output_socio_escola_path)

    # Agregações para Painéis Gerais (Notas por UF e Notas por Renda)
    print("Atualizando agregações de apoio (Notas por UF e Notas por Renda)...")
    if uf_col in df_joined.columns and "IN_TREINEIRO" in df_joined.columns:
        agg_notas_uf = df_joined.groupBy("NU_ANO", uf_col, "IN_TREINEIRO").agg(
            F.count("*").alias("total_candidatos"),
            F.round(F.avg("NU_NOTA_CN"), 2).alias("media_cn"),
            F.round(F.avg("NU_NOTA_CH"), 2).alias("media_ch"),
            F.round(F.avg("NU_NOTA_LC"), 2).alias("media_lc"),
            F.round(F.avg("NU_NOTA_MT"), 2).alias("media_mt"),
            F.round(F.avg("NU_NOTA_REDACAO"), 2).alias("media_redacao")
        )
        agg_notas_uf.write.mode("overwrite").parquet(output_notas_uf_path)

    if "Q006" in df_joined.columns and "IN_TREINEIRO" in df_joined.columns:
        agg_notas_renda = df_joined.groupBy("NU_ANO", "Q006", "IN_TREINEIRO").agg(
            F.count("*").alias("total_candidatos"),
            F.round(F.avg("NU_NOTA_CN"), 2).alias("media_cn"),
            F.round(F.avg("NU_NOTA_CH"), 2).alias("media_ch"),
            F.round(F.avg("NU_NOTA_LC"), 2).alias("media_lc"),
            F.round(F.avg("NU_NOTA_MT"), 2).alias("media_mt"),
            F.round(F.avg("NU_NOTA_REDACAO"), 2).alias("media_redacao")
        )
        agg_notas_renda.write.mode("overwrite").parquet(output_notas_renda_path)

    print(f"Pipeline de transformação para ENEM {year} concluído com sucesso!\n")

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
            run_transformation(spark, year=y, dict_path=args.dict_path)
    finally:
        spark.stop()