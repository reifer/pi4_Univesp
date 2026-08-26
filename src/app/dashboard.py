import json
import os
import pandas as pd
import pyarrow.dataset as ds
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração inicial da página (Tema claro forçado globalmente)
st.set_page_config(
    page_title="ENEM 2025 - Analytics & AI Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (Tema Claro Profissional & Clean)
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
    section[data-testid="stSidebar"] div[data-testid="stAlert"] * {
        color: #334155 !important;
    }
    span[data-baseweb="tag"] {
        background-color: #2563EB !important;
        border-radius: 6px !important;
    }
    span[data-baseweb="tag"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"] {
        color: #475569 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        background-color: transparent !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 12px 24px !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563EB !important;
        border-bottom: 3px solid #2563EB !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
    }
    .badge-primary {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 700;
        display: inline-block;
    }
    .metric-value-clean {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
    }
    .metric-label-clean {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    enriched_parquet_path = "data/processed/enem_2025_enriched_parquet"
    raw_parquet_path = "data/processed/enem_2025_cleaned_parquet"
    dict_path = "data/dictionary/enem_2025_dict.json"
    insights_path = "data/processed/enem_2025_ml_insights.json"
    notas_uf_path = "data/processed/enem_2025_agg_notas_uf_parquet"
    notas_renda_path = "data/processed/enem_2025_agg_notas_renda_parquet"
    rede_path = "data/processed/enem_2025_agg_rede_ensino_parquet"
    socio_avancado_path = "data/processed/enem_2025_agg_socio_avancado_parquet"
    socio_escola_path = "data/processed/enem_2025_agg_socio_escola_parquet"
    
    enem_dict = {}
    if os.path.exists(dict_path):
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                enem_dict = json.load(f)
        except Exception as ex:
            st.sidebar.warning(f"Erro ao ler dicionário JSON: {ex}")

    df = pd.DataFrame()
    if os.path.exists(enriched_parquet_path):
        try:
            dataset = ds.dataset(enriched_parquet_path)
            available_cols = dataset.schema.names
            desired_cols = [
                'SG_UF_PROVA', 'IN_TREINEIRO', 'IN_TREINEIRO_DESC',
                'TP_SEXO', 'TP_SEXO_DESC',
                'Q006', 'Q006_DESC',
                'Q007', 'Q007_DESC',
                'TP_COR_RACA', 'TP_COR_RACA_DESC',
                'TP_ST_CONCLUSAO', 'TP_ST_CONCLUSAO_DESC',
                'TP_FAIXA_ETARIA', 'TP_FAIXA_ETARIA_DESC',
                'TP_DEPENDENCIA_ADM_ESC', 'TP_DEPENDENCIA_ADM_ESC_DESC'
            ]
            cols_to_load = [c for c in desired_cols if c in available_cols]
            df = pd.read_parquet(enriched_parquet_path, columns=cols_to_load)
        except Exception as ex:
            st.sidebar.warning(f"Recorrendo ao dataset padrão devido a: {ex}")
            if os.path.exists(raw_parquet_path):
                df = pd.read_parquet(raw_parquet_path, columns=['SG_UF_PROVA', 'IN_TREINEIRO', 'TP_SEXO', 'Q006'])
    elif os.path.exists(raw_parquet_path):
        df = pd.read_parquet(raw_parquet_path, columns=['SG_UF_PROVA', 'IN_TREINEIRO', 'TP_SEXO', 'Q006'])

    df_notas_uf = pd.read_parquet(notas_uf_path) if os.path.exists(notas_uf_path) else pd.DataFrame()
    df_notas_renda = pd.read_parquet(notas_renda_path) if os.path.exists(notas_renda_path) else pd.DataFrame()
    df_rede = pd.read_parquet(rede_path) if os.path.exists(rede_path) else pd.DataFrame()
    df_socio_avancado = pd.read_parquet(socio_avancado_path) if os.path.exists(socio_avancado_path) else pd.DataFrame()
    df_socio_escola = pd.read_parquet(socio_escola_path) if os.path.exists(socio_escola_path) else pd.DataFrame()
        
    ml_insights = {}
    if os.path.exists(insights_path):
        with open(insights_path, "r", encoding="utf-8") as f:
            ml_insights = json.load(f)
            
    return df, df_notas_uf, df_notas_renda, df_rede, df_socio_avancado, df_socio_escola, ml_insights, enem_dict

df_raw, df_notas_uf, df_notas_renda, df_rede, df_socio_avancado, df_socio_escola, ml_insights, enem_dict = load_data()

# Header da Aplicação
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; padding: 20px 0; border-bottom: 1px solid #E2E8F0;">
    <div>
        <span class="badge-primary">Projeto Integrador (PI4 Univesp)</span>
        <h1 style="margin-top: 10px; margin-bottom: 0; font-size: 2.2rem;">🎓 ENEM 2025 — Analytics & AI Dashboard</h1>
        <p style="color: #475569; font-size: 1.05rem; margin-top: 5px;">Visão executiva, geográfica, socioeconômica, redes de ensino detalhadas e preditiva</p>
    </div>
</div>
""", unsafe_allow_html=True)

if df_raw.empty:
    st.error("Erro: Dados do ENEM não encontrados.")
    st.stop()

treineiro_map = {"Não Treineiro": "0", "Treineiro": "1"}

# --- PAINEL LATERAL (SIDEBAR) COM EXPANDERS ---
st.sidebar.image("https://img.icons8.com/isometric-line/100/education.png", width=55)
st.sidebar.title("🎛️ Filtros de Pesquisa")
st.sidebar.divider()

with st.sidebar.expander("📍 Recorte Geográfico", expanded=True):
    all_ufs = sorted(df_raw["SG_UF_PROVA"].unique())
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
        help="Selecione 'Treineiro' para testes e 'Não Treineiro' para concorrentes regulares do Sisu/Prouni."
    )

st.sidebar.divider()
st.sidebar.info(
    "💡 **Nota de Negócio (Treineiros):**\n\n"
    "Treineiros realizam o exame para autoavaliação e não concorrem a vagas diretas no Sisu/Prouni."
)

if not selected_ufs or not selected_treineiro_labels:
    st.warning("Selecione pelo menos um Estado e um Tipo de Candidato nos filtros laterais.")
    st.stop()

selected_treineiro_values = [treineiro_map[label] for label in selected_treineiro_labels]

filtered_df = df_raw[
    (df_raw["SG_UF_PROVA"].isin(selected_ufs)) &
    (df_raw["IN_TREINEIRO"].isin(selected_treineiro_values))
]

# Cards KPI
c1, c2, c3, c4 = st.columns(4)
total_inscritos = len(filtered_df)
total_treineiros = len(filtered_df[filtered_df["IN_TREINEIRO"] == "1"])
total_nao_treineiros = len(filtered_df[filtered_df["IN_TREINEIRO"] == "0"])
top_uf = filtered_df["SG_UF_PROVA"].value_counts().idxmax() if total_inscritos > 0 else "N/A"

with c1:
    st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Total de Inscritos (Filtrados)</div><div class="metric-value-clean">{total_inscritos:,.0f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Total Treineiros</div><div class="metric-value-clean">{total_treineiros:,.0f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Não Treineiros (Regulares)</div><div class="metric-value-clean">{total_nao_treineiros:,.0f}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="clean-card"><div class="metric-label-clean">Estado Líder</div><div class="metric-value-clean">{top_uf}</div></div>', unsafe_allow_html=True)

# Abas de visualização atualizadas com Redes de Ensino e Raio-X Avançado
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Panorama Geográfico (UF)",
    "💰 Perfil Socioeconômico & Demográfico",
    "🏫 Redes de Ensino & Impacto",
    "📈 Desempenho & Notas (TRI)",
    "🤖 Machine Learning & IA"
])

with tab1:
    col_left, col_right = st.columns([6, 4])
    with col_left:
        st.subheader("Inscritos por Estado (UF)")
        uf_counts = filtered_df["SG_UF_PROVA"].value_counts().reset_index()
        uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
        fig_uf = px.bar(uf_counts.sort_values(by="total_inscritos", ascending=True), x="total_inscritos", y="SG_UF_PROVA", orientation="h", text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues")
        fig_uf.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450, coloraxis_showscale=False)
        st.plotly_chart(fig_uf, use_container_width=True)
    with col_right:
        st.subheader("Distribuição por Sexo")
        sex_col = "TP_SEXO_DESC" if "TP_SEXO_DESC" in filtered_df.columns else "TP_SEXO"
        sex_counts = filtered_df[sex_col].value_counts()
        fig_pie = go.Figure(data=[go.Pie(labels=sex_counts.index.tolist(), values=sex_counts.values.tolist(), hole=.5, marker_colors=["#ec4899", "#2563eb"])])
        fig_pie.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("💰 Distribuição por Faixa de Renda Familiar")
    if "Q006_DESC" in filtered_df.columns and "Q006" in filtered_df.columns:
        display_series = filtered_df["Q006"] + " — " + filtered_df["Q006_DESC"]
    else:
        display_series = filtered_df["Q006"]
    
    renda_counts = display_series.value_counts().reset_index()
    renda_counts.columns = ["Faixa_Renda", "total_inscritos"]
    fig_renda = px.bar(renda_counts.sort_values(by="Faixa_Renda"), x="Faixa_Renda", y="total_inscritos", color="total_inscritos", color_continuous_scale="Blues", text_auto=".2s")
    fig_renda.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420, coloraxis_showscale=False)
    st.plotly_chart(fig_renda, use_container_width=True)

with tab3:
    st.subheader("🏫 Análise Detalhada por Rede de Ensino (Fase 5.1 & 5.2)")
    if df_rede.empty:
        st.info("Dados de agregação por rede de ensino não encontrados. Execute o transform.py atualizado.")
    else:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("##### Candidatos por Dependência Administrativa")
            fig_rede = px.bar(df_rede, x="TP_DEPENDENCIA_ADM_ESC_DESC", y="total_candidatos", color="TP_DEPENDENCIA_ADM_ESC_DESC", text_auto=".2s")
            fig_rede.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, showlegend=False)
            st.plotly_chart(fig_rede, use_container_width=True)
        with col_r2:
            st.markdown("##### Média de Notas de Matemática por Rede")
            fig_rede_mat = px.bar(df_rede, x="TP_DEPENDENCIA_ADM_ESC_DESC", y="media_matematica", color="TP_DEPENDENCIA_ADM_ESC_DESC", text_auto=".1f")
            fig_rede_mat.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380, showlegend=False)
            st.plotly_chart(fig_rede_mat, use_container_width=True)

    # Inclusão da visualização da Fase 5.2: Raio-X Socioeconômico Avançado
    st.markdown("---")
    st.markdown("##### 🔬 Raio-X Avançado: Impacto da Renda e Autonomia na Escola (`Q006` x `Q007`)")
    
    if not df_socio_escola.empty:
        selected_rede_filter = st.selectbox(
            "Filtrar por Dependência Administrativa da Escola:",
            options=df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"].unique()
        )
        df_filtered_socio = df_socio_escola[df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"] == selected_rede_filter]
        
        fig_socio = px.scatter(
            df_filtered_socio,
            x="Q006_DESC",
            y="media_matematica",
            size="total_candidatos",
            color="Q007_DESC",
            hover_name="Q006_DESC",
            title=f"Desempenho em Matemática vs Faixa de Renda e Suporte/Trabalho ({selected_rede_filter})",
            labels={"Q006_DESC": "Faixa de Renda Familiar", "media_matematica": "Média de Matemática", "Q007_DESC": "Suporte / Autonomia (Q007)"}
        )
        fig_socio.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
        fig_socio.update_xaxes(tickangle=45)
        st.plotly_chart(fig_socio, use_container_width=True)
    else:
        st.info("Execute o transform.py atualizado para gerar a base agregada da Fase 5.2.")

with tab4:
    st.subheader("📈 Análise de Desempenho e Notas Médias no ENEM 2025")
    if df_notas_uf.empty:
        st.info("Dados agregados de notas não encontrados.")
    else:
        f_notas_uf = df_notas_uf[(df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)) & (df_notas_uf["IN_TREINEIRO"].isin(selected_treineiro_values))]
        if not f_notas_uf.empty and f_notas_uf["total_candidatos"].sum() > 0:
            tot_cand = f_notas_uf["total_candidatos"].sum()
            avg_redacao = (f_notas_uf["media_redacao"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_mt = (f_notas_uf["media_mt"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            n1, n2 = st.columns(2)
            with n1: st.metric("Redação (Média)", f"{avg_redacao:.1f}")
            with n2: st.metric("Matemática (Média)", f"{avg_mt:.1f}")

with tab5:
    st.subheader("🧠 Performance do Modelo Preditivo")
    if ml_insights and "modelo_machine_learning" in ml_insights:
        metrics = ml_insights["modelo_machine_learning"]["metricas_avaliacao"]
        st.metric(label="Acurácia do Modelo", value=f"{metrics['accuracy']*100:.2f}%")
    else:
        st.info("Insights de Machine Learning não encontrados.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>Desenvolvido com PySpark, Streamlit & Plotly — Projeto Integrador (PI4 Univesp)</div>", unsafe_allow_html=True)