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
        if os.path.exists(os.path.join(d, f"PARTICIPANTES_{year}.csv")):
            data_dir = d
            break

    if not data_dir:
        if os.path.exists(f"PARTICIPANTES_{year}.csv"):
            data_dir = "."
        else:
            print(f"Aviso crítico: Pasta de dados para o ano {year} não encontrada.")
            spark.stop()
            return

    part_csv = os.path.join(data_dir, f"PARTICIPANTES_{year}.csv")
    res_csv = os.path.join(data_dir, f"RESULTADOS_{year}.csv")
    itens_csv = os.path.join(data_dir, f"ITENS_PROVA_{year}.csv")

    participantes_output = f"data/processed/enem_{year}_cleaned_parquet"
    resultados_output = f"data/processed/enem_{year}_resultados_parquet"

    print(f"Iniciando leitura dos arquivos modulares do ENEM {year} em '{data_dir}'...")

    if os.path.exists(part_csv):
        print(f"Lendo participantes: {part_csv}")
        df_part = spark.read.csv(part_csv, header=True, sep=";", encoding="ISO-8859-1", inferSchema=False)
        
        # Identifica a chave primária no DataFrame de participantes
        id_col_part = "NU_INSCRICAO" if "NU_INSCRICAO" in df_part.columns else "NU_SEQUENCIAL"

        if os.path.exists(itens_csv):
            print(f"Lendo itens de prova/escola: {itens_csv}")
            df_itens = spark.read.csv(itens_csv, header=True, sep=";", encoding="ISO-8859-1", inferSchema=False)
            
            # Identifica a chave primária no DataFrame de itens
            id_col_itens = "NU_INSCRICAO" if "NU_INSCRICAO" in df_itens.columns else "NU_SEQUENCIAL"
            
            # Procura por colunas relacionadas a escola, dependência administrativa ou localização
            escola_cols = [c for c in df_itens.columns if any(k in c.upper() for k in ["ESCOLA", "DEP", "LOCALIZACAO"])]
            
            cols_to_bring = [id_col_itens] + escola_cols
            print(f"Colunas de escola identificadas no arquivo de itens para cruzamento: {escola_cols}")
            
            if len(escola_cols) > 0:
                # Se as chaves tiverem nomes diferentes, padroniza temporariamente para o join
                if id_col_part != id_col_itens:
                    df_itens = df_itens.withColumnRenamed(id_col_itens, id_col_part)
                    join_key = id_col_part
                else:
                    join_key = id_col_part

                df_part = df_part.join(df_itens.select(*cols_to_bring), on=join_key, how="left")
            else:
                print("Aviso: Nenhuma coluna contendo 'ESCOLA', 'DEP' ou 'LOCALIZACAO' foi encontrada no arquivo de itens.")

        print(f"Gravando dataset de participantes unificado para {year}...")
        df_part.write.mode("overwrite").parquet(participantes_output)
    else:
        print(f"Erro: Arquivo {part_csv} não encontrado!")

    if os.path.exists(res_csv):
        print(f"Lendo resultados (notas): {res_csv}")
        df_res = spark.read.csv(res_csv, header=True, sep=";", encoding="ISO-8859-1", inferSchema=False)
        df_res.write.mode("overwrite").parquet(resultados_output)

    print(f"Pipeline de Ingestão modular para o ano {year} concluído com sucesso!")
    spark.stop()

if __name__ == "__main__":
    for target_year in [2025]:
        ingest_enem_data_by_year(target_year)