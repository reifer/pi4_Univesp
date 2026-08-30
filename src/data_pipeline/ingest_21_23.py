import os
from pyspark.sql import SparkSession

def ingest_enem_data_by_year(year: int):
    spark = SparkSession.builder \
        .appName(f"EnemIngestion_{year}") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()

    base_dirs = [
        f"data/raw/enem_{year}/DADOS",
        f"data/raw/DADOS",
        f"/home/reifer/Downloads/microdados_enem_{year}/DADOS",
        f"data/raw"
    ]
    
    data_dir = None
    for d in base_dirs:
        if os.path.exists(os.path.join(d, f"PARTICIPANTES_{year}.csv")) or os.path.exists(os.path.join(d, f"MICRODADOS_ENEM_{year}.csv")):
            data_dir = d
            break

    if not data_dir:
        if os.path.exists(f"PARTICIPANTES_{year}.csv") or os.path.exists(f"MICRODADOS_ENEM_{year}.csv"):
            data_dir = "."
        else:
            print(f"Aviso crítico: Pasta de dados para o ano {year} não encontrada.")
            spark.stop()
            return

    # Identifica os arquivos corretos na pasta
    part_file = f"PARTICIPANTES_{year}.csv" if os.path.exists(os.path.join(data_dir, f"PARTICIPANTES_{year}.csv")) else f"MICRODADOS_ENEM_{year}.csv"
    part_csv = os.path.join(data_dir, part_file)
    
    # Possíveis nomes para o arquivo de notas/resultados nos anos recentes
    res_candidates = [f"RESULTADOS_{year}.csv", f"ITENS_PROVA_{year}.csv", f"DADOS_STAT_{year}.csv"]
    res_csv = None
    for rc in res_candidates:
        if os.path.exists(os.path.join(data_dir, rc)):
            res_csv = os.path.join(data_dir, rc)
            break

    output_parquet = f"data/processed/enem_{year}_cleaned_parquet"

    print(f"Iniciando leitura dos microdados do ENEM {year} em '{part_csv}'...")

    if os.path.exists(part_csv):
        df_part = spark.read.csv(part_csv, header=True, sep=";", encoding="ISO-8859-1", inferSchema=False)
        
        id_col_part = "NU_INSCRICAO" if "NU_INSCRICAO" in df_part.columns else "NU_SEQUENCIAL"

        # Se houver um arquivo complementar de notas/resultados na pasta, faz o join
        if res_csv and os.path.exists(res_csv):
            print(f"Lendo arquivo complementar de notas/resultados: {res_csv}")
            df_res = spark.read.csv(res_csv, header=True, sep=";", encoding="ISO-8859-1", inferSchema=False)
            id_col_res = "NU_INSCRICAO" if "NU_INSCRICAO" in df_res.columns else ("NU_SEQUENCIAL" if "NU_SEQUENCIAL" in df_res.columns else None)
            
            if id_col_res:
                if id_col_part != id_col_res:
                    df_res = df_res.withColumnRenamed(id_col_res, id_col_part)
                
                # Seleciona apenas colunas de notas ou escola que não estejam duplicadas
                val_cols = [c for c in df_res.columns if c == id_col_part or "NOTA" in c.upper() or "ESCOLA" in c.upper() or "DEP" in c.upper()]
                df_part = df_part.join(df_res.select(*val_cols).dropDuplicates([id_col_part]), on=id_col_part, how="left")

        print(f"Gravando dataset unificado completo para {year} em '{output_parquet}'...")
        df_part.write.mode("overwrite").parquet(output_parquet)
        print(f"Pipeline de Ingestão para o ano {year} concluído com sucesso!")
    else:
        print(f"Erro: Arquivo {part_csv} não encontrado!")

    spark.stop()

if __name__ == "__main__":
    for target_year in [2024, 2025]:
        ingest_enem_data_by_year(target_year)