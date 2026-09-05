import json
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, round as spark_round
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

def run_ml_and_generate_report():
    """
    Treina um modelo de Machine Learning (LogisticRegression) para classificar perfil de Treineiro
    e gera um relatório analítico em formato JSON.
    """
    spark = SparkSession.builder \
        .appName("EnemMLAndReport") \
        .getOrCreate()

    input_path = "data/processed/enem_2025_cleaned_parquet"
    output_report_path = "data/processed/enem_2025_ml_insights.json"

    print(f"Lendo dataset limpo de: {input_path}...")
    df = spark.read.parquet(input_path)

    # 1. Preparação da variável alvo (label)
    df = df.withColumn("label", col("IN_TREINEIRO").cast("double"))

    # Seleção de características preditivas (Demográficas e Socioeconômicas)
    feature_cols = ["TP_FAIXA_ETARIA", "TP_SEXO", "TP_COR_RACA", "TP_ST_CONCLUSAO", "Q001", "Q002", "Q006"]

    print("Construindo Pipeline de Machine Learning com PySpark ML...")
    indexers = [
        StringIndexer(inputCol=c, outputCol=f"{c}_indexed", handleInvalid="keep")
        for c in feature_cols
    ]

    indexed_cols = [f"{c}_indexed" for c in feature_cols]
    assembler = VectorAssembler(inputCols=indexed_cols, outputCol="features")

    lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=20)

    stages: list = [*indexers, assembler, lr]
    pipeline = Pipeline(stages=stages)

    # 2. Divisão Treino / Teste (amostragem para treino rápido e eficiente)
    sample_df = df.sample(withReplacement=False, fraction=0.1, seed=42)
    train_df, test_df = sample_df.randomSplit([0.8, 0.2], seed=42)

    print("Treinando o modelo de Regressão Logística...")
    model = pipeline.fit(train_df)

    print("Avaliando o modelo no conjunto de teste...")
    predictions = model.transform(test_df)

    evaluator_roc = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    evaluator_pr = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction", metricName="areaUnderPR")
    evaluator_acc = MulticlassClassificationEvaluator(predictionCol="prediction", metricName="accuracy")
    evaluator_f1 = MulticlassClassificationEvaluator(predictionCol="prediction", metricName="f1")

    roc_auc = round(evaluator_roc.evaluate(predictions), 4)
    pr_auc = round(evaluator_pr.evaluate(predictions), 4)
    accuracy = round(evaluator_acc.evaluate(predictions), 4)
    f1_score = round(evaluator_f1.evaluate(predictions), 4)

    print(f"Métricas do Modelo ML:")
    print(f"  - ROC AUC: {roc_auc}")
    print(f"  - PR AUC: {pr_auc}")
    print(f"  - Acurácia: {accuracy}")
    print(f"  - F1-Score: {f1_score}")

    # 3. Métricas de Negócio & Insights Gerais
    print("Gerando resumo analítico dos dados...")
    total_inscritos = df.count()
    total_treineiros = df.filter(col("IN_TREINEIRO") == "1").count()
    pct_treineiros = round((total_treineiros / total_inscritos) * 100, 2)

    top_uf_rows = df.groupBy("SG_UF_PROVA").agg(
        count("*").alias("total"),
        count(when(col("IN_TREINEIRO") == "1", 1)).alias("treineiros")
    ).withColumn("pct_treineiros", spark_round((col("treineiros") / col("total")) * 100, 2)) \
     .orderBy(col("pct_treineiros").desc()).limit(5).collect()

    top_ufs = [
        {
            "SG_UF_PROVA": row["SG_UF_PROVA"],
            "total": row["total"],
            "treineiros": row["treineiros"],
            "pct_treineiros": float(row["pct_treineiros"])
        }
        for row in top_uf_rows
    ]

    report_data = {
        "projeto": "Análise e Modelagem Preditiva dos Dados do ENEM 2025 (PI4)",
        "resumo_executivo": {
            "total_inscritos": total_inscritos,
            "total_treineiros": total_treineiros,
            "percentual_treineiros": pct_treineiros,
            "top_ufs_por_pct_treineiros": top_ufs
        },
        "modelo_machine_learning": {
            "algoritmo": "LogisticRegression (PySpark ML)",
            "variavel_alvo": "IN_TREINEIRO",
            "features_utilizadas": feature_cols,
            "metricas_avaliacao": {
                "accuracy": accuracy,
                "roc_auc": roc_auc,
                "pr_auc": pr_auc,
                "f1_score": f1_score
            }
        }
    }

    os.makedirs("data/processed", exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)

    print(f"Relatório de Insights e ML salvo em: {output_report_path}")
    print("Passo 4 concluído com sucesso!")

if __name__ == "__main__":
    run_ml_and_generate_report()
