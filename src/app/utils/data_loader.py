import json
import os
import glob
import pandas as pd
import pyarrow.dataset as ds
import streamlit as st

@st.cache_data
def load_data(year="2025"):
    enriched_parquet_path = f"data/processed/enem_{year}_enriched_parquet"
    dict_path = f"data/dictionary/enem_{year}_dict.json"
    if not os.path.exists(dict_path):
        dict_path = "data/dictionary/enem_2025_dict.json"
    
    insights_path = f"data/processed/enem_{year}_ml_insights.json"
    notas_uf_path = f"data/processed/enem_{year}_agg_notas_uf_parquet"
    notas_renda_path = f"data/processed/enem_{year}_agg_notas_renda_parquet"
    rede_path = f"data/processed/enem_{year}_agg_rede_ensino_parquet"
    socio_escola_path = f"data/processed/enem_{year}_agg_socio_escola_parquet"
    demografia_path = f"data/processed/enem_{year}_agg_demografia_parquet"
    renda_raca_path = f"data/processed/enem_{year}_agg_renda_raca_parquet"
    
    enem_dict = {}
    if os.path.exists(dict_path):
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                enem_dict = json.load(f)
        except Exception as ex:
            st.sidebar.warning(f"Erro ao ler dicionário JSON: {ex}")

    def safe_read_parquet(path, columns=None):
        if os.path.exists(path):
            try:
                if columns is not None:
                    return pd.read_parquet(path, columns=columns)
                return pd.read_parquet(path)
            except Exception as e:
                return pd.DataFrame()
        return pd.DataFrame()

    df = pd.DataFrame()
    if os.path.exists(enriched_parquet_path):
        try:
            dataset = ds.dataset(enriched_parquet_path)
            available_cols = dataset.schema.names
            desired_cols = [
                'SG_UF_PROVA', 'IN_TREINEIRO', 'IN_TREINEIRO_DESC',
                'TP_SEXO', 'TP_SEXO_DESC', 'Q006', 'Q006_DESC', 'Q007', 'Q007_DESC',
                'RENDA_FAMILIAR_COD', 'RENDA_FAMILIAR_DESC', 'TRABALHO_COND_DESC', 'TP_COR_RACA_DESC'
            ]
            cols_to_load = [c for c in desired_cols if c in available_cols]
            
            scanner = dataset.scanner(columns=cols_to_load, batch_size=100000)
            for batch in scanner.to_batches():
                df = batch.to_pandas()
                break
            if not df.empty and "IN_TREINEIRO" in df.columns:
                df["IN_TREINEIRO"] = df["IN_TREINEIRO"].astype(str)
        except Exception as ex:
            st.sidebar.warning(f"Aviso ao carregar parquet otimizado: {ex}")
            df = pd.DataFrame()

    df_notas_uf = safe_read_parquet(notas_uf_path)
    df_notas_renda = safe_read_parquet(notas_renda_path)
    df_socio_escola = safe_read_parquet(socio_escola_path)
    df_demografia = safe_read_parquet(demografia_path)
    df_renda_raca = safe_read_parquet(renda_raca_path)

    rede_files = glob.glob("data/processed/enem_*_agg_rede_ensino_parquet")
    df_rede_plurianual_list = []
    for rf in sorted(rede_files):
        df_temp = safe_read_parquet(rf)
        if not df_temp.empty:
            if "NU_ANO" in df_temp.columns:
                df_temp["NU_ANO"] = pd.to_numeric(df_temp["NU_ANO"], errors="coerce").astype("Int64")
            df_rede_plurianual_list.append(df_temp)

    df_rede_plurianual = pd.concat(df_rede_plurianual_list, ignore_index=True) if df_rede_plurianual_list else pd.DataFrame()

    year_int = int(year)
    if not df_rede_plurianual.empty and "NU_ANO" in df_rede_plurianual.columns:
        df_rede = df_rede_plurianual[df_rede_plurianual["NU_ANO"] == year_int].copy()
    else:
        df_rede = safe_read_parquet(rede_path)
        if not df_rede.empty and "NU_ANO" in df_rede.columns:
            df_rede["NU_ANO"] = pd.to_numeric(df_rede["NU_ANO"], errors="coerce").astype("Int64")
            df_rede = df_rede[df_rede["NU_ANO"] == year_int].copy()

    ml_insights = {}
    if os.path.exists(insights_path):
        with open(insights_path, "r", encoding="utf-8") as f:
            ml_insights = json.load(f)
            
    return df, df_notas_uf, df_notas_renda, df_rede, df_rede_plurianual, df_socio_escola, df_demografia, ml_insights, enem_dict, df_renda_raca