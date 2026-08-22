from pyspark.sql import SparkSession
from pyspark.sql.functions import col, coalesce, lit, trim, when

def clean_enem_data():
    """
    Carrega o dataset em Parquet do ENEM, aplica a limpeza de dados
    (tratamento de valores nulos e trim de strings) e salva o dataset limpo.
    """
    # Inicializa a sessão Spark
    spark = SparkSession.builder \
        .appName("EnemDataCleaning") \
        .getOrCreate()

    input_path = "data/processed/enem_2025_parquet"
    output_path = "data/processed/enem_2025_cleaned_parquet"

    print(f"Lendo dataset Parquet de: {input_path}...")
    df = spark.read.parquet(input_path)

    total_initial_count = df.count()
    print(f"Total de registros carregados: {total_initial_count}")

    # 1. Aplicar trim em todas as colunas do tipo string para eliminar espaços em branco
    string_cols = [f.name for f in df.schema.fields if f.dataType.typeName() == "string"]
    for col_name in string_cols:
        df = df.withColumn(col_name, trim(col(col_name)))

    # 2. Tratamento de valores nulos/vazios na coluna TP_ENSINO
    # No ENEM, a ausência de TP_ENSINO indica participantes que já concluíram o ensino médio ou não informaram.
    # Preenchemos com "0" (Não informado).
    print("Tratando valores nulos na coluna TP_ENSINO...")
    df = df.withColumn(
        "TP_ENSINO",
        coalesce(
            when((col("TP_ENSINO").isNull()) | (col("TP_ENSINO") == ""), lit("0"))
            .otherwise(col("TP_ENSINO")),
            lit("0")
        )
    )

    # 3. Tratamento de nulos nas questões socioeconômicas (Q001 até Q023)
    question_cols = [c for c in df.columns if c.startswith("Q0")]
    for q_col in question_cols:
        df = df.withColumn(
            q_col,
            coalesce(
                when((col(q_col).isNull()) | (col(q_col) == ""), lit("N/A"))
                .otherwise(col(q_col)),
                lit("N/A")
            )
        )

    # Salva em formato Parquet para uso nas próximas etapas do pipeline
    print(f"Salvando dataset limpo em Parquet no caminho: {output_path}...")
    df.write.mode("overwrite").parquet(output_path)

    print("Pipeline de limpeza concluído com sucesso!")

if __name__ == "__main__":
    clean_enem_data()
