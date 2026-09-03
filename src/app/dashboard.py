import json
import os
import glob
import pandas as pd
import pyarrow.dataset as ds
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pages.conclusao_estrategica import render as render_conclusao_estrategica

# Configuração inicial da página (Tema claro profissional & responsivo)
st.set_page_config(
    page_title="ENEM Analytics & AI — Plurianual PI4",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Clean Professional Analytics)
st.markdown("""
<style>
    .stApp, .main, .block-container {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    .main p, .main span, .main label {
        color: #334155;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #1E293B !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    span[data-baseweb="tag"] {
        background-color: #2563EB !important;
        border-radius: 6px !important;
    }
    span[data-baseweb="tag"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .badge-primary {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-block;
    }
    .metric-value-clean {
        font-size: 2.0rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .metric-label-clean {
        font-size: 0.80rem;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-sub-clean {
        font-size: 0.82rem;
        color: #10B981;
        font-weight: 600;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Paleta oficial para Dependência Administrativa da Escola
COLOR_MAP_REDE = {
    "Federal":       "#2563EB",
    "Estadual":      "#10B981",
    "Municipal":     "#F59E0B",
    "Privada":       "#8B5CF6",
    "Pública":       "#0EA5E9",
    "Não Informado": "#94A3B8"
}

try:
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
                    'RENDA_FAMILIAR_COD', 'RENDA_FAMILIAR_DESC', 'TRABALHO_COND_DESC'
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
                
        return df, df_notas_uf, df_notas_renda, df_rede, df_rede_plurianual, df_socio_escola, df_demografia, ml_insights, enem_dict

    # --- PAINEL LATERAL (SIDEBAR) COM EXPANDERS ---
    st.sidebar.image("https://img.icons8.com/isometric-line/100/education.png", width=50)
    st.sidebar.title("🎛️ Painel de Controle")
    
    selected_year = st.sidebar.selectbox("Selecione o Ano do ENEM:", ["2025", "2024", "2023", "2022", "2021"], index=0)
    st.sidebar.divider()

    # NAVEGAÇÃO MOBILE-FIRST (SUBSTITUINDO AS ABAS HORIZONTAIS)
    st.sidebar.markdown("### 🧭 Módulos de Análise")
    menu_opcao = st.sidebar.radio(
        "Selecione a Seção:",
        options=[
            "📊 Panorama Geográfico (UF)",
            "💰 Perfil Socioeconômico & Demográfico",
            "🏫 Redes de Ensino & Plurianual",
            "📈 Desempenho & Notas (TRI)",
            "🤖 Machine Learning & IA",
            "🌎 Geopolítica & Séries Temporais",
            "🎓 Conclusão Estratégica"
        ],
        index=0,
        label_visibility="collapsed"
    )
    st.sidebar.divider()

    df_raw, df_notas_uf, df_notas_renda, df_rede, df_rede_plurianual, df_socio_escola, df_demografia, ml_insights, enem_dict = load_data(selected_year)

    # Header da Aplicação
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding: 15px 0; border-bottom: 1px solid #E2E8F0;">
        <div>
            <span class="badge-primary">Projeto Integrador (PI4 Univesp)</span>
            <h1 style="margin-top: 8px; margin-bottom: 0; font-size: 2.1rem;">🎓 ENEM {selected_year} — Analytics & AI Dashboard</h1>
            <p style="color: #475569; font-size: 1.0rem; margin-top: 4px;">Análise plurianual de desempenho, perfil socioeconômico e granularidade por redes de ensino</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_raw.empty and df_rede.empty:
        st.error(f"Erro: Dados do ENEM {selected_year} não encontrados. Execute o pipeline de transformação primeiro.")
        st.stop()

    treineiro_map = {"Não Treineiro": "0", "Treineiro": "1"}

    if not df_raw.empty and "SG_UF_PROVA" in df_raw.columns:
        all_ufs = sorted(df_raw["SG_UF_PROVA"].dropna().unique())
    elif not df_rede.empty and "SG_UF_PROVA" in df_rede.columns:
        all_ufs = sorted(df_rede["SG_UF_PROVA"].dropna().unique())
    else:
        all_ufs = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

    with st.sidebar.expander("📍 Recorte Geográfico", expanded=False):
        select_all_ufs = st.checkbox("Selecionar Todos os Estados (UF)", value=True)
        if select_all_ufs:
            selected_ufs = all_ufs
        else:
            selected_ufs = st.multiselect("Filtrar por UF:", all_ufs, default=all_ufs[:5] if len(all_ufs) >= 5 else all_ufs)

    with st.sidebar.expander("👤 Perfil do Candidato", expanded=False):
        selected_treineiro_labels = st.multiselect(
            "Tipo de Candidato (IN_TREINEIRO):",
            options=["Não Treineiro", "Treineiro"],
            default=["Não Treineiro", "Treineiro"],
            help="Treineiro = autoavaliação; Não Treineiro = candidatos regulares."
        )

    st.sidebar.divider()
    st.sidebar.markdown(
        "💡 <b>OBSERVAÇÕES:</b><br>"
        "O campo <code>TP_DEPENDENCIA_ADM_ESC</code> segmenta detalhadamente as redes de ensino em: "
        "<b>Federal, Estadual, Municipal e Privada.</b>",
        unsafe_allow_html=True
    )

    if not selected_ufs or not selected_treineiro_labels:
        st.warning("Selecione pelo menos um Estado e um Tipo de Candidato nos filtros laterais.")
        st.stop()

    selected_treineiro_values = [treineiro_map[label] for label in selected_treineiro_labels]

    if not df_raw.empty:
        df_raw["IN_TREINEIRO"] = df_raw["IN_TREINEIRO"].astype(str)
        if "IN_TREINEIRO_DESC" in df_raw.columns:
            filtered_df = df_raw[
                (df_raw["SG_UF_PROVA"].isin(selected_ufs)) &
                (df_raw["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels))
            ]
        else:
            filtered_df = df_raw[
                (df_raw["SG_UF_PROVA"].isin(selected_ufs)) &
                (df_raw["IN_TREINEIRO"].isin(selected_treineiro_values))
            ]
    else:
        filtered_df = pd.DataFrame()

    # Cards KPI Gerais do Topo
    c1, c2, c3, c4 = st.columns(4)
    if not df_notas_uf.empty and "SG_UF_PROVA" in df_notas_uf.columns:
        df_kpi_uf = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)].copy()
        if "IN_TREINEIRO_DESC" in df_kpi_uf.columns:
            df_kpi_filtered = df_kpi_uf[df_kpi_uf["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
            total_inscritos = int(df_kpi_filtered["total_candidatos"].sum())
            total_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO_DESC"] == "Treineiro"]["total_candidatos"].sum())
            total_nao_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO_DESC"] == "Não Treineiro"]["total_candidatos"].sum())
        elif "IN_TREINEIRO" in df_kpi_uf.columns:
            df_kpi_uf["IN_TREINEIRO"] = df_kpi_uf["IN_TREINEIRO"].astype(str)
            df_kpi_filtered = df_kpi_uf[df_kpi_uf["IN_TREINEIRO"].isin(selected_treineiro_values)]
            total_inscritos = int(df_kpi_filtered["total_candidatos"].sum())
            total_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO"] == "1"]["total_candidatos"].sum())
            total_nao_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO"] == "0"]["total_candidatos"].sum())
        else:
            df_kpi_filtered = df_kpi_uf
            total_inscritos = int(df_kpi_uf["total_candidatos"].sum())
            total_treineiros = 0
            total_nao_treineiros = total_inscritos
            
        uf_totals = df_kpi_filtered.groupby("SG_UF_PROVA")["total_candidatos"].sum()
        top_uf = uf_totals.idxmax() if not uf_totals.empty else (selected_ufs[0] if selected_ufs else "SP")
    else:
        total_inscritos = int(df_rede["total_candidatos"].sum()) if not df_rede.empty else len(filtered_df)
        total_treineiros = int(filtered_df[filtered_df["IN_TREINEIRO"] == "1"].shape[0]) if not filtered_df.empty and "IN_TREINEIRO" in filtered_df.columns else 0
        total_nao_treineiros = int(filtered_df[filtered_df["IN_TREINEIRO"] == "0"].shape[0]) if not filtered_df.empty and "IN_TREINEIRO" in filtered_df.columns else total_inscritos
        top_uf = filtered_df["SG_UF_PROVA"].value_counts().idxmax() if not filtered_df.empty and "SG_UF_PROVA" in filtered_df.columns else (selected_ufs[0] if selected_ufs else "SP")

    with c1:
        st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Total de Inscritos</div><div class="metric-value-clean">{total_inscritos:,.0f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Total Treineiros</div><div class="metric-value-clean">{total_treineiros:,.0f}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Total Regulares</div><div class="metric-value-clean">{total_nao_treineiros:,.0f}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Estado Destaque</div><div class="metric-value-clean">{top_uf}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # === RENDERIZAÇÃO CONDICIONAL POR MÓDULO (MOBILE-FIRST) ===

    if menu_opcao == "📊 Panorama Geográfico (UF)":
        col_left, col_right = st.columns([6, 4])
        with col_left:
            st.subheader("Inscritos por Estado (UF)")
            if not df_notas_uf.empty and "SG_UF_PROVA" in df_notas_uf.columns:
                df_uf_agg = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)].copy()
                if "IN_TREINEIRO_DESC" in df_uf_agg.columns:
                    df_uf_agg = df_uf_agg[df_uf_agg["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
                elif "IN_TREINEIRO" in df_uf_agg.columns:
                    df_uf_agg["IN_TREINEIRO"] = df_uf_agg["IN_TREINEIRO"].astype(str)
                    df_uf_agg = df_uf_agg[df_uf_agg["IN_TREINEIRO"].isin(selected_treineiro_values)]
                
                uf_counts = df_uf_agg.groupby("SG_UF_PROVA")["total_candidatos"].sum().reset_index()
                uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
                fig_uf = px.bar(
                    uf_counts.sort_values(by="total_inscritos", ascending=True),
                    x="total_inscritos", y="SG_UF_PROVA", orientation="h",
                    text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues"
                )
                fig_uf.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450, coloraxis_showscale=False)
                st.plotly_chart(fig_uf, width="stretch")
            elif not filtered_df.empty:
                uf_counts = filtered_df["SG_UF_PROVA"].value_counts().reset_index()
                uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
                fig_uf = px.bar(
                    uf_counts.sort_values(by="total_inscritos", ascending=True),
                    x="total_inscritos", y="SG_UF_PROVA", orientation="h",
                    text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues"
                )
                fig_uf.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450, coloraxis_showscale=False)
                st.plotly_chart(fig_uf, width="stretch")
            else:
                st.info("Dados detalhados por UF não carregados.")
        with col_right:
            st.subheader("Distribuição por Sexo")
            if not df_demografia.empty and "TP_SEXO_DESC" in df_demografia.columns:
                df_demo_filt = df_demografia[df_demografia["SG_UF_PROVA"].isin(selected_ufs)].copy()
                if "IN_TREINEIRO_DESC" in df_demo_filt.columns:
                    df_demo_filt = df_demo_filt[df_demo_filt["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
                elif "IN_TREINEIRO" in df_demo_filt.columns:
                    df_demo_filt["IN_TREINEIRO"] = df_demo_filt["IN_TREINEIRO"].astype(str)
                    df_demo_filt = df_demo_filt[df_demo_filt["IN_TREINEIRO"].isin(selected_treineiro_values)]
                
                sex_counts = df_demo_filt.groupby("TP_SEXO_DESC")["total_candidatos"].sum()
                fig_pie = go.Figure(data=[go.Pie(labels=sex_counts.index.tolist(), values=sex_counts.values.tolist(), hole=.5, marker_colors=["#ec4899", "#2563eb"])])
                fig_pie.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
                st.plotly_chart(fig_pie, width="stretch")
            elif not filtered_df.empty:
                sex_col = "TP_SEXO_DESC" if "TP_SEXO_DESC" in filtered_df.columns else "TP_SEXO"
                sex_counts = filtered_df[sex_col].value_counts()
                fig_pie = go.Figure(data=[go.Pie(labels=sex_counts.index.tolist(), values=sex_counts.values.tolist(), hole=.5, marker_colors=["#ec4899", "#2563eb"])])
                fig_pie.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
                st.plotly_chart(fig_pie, width="stretch")
            else:
                st.info("Distribuição de sexo não disponível.")

    elif menu_opcao == "💰 Perfil Socioeconômico & Demográfico":
        st.subheader("💰 Distribuição por Faixa de Renda Familiar")
        if not df_notas_renda.empty:
            df_renda_filt = df_notas_renda.copy()
            if "IN_TREINEIRO_DESC" in df_renda_filt.columns:
                df_renda_filt = df_renda_filt[df_renda_filt["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
            elif "IN_TREINEIRO" in df_renda_filt.columns:
                df_renda_filt["IN_TREINEIRO"] = df_renda_filt["IN_TREINEIRO"].astype(str)
                df_renda_filt = df_renda_filt[df_renda_filt["IN_TREINEIRO"].isin(selected_treineiro_values)]
            
            cod_col = "RENDA_FAMILIAR_COD" if "RENDA_FAMILIAR_COD" in df_renda_filt.columns else ("Q006" if "Q006" in df_renda_filt.columns else df_renda_filt.columns[1])
            desc_col = "RENDA_FAMILIAR_DESC" if "RENDA_FAMILIAR_DESC" in df_renda_filt.columns else ("Q006_DESC" if "Q006_DESC" in df_renda_filt.columns else cod_col)
            
            df_renda_agg = df_renda_filt.groupby([cod_col, desc_col])["total_candidatos"].sum().reset_index()
            df_renda_agg["Faixa_Renda"] = df_renda_agg[cod_col].astype(str) + " — " + df_renda_agg[desc_col].astype(str)
            df_renda_agg = df_renda_agg.sort_values(by=cod_col)
            
            fig_renda = px.bar(
                df_renda_agg,
                x="Faixa_Renda", y="total_candidatos",
                color="total_candidatos", color_continuous_scale="Blues", text_auto=".2s",
                labels={"Faixa_Renda": "Faixa de Renda Familiar", "total_candidatos": "Total de Candidatos"}
            )
            fig_renda.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450, coloraxis_showscale=False)
            st.plotly_chart(fig_renda, width="stretch")
        elif not filtered_df.empty:
            cod_col = "RENDA_FAMILIAR_COD" if "RENDA_FAMILIAR_COD" in filtered_df.columns else "Q006"
            desc_col = "RENDA_FAMILIAR_DESC" if "RENDA_FAMILIAR_DESC" in filtered_df.columns else "Q006_DESC"
            
            if cod_col in filtered_df.columns and desc_col in filtered_df.columns:
                display_series = filtered_df[cod_col].astype(str) + " — " + filtered_df[desc_col].astype(str)
            elif cod_col in filtered_df.columns:
                display_series = filtered_df[cod_col].astype(str)
            else:
                display_series = pd.Series(dtype=str)
            
            if not display_series.empty:
                renda_counts = display_series.value_counts().reset_index()
                renda_counts.columns = ["Faixa_Renda", "total_inscritos"]
                fig_renda = px.bar(
                    renda_counts.sort_values(by="Faixa_Renda"),
                    x="Faixa_Renda", y="total_inscritos",
                    color="total_inscritos", color_continuous_scale="Blues", text_auto=".2s"
                )
                fig_renda.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420, coloraxis_showscale=False)
                st.plotly_chart(fig_renda, width="stretch")
            else:
                st.info("Dados de renda familiar não disponíveis no recorte atual.")
        else:
            st.info("Dados de renda familiar não disponíveis no recorte atual.")

    elif menu_opcao == "🏫 Redes de Ensino & Plurianual":
        st.markdown(f"### 🏫 Granularidade e Desempenho por Rede de Ensino — ENEM {selected_year} & Plurianual")
        st.markdown(
            "Análise detalhada baseada no campo oficial **`TP_DEPENDENCIA_ADM_ESC`** (1 = Federal, 2 = Estadual, 3 = Municipal, 4 = Privada), "
            "permitindo avaliar a volumetria, as disparidades de desempenho e a evolução temporal das escolas públicas versus rede privada."
        )

        if df_rede.empty:
            st.warning(
                f"⚠️ Nenhum dado de rede de ensino encontrado para o ano **{selected_year}**. "
                "Execute `python src/data_pipeline/transform.py` para gerar os agregados."
            )
        else:
            if "SG_UF_PROVA" in df_rede.columns:
                df_rede_filtered = df_rede[df_rede["SG_UF_PROVA"].isin(selected_ufs)].copy()
            else:
                df_rede_filtered = df_rede.copy()

            if df_rede_filtered.empty:
                st.warning(
                    f"⚠️ Nenhum registro encontrado para os estados selecionados em {selected_year}. "
                    "Verifique o filtro geográfico na barra lateral."
                )
                st.stop()

            def _media_pond(col_name, grp_df):
                def _calc(x):
                    total = grp_df.loc[x.index, "total_candidatos"].sum()
                    if total > 0:
                        return (x * grp_df.loc[x.index, "total_candidatos"]).sum() / total
                    return 0
                return (col_name, _calc)

            _nota_agg_cols = [c for c in ["media_mt", "media_redacao", "media_cn", "media_ch", "media_lc", "media_geral"] if c in df_rede_filtered.columns]

            rede_summary = df_rede_filtered.groupby("TP_DEPENDENCIA_ADM_ESC_DESC").agg(
                total_candidatos=("total_candidatos", "sum"),
                **{col: _media_pond(col, df_rede_filtered) for col in _nota_agg_cols}
            ).reset_index()

            total_geral_rede = rede_summary["total_candidatos"].sum()
            rede_summary["percentual_alunos"] = (
                (rede_summary["total_candidatos"] / total_geral_rede * 100).round(2)
                if total_geral_rede > 0 else 0
            )

            redes_identificadas = rede_summary[rede_summary["TP_DEPENDENCIA_ADM_ESC_DESC"] != "Não Informado"].copy()

            st.markdown("#### 📌 Destaques Executivos por Dependência Administrativa")
            k1, k2, k3, k4 = st.columns(4)

            cand_publica = rede_summary[rede_summary["TP_DEPENDENCIA_ADM_ESC_DESC"].isin(["Federal", "Estadual", "Municipal"])]["total_candidatos"].sum()
            cand_privada = rede_summary[rede_summary["TP_DEPENDENCIA_ADM_ESC_DESC"] == "Privada"]["total_candidatos"].sum()
            
            top_mt_rede = redes_identificadas.loc[redes_identificadas["media_mt"].idxmax()] if not redes_identificadas.empty else None
            top_red_rede = redes_identificadas.loc[redes_identificadas["media_redacao"].idxmax()] if not redes_identificadas.empty else None

            with k1:
                st.markdown(f"""
                <div class="clean-card">
                    <div class="metric-label-clean">Alunos Rede Pública (Fed+Est+Mun)</div>
                    <div class="metric-value-clean">{cand_publica:,.0f}</div>
                    <div class="metric-sub-clean">{(cand_publica/total_geral_rede*100):.1f}% do total</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class="clean-card">
                    <div class="metric-label-clean">Alunos Rede Privada</div>
                    <div class="metric-value-clean">{cand_privada:,.0f}</div>
                    <div class="metric-sub-clean">{(cand_privada/total_geral_rede*100):.1f}% do total</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                val_mt = f"{top_mt_rede['media_mt']:.1f}" if top_mt_rede is not None else "N/A"
                nome_mt = top_mt_rede['TP_DEPENDENCIA_ADM_ESC_DESC'] if top_mt_rede is not None else "-"
                st.markdown(f"""
                <div class="clean-card">
                    <div class="metric-label-clean">Maior Média Matemática</div>
                    <div class="metric-value-clean">{val_mt}</div>
                    <div class="metric-sub-clean">Líder: {nome_mt}</div>
                </div>
                """, unsafe_allow_html=True)
            with k4:
                val_red = f"{top_red_rede['media_redacao']:.1f}" if top_red_rede is not None else "N/A"
                nome_red = top_red_rede['TP_DEPENDENCIA_ADM_ESC_DESC'] if top_red_rede is not None else "-"
                st.markdown(f"""
                <div class="clean-card">
                    <div class="metric-label-clean">Maior Média Redação</div>
                    <div class="metric-value-clean">{val_red}</div>
                    <div class="metric-sub-clean">Líder: {nome_red}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 1️⃣ Volumetria de Alunos por Dependência Administrativa")
            col_v1, col_v2 = st.columns([5, 5])
            
            with col_v1:
                st.markdown("##### Total Absoluto de Inscritos")
                fig_vol = px.bar(
                    redes_identificadas,
                    x="TP_DEPENDENCIA_ADM_ESC_DESC",
                    y="total_candidatos",
                    color="TP_DEPENDENCIA_ADM_ESC_DESC",
                    color_discrete_map=COLOR_MAP_REDE,
                    text_auto=".2s",
                    labels={"TP_DEPENDENCIA_ADM_ESC_DESC": "Rede de Ensino", "total_candidatos": "Total de Candidatos"}
                )
                fig_vol.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350, showlegend=False)
                st.plotly_chart(fig_vol, width="stretch")

            with col_v2:
                st.markdown("##### Proporção / Participação (%)")
                fig_donut = px.pie(
                    redes_identificadas,
                    names="TP_DEPENDENCIA_ADM_ESC_DESC",
                    values="total_candidatos",
                    hole=0.5,
                    color="TP_DEPENDENCIA_ADM_ESC_DESC",
                    color_discrete_map=COLOR_MAP_REDE
                )
                fig_donut.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
                st.plotly_chart(fig_donut, width="stretch")

            st.markdown("---")
            st.markdown("#### 2️⃣ Comparativo Multidisciplinar de Desempenho (Barras Agrupadas)")
            _nota_cols = [c for c in ["media_cn", "media_ch", "media_lc", "media_mt", "media_redacao"] if c in redes_identificadas.columns]
            melted_notas = redes_identificadas.melt(
                id_vars=["TP_DEPENDENCIA_ADM_ESC_DESC"],
                value_vars=_nota_cols,
                var_name="Area_Conhecimento",
                value_name="Nota_Media"
            )
            area_names = {
                "media_cn": "Ciências da Natureza",
                "media_ch": "Ciências Humanas",
                "media_lc": "Linguagens e Códigos",
                "media_mt": "Matemática",
                "media_redacao": "Redação"
            }
            melted_notas["Area_Desc"] = melted_notas["Area_Conhecimento"].map(area_names)

            fig_grouped_bar = px.bar(
                melted_notas,
                x="Area_Desc",
                y="Nota_Media",
                color="TP_DEPENDENCIA_ADM_ESC_DESC",
                barmode="group",
                color_discrete_map=COLOR_MAP_REDE,
                text_auto=".1f",
                labels={"Area_Desc": "Área de Conhecimento", "Nota_Media": "Nota Média (TRI)", "TP_DEPENDENCIA_ADM_ESC_DESC": "Dependência Administrativa"}
            )
            fig_grouped_bar.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_grouped_bar, width="stretch")

            st.markdown("---")
            st.markdown("#### 3️⃣ Evolução Histórica Plurianual por Rede de Ensino")
            if not df_rede_plurianual.empty and "NU_ANO" in df_rede_plurianual.columns:
                _uf_mask = (
                    df_rede_plurianual["SG_UF_PROVA"].isin(selected_ufs)
                    if "SG_UF_PROVA" in df_rede_plurianual.columns
                    else pd.Series(True, index=df_rede_plurianual.index)
                )
                df_pluri_filtered = df_rede_plurianual[
                    (df_rede_plurianual["TP_DEPENDENCIA_ADM_ESC_DESC"] != "Não Informado") & _uf_mask
                ].copy()

                if not df_pluri_filtered.empty:
                    _pluri_nota_cols = [c for c in ["media_mt", "media_redacao", "media_cn", "media_ch", "media_lc", "media_geral"] if c in df_pluri_filtered.columns]

                    def _pp(col):
                        def _f(x):
                            total = df_pluri_filtered.loc[x.index, "total_candidatos"].sum()
                            return (x * df_pluri_filtered.loc[x.index, "total_candidatos"]).sum() / total if total > 0 else 0
                        return (col, _f)

                    pluri_summary = df_pluri_filtered.groupby(["NU_ANO", "TP_DEPENDENCIA_ADM_ESC_DESC"]).agg(
                        total_candidatos=("total_candidatos", "sum"),
                        **{col: _pp(col) for col in _pluri_nota_cols}
                    ).reset_index().sort_values(by="NU_ANO")

                    col_line1, col_line2 = st.columns(2)
                    with col_line1:
                        metric_to_plot = st.selectbox(
                            "Selecione a Métrica para Série Temporal:",
                            options=["media_mt", "media_redacao", "media_geral", "media_cn", "media_ch", "media_lc"],
                            format_func=lambda x: {
                                "media_mt": "Matemática",
                                "media_redacao": "Redação",
                                "media_geral": "Média Geral",
                                "media_cn": "Ciências da Natureza",
                                "media_ch": "Ciências Humanas",
                                "media_lc": "Linguagens e Códigos"
                            }[x]
                        )
                        fig_line_notas = px.line(
                            pluri_summary,
                            x="NU_ANO",
                            y=metric_to_plot,
                            color="TP_DEPENDENCIA_ADM_ESC_DESC",
                            markers=True,
                            color_discrete_map=COLOR_MAP_REDE,
                            title=f"Evolução das Notas ({metric_to_plot})",
                            labels={"NU_ANO": "Ano do Exame", metric_to_plot: "Nota Média", "TP_DEPENDENCIA_ADM_ESC_DESC": "Rede"}
                        )
                        fig_line_notas.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
                        st.plotly_chart(fig_line_notas, width="stretch")

                    with col_line2:
                        fig_line_vol = px.line(
                            pluri_summary,
                            x="NU_ANO",
                            y="total_candidatos",
                            color="TP_DEPENDENCIA_ADM_ESC_DESC",
                            markers=True,
                            color_discrete_map=COLOR_MAP_REDE,
                            title="Evolução de Inscritos por Rede",
                            labels={"NU_ANO": "Ano do Exame", "total_candidatos": "Total de Candidatos", "TP_DEPENDENCIA_ADM_ESC_DESC": "Rede"}
                        )
                        fig_line_vol.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
                        st.plotly_chart(fig_line_vol, width="stretch")

            st.markdown("---")
            st.markdown("#### 4️⃣ 🔬 Raio-X Avançado: Impacto Socioeconômico na Escola (`Q006` x `Q007` x Rede)")
            
            if not df_socio_escola.empty:
                opcoes_redes = [r for r in df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"].unique() if r != "Não Informado"]
                if not opcoes_redes:
                    opcoes_redes = df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"].unique()

                selected_rede_filter = st.selectbox(
                    "Filtrar por Dependência Administrativa da Escola:",
                    options=opcoes_redes
                )
                df_filtered_socio = df_socio_escola[df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"] == selected_rede_filter]
                
                fig_socio = px.scatter(
                    df_filtered_socio,
                    x="Q006_DESC",
                    y="media_matematica",
                    size="total_candidatos",
                    color="Q007_DESC",
                    hover_name="Q006_DESC",
                    title=f"Desempenho em Matemática vs Renda Familiar ({selected_rede_filter})",
                    labels={"Q006_DESC": "Faixa de Renda", "media_matematica": "Média Matemática", "Q007_DESC": "Trabalho (Q007)"}
                )
                fig_socio.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
                fig_socio.update_xaxes(tickangle=45)
                st.plotly_chart(fig_socio, width="stretch")

    elif menu_opcao == "📈 Desempenho & Notas (TRI)":
        st.subheader(f"📈 Análise de Desempenho e Notas Médias no ENEM {selected_year}")
        if df_notas_uf.empty:
            st.info("Dados agregados de notas não encontrados.")
        else:
            f_notas_uf = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)]
            if not f_notas_uf.empty and f_notas_uf["total_candidatos"].sum() > 0:
                tot_cand = f_notas_uf["total_candidatos"].sum()
                avg_redacao = (f_notas_uf["media_redacao"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
                avg_mt = (f_notas_uf["media_mt"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
                avg_cn = (f_notas_uf["media_cn"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
                avg_ch = (f_notas_uf["media_ch"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
                avg_lc = (f_notas_uf["media_lc"] * f_notas_uf["total_candidatos"]).sum() / tot_cand

                n1, n2, n3, n4, n5 = st.columns(5)
                with n1: st.metric("Matemática", f"{avg_mt:.1f}")
                with n2: st.metric("Redação", f"{avg_redacao:.1f}")
                with n3: st.metric("Natureza", f"{avg_cn:.1f}")
                with n4: st.metric("Humanas", f"{avg_ch:.1f}")
                with n5: st.metric("Linguagens", f"{avg_lc:.1f}")

                st.markdown("##### Desempenho Médio por UF")
                fig_notas_uf = px.bar(
                    f_notas_uf.groupby("SG_UF_PROVA")[["media_mt", "media_redacao"]].mean().reset_index(),
                    x="SG_UF_PROVA", y=["media_mt", "media_redacao"],
                    barmode="group",
                    labels={"value": "Nota Média", "variable": "Disciplina", "SG_UF_PROVA": "Estado (UF)"}
                )
                fig_notas_uf.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
                st.plotly_chart(fig_notas_uf, width="stretch")

    elif menu_opcao == "🤖 Machine Learning & IA":
        st.subheader("🧠 Performance do Modelo Preditivo")
        if ml_insights and "modelo_machine_learning" in ml_insights:
            metrics = ml_insights["modelo_machine_learning"]["metricas_avaliacao"]
            m1, m2, m3 = st.columns(3)
            with m1: st.metric(label="Acurácia Global", value=f"{metrics.get('accuracy', 0)*100:.2f}%")
            with m2: st.metric(label="ROC AUC", value=f"{metrics.get('roc_auc', 0):.4f}")
            with m3: st.metric(label="F1-Score", value=f"{metrics.get('f1_score', 0):.4f}")
            
            st.markdown("---")
            st.markdown("##### Importância das Variáveis")
            if "features_importantes" in ml_insights["modelo_machine_learning"]:
                feat_df = pd.DataFrame(ml_insights["modelo_machine_learning"]["features_importantes"])
                fig_feat = px.bar(feat_df, x="importancia", y="feature", orientation="h", title="Top Features Preditivas")
                fig_feat.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
                st.plotly_chart(fig_feat, width="stretch")
        else:
            st.info("Insights de Machine Learning não encontrados.")

    elif menu_opcao == "🌎 Geopolítica & Séries Temporais":
        st.subheader("🌎 Geopolítica e Séries Temporais Plurianual")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("##### 📍 Desempenho por Macrorregião")
            uf_to_regiao = {
                'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
                'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
                'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
                'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
                'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
            }
            if not df_notas_uf.empty:
                df_regiao = df_notas_uf.copy()
                df_regiao["Regiao"] = df_regiao["SG_UF_PROVA"].map(uf_to_regiao)
                df_regiao_agg = df_regiao.groupby("Regiao").agg(
                    media_matematica=("media_mt", "mean"),
                    media_redacao=("media_redacao", "mean")
                ).reset_index()
                
                fig_reg = px.bar(
                    df_regiao_agg, x="Regiao", y=["media_matematica", "media_redacao"], barmode="group",
                    title="Médias por Região", labels={"value": "Média", "variable": "Área"}
                )
                fig_reg.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
                st.plotly_chart(fig_reg, width="stretch")
                
        with col_g2:
            st.markdown("##### 📈 Evolução Histórica Nacional Plurianual")
            if not df_rede_plurianual.empty and "NU_ANO" in df_rede_plurianual.columns:
                nat_series = df_rede_plurianual.groupby("NU_ANO").agg(
                    Matematica=("media_mt", lambda x: (x * df_rede_plurianual.loc[x.index, "total_candidatos"]).sum() / df_rede_plurianual.loc[x.index, "total_candidatos"].sum() if df_rede_plurianual.loc[x.index, "total_candidatos"].sum() > 0 else 0),
                    Redacao=("media_redacao", lambda x: (x * df_rede_plurianual.loc[x.index, "total_candidatos"]).sum() / df_rede_plurianual.loc[x.index, "total_candidatos"].sum() if df_rede_plurianual.loc[x.index, "total_candidatos"].sum() > 0 else 0)
                ).reset_index()
                fig_time = px.line(
                    nat_series, x="NU_ANO", y=["Matematica", "Redacao"], markers=True,
                    title="Evolução Nacional", labels={"value": "Média", "variable": "Componente"}
                )
                fig_time.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
                st.plotly_chart(fig_time, width="stretch")

    elif menu_opcao == "🎓 Conclusão Estratégica":
        render_conclusao_estrategica()

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>Desenvolvido com PySpark, Streamlit & Plotly — Metodologia COFRE — Projeto Integrador (PI4 Univesp)</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Erro Crítico na Execução do Painel")
    st.exception(e)