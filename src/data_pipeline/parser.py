import os
import json
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import DoubleType
from pyspark.sql.window import Window


UF_BY_CODE = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
    "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
    "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR",
    "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}

SCORE_COLUMNS = {
    "cn": "NU_NOTA_CN",
    "ch": "NU_NOTA_CH",
    "lc": "NU_NOTA_LC",
    "mt": "NU_NOTA_MT",
    "redacao": "NU_NOTA_REDACAO",
}


def _score_aggregation_expressions():
    expressions = []
    for alias, column in SCORE_COLUMNS.items():
        expressions.extend([
            F.sum(column).alias(f"soma_notas_{alias}"),
            F.count(column).alias(f"total_notas_{alias}"),
        ])
    return expressions


def _add_score_means(aggregate):
    for alias in SCORE_COLUMNS:
        aggregate = aggregate.withColumn(
            f"media_{alias}",
            F.when(
                F.col(f"total_notas_{alias}") > 0,
                F.round(
                    F.col(f"soma_notas_{alias}") / F.col(f"total_notas_{alias}"),
                    2,
                ),
            ),
        )
    return aggregate


def process_enrichment_and_aggregations(spark: SparkSession, year: int = 2025, dict_path: str | None = None):
    print(f"\n=======================================================")
    print(f" Iniciando pipeline de transformação ENEM {year}")
    print(f"=======================================================")

    enriched_output_path = f"data/processed/enem_{year}_enriched_parquet"
    output_rede_path = f"data/processed/enem_{year}_agg_rede_ensino_parquet"
    output_socio_escola_path = f"data/processed/enem_{year}_agg_socio_escola_parquet"
    output_notas_uf_path = f"data/processed/enem_{year}_agg_notas_uf_parquet"
    output_notas_renda_path = f"data/processed/enem_{year}_agg_notas_renda_parquet"
    output_demografia_path = f"data/processed/enem_{year}_agg_demografia_parquet"
    output_renda_raca_path = f"data/processed/enem_{year}_agg_renda_raca_parquet"

    input_path = f"data/processed/enem_{year}_cleaned_parquet"
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Dataset limpo não encontrado em: {input_path}. Execute o ingest_all.py primeiro.")
    
    print(f"Lendo dataset unificado de {year}: {input_path}...")
    df_joined = spark.read.parquet(input_path)

    # Reparticionamento para otimizar o processamento no Spark
    df_joined = df_joined.repartition(32)

    # Blindagem Dinâmica de Notas
    nota_cols = ['NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC']
    for c in nota_cols:
        if c in df_joined.columns:
            df_joined = df_joined.withColumn(c, F.col(c).cast(DoubleType()))
        else:
            df_joined = df_joined.withColumn(c, F.lit(None).cast(DoubleType()))

    df_joined = df_joined.withColumn("NU_ANO", F.lit(year))

    uf_code_to_name = F.create_map(
        *[F.lit(value) for code_name in UF_BY_CODE.items() for value in code_name]
    )
    uf_from_code = (
        uf_code_to_name[F.lpad(F.col("CO_UF_PROVA").cast("string"), 2, "0")]
        if "CO_UF_PROVA" in df_joined.columns
        else F.lit(None).cast("string")
    )
    if "SG_UF_PROVA" in df_joined.columns:
        uf_from_name = F.upper(F.trim(F.col("SG_UF_PROVA").cast("string")))
    else:
        uf_from_name = F.lit(None).cast("string")
    df_joined = df_joined.withColumn(
        "SG_UF_PROVA",
        F.coalesce(
            F.when(F.length(uf_from_name) > 0, uf_from_name),
            uf_from_code,
            F.lit("Não Informado"),
        ),
    )

    if "IN_TREINEIRO" in df_joined.columns:
        treineiro = F.col("IN_TREINEIRO").cast("int")
    else:
        treineiro = F.lit(None).cast("int")
    df_joined = df_joined.withColumn(
        "IN_TREINEIRO",
        F.coalesce(treineiro, F.lit(-1)),
    )

    # Mapeamentos Sociodemográficos Descritivos
    if "TP_SEXO" in df_joined.columns:
        df_joined = df_joined.withColumn(
            "TP_SEXO_DESC",
            F.when(F.col("TP_SEXO") == "M", "Masculino")
             .when(F.col("TP_SEXO") == "F", "Feminino")
             .otherwise("Não Informado")
        )

    df_joined = df_joined.withColumn(
        "IN_TREINEIRO_DESC",
        F.when(F.col("IN_TREINEIRO") == 1, "Treineiro")
         .when(F.col("IN_TREINEIRO") == 0, "Não Treineiro")
         .otherwise("Não Informado"),
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

    df_joined = df_joined.withColumn(
        "TP_REDE_MACRO_DESC",
        F.when(F.col("TP_DEPENDENCIA_ADM_ESC_DESC").isin("Federal", "Estadual", "Municipal"), "Pública")
         .when(F.col("TP_DEPENDENCIA_ADM_ESC_DESC") == "Privada", "Privada")
         .otherwise("Não Informado")
    )

    # Carregamento do Dicionário JSON
    dict_file = dict_path if (dict_path and os.path.exists(dict_path) and str(year) in dict_path) else f"data/dictionary/enem_{year}_dict.json"
    if not os.path.exists(dict_file):
        dict_file = "data/dictionary/enem_2025_dict.json"
    
    enem_dict = {}
    if os.path.exists(dict_file):
        try:
            with open(dict_file, "r", encoding="utf-8") as f:
                enem_dict = json.load(f)
            print(f"📖 Dicionário carregado com sucesso: {dict_file}")
        except Exception as ex:
            print(f"⚠️ Aviso ao ler dicionário {dict_file}: {ex}")

    if year in [2024, 2025]:
        col_renda_raw = "Q007"
        col_trabalho_raw = "Q006"
        dict_renda = enem_dict.get("Q007", {})
        dict_trabalho = enem_dict.get("Q006", {})
    else:
        col_renda_raw = "Q006"
        col_trabalho_raw = "Q007"
        dict_renda = enem_dict.get("Q006", {})
        dict_trabalho = enem_dict.get("Q007", {})

    def build_when_map(column_name: str, mapping: dict, default_val: str = "Não Informado"):
        if column_name not in df_joined.columns or not mapping:
            return F.lit(default_val)
        expr = F.col(column_name)
        when_chain = None
        for k, v in mapping.items():
            if when_chain is None:
                when_chain = F.when(expr == k, F.lit(v))
            else:
                when_chain = when_chain.when(expr == k, F.lit(v))
        return when_chain.otherwise(F.lit(default_val)) if when_chain is not None else F.lit(default_val)

    print("Mapeando colunas canônicas de Renda e Trabalho com base no Dicionário Oficial...")
    if col_renda_raw in df_joined.columns:
        df_joined = df_joined.withColumn("RENDA_FAMILIAR_COD", F.col(col_renda_raw))
    else:
        df_joined = df_joined.withColumn("RENDA_FAMILIAR_COD", F.lit("Não Informado"))

    df_joined = df_joined.withColumn("RENDA_FAMILIAR_DESC", build_when_map(col_renda_raw, dict_renda))
    df_joined = df_joined.withColumn("TRABALHO_COND_DESC", build_when_map(col_trabalho_raw, dict_trabalho))

    df_joined = df_joined.withColumn("Q006_DESC", build_when_map("Q006", enem_dict.get("Q006", {})))
    df_joined = df_joined.withColumn("Q007_DESC", build_when_map("Q007", enem_dict.get("Q007", {})))

    # Salvando dataset enriquecido
    print(f"Salvando dataset enriquecido em: {enriched_output_path}...")
    df_joined.write.mode("overwrite").parquet(enriched_output_path)

    base_dimensions = ["NU_ANO", "SG_UF_PROVA", "IN_TREINEIRO", "IN_TREINEIRO_DESC"]
    note_aggregations = [F.count("*").alias("total_candidatos"), *_score_aggregation_expressions()]
    aggregations = {}

    print("Gerando agregação: Rede de Ensino...")
    agg_rede = _add_score_means(df_joined.groupBy(
        *base_dimensions, "TP_DEPENDENCIA_ADM_ESC_DESC"
    ).agg(*note_aggregations))
    agg_rede = agg_rede.withColumn(
        "soma_notas_geral",
        sum(F.coalesce(F.col(f"soma_notas_{name}"), F.lit(0.0)) for name in SCORE_COLUMNS),
    ).withColumn(
        "total_notas_geral",
        sum(F.col(f"total_notas_{name}") for name in SCORE_COLUMNS),
    ).withColumn(
        "media_geral",
        F.when(
            F.col("total_notas_geral") > 0,
            F.round(F.col("soma_notas_geral") / F.col("total_notas_geral"), 2),
        ),
    )
    w_uf_ano_treineiro = Window.partitionBy(*base_dimensions)
    agg_rede = agg_rede.withColumn(
        "percentual_alunos",
        F.round(
            (F.col("total_candidatos") / F.sum("total_candidatos").over(w_uf_ano_treineiro)) * 100.0,
            2,
        ),
    )
    aggregations["agg_rede_ensino"] = (agg_rede, output_rede_path)

    print("Gerando agregação: Notas por UF...")
    agg_notas_uf = _add_score_means(
        df_joined.groupBy(*base_dimensions).agg(*note_aggregations)
    )
    aggregations["agg_notas_uf"] = (agg_notas_uf, output_notas_uf_path)

    print("Gerando agregação: Notas por Renda Canônica...")
    agg_notas_renda = df_joined.groupBy(
        *base_dimensions, "RENDA_FAMILIAR_COD", "RENDA_FAMILIAR_DESC"
    ).agg(*note_aggregations)
    agg_notas_renda = _add_score_means(agg_notas_renda).withColumn(
        "Q006", F.col("RENDA_FAMILIAR_COD")
    ).withColumn("Q006_DESC", F.col("RENDA_FAMILIAR_DESC"))
    aggregations["agg_notas_renda"] = (agg_notas_renda, output_notas_renda_path)

    print("Gerando agregação: Demografia Completa...")
    agg_demografia = df_joined.groupBy(*base_dimensions, "TP_SEXO_DESC").agg(
        F.count("*").alias("total_candidatos")
    )
    aggregations["agg_demografia"] = (agg_demografia, output_demografia_path)

    print("Gerando agregação: Renda Familiar x Raça/Cor...")
    agg_renda_raca = _add_score_means(df_joined.groupBy(
        *base_dimensions, "RENDA_FAMILIAR_DESC", "TP_COR_RACA_DESC"
    ).agg(*note_aggregations))
    aggregations["agg_renda_raca"] = (agg_renda_raca, output_renda_raca_path)

    print("Gerando agregação: Socioeconômico x Escola...")
    agg_socio_escola = df_joined.groupBy(
        *base_dimensions,
        "TP_DEPENDENCIA_ADM_ESC_DESC",
        "RENDA_FAMILIAR_DESC",
        "TRABALHO_COND_DESC",
    ).agg(*note_aggregations)
    agg_socio_escola = _add_score_means(agg_socio_escola).withColumn(
        "Q006_DESC", F.col("RENDA_FAMILIAR_DESC")
    ).withColumn(
        "Q007_DESC", F.col("TRABALHO_COND_DESC")
    ).withColumn(
        "media_matematica", F.col("media_mt")
    ).withColumn(
        "soma_notas_matematica", F.col("soma_notas_mt")
    ).withColumn(
        "total_notas_matematica", F.col("total_notas_mt")
    )
    aggregations["agg_socio_escola"] = (agg_socio_escola, output_socio_escola_path)

    required_dimensions = base_dimensions
    for name, (aggregate, output_path) in aggregations.items():
        null_dimensions = None
        for column in required_dimensions:
            condition = F.col(column).isNull()
            null_dimensions = condition if null_dimensions is None else null_dimensions | condition
        if aggregate.filter(null_dimensions).limit(1).count():
            raise ValueError(f"Dimensões canônicas nulas encontradas em {name} para {year}.")
        aggregate.coalesce(1).write.option("compression", "zstd").mode("overwrite").parquet(output_path)

    source_by_uf = df_joined.groupBy("NU_ANO", "SG_UF_PROVA").count().alias("source")
    aggregate_by_uf = agg_notas_uf.groupBy("NU_ANO", "SG_UF_PROVA").agg(
        F.sum("total_candidatos").alias("total_candidatos")
    ).alias("aggregate")
    uf_mismatches = source_by_uf.join(
        aggregate_by_uf,
        ["NU_ANO", "SG_UF_PROVA"],
        "full",
    ).filter(
        F.coalesce(F.col("count"), F.lit(0)) != F.coalesce(F.col("total_candidatos"), F.lit(0))
    )
    if uf_mismatches.limit(1).count():
        raise ValueError(f"Total de candidatos por UF diverge dos microdados para {year}.")

    print(f"✅ Transformação do ano {year} concluída com sucesso!")