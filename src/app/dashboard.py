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
    /* Fundo principal em cinza bem claro (#F8FAFC) e texto escuro (#0F172A) */
    .stApp, .main, .block-container {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Cabeçalhos e Títulos Principais no corpo */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    .main p, .main span, .main label {
        color: #334155;
    }

    /* Fundo da Barra Lateral (Sidebar) em tema claro limpo (#FFFFFF) com borda sutil */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Textos, rótulos e títulos na Barra Lateral legíveis */
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

    /* Componente de Alerta / Nota de Negócio na Sidebar */
    section[data-testid="stSidebar"] div[data-testid="stAlert"] {
        background-color: #F1F5F9 !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stAlert"] * {
        color: #334155 !important;
    }

    /* Tags do Multiselect na Sidebar */
    span[data-baseweb="tag"] {
        background-color: #2563EB !important;
        border-radius: 6px !important;
    }
    span[data-baseweb="tag"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Abas (Tabs) para visualização clara */
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

    /* Métricas Padrão do Streamlit */
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
    
    /* Cartões Clean para Dashboard */
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
    }
    
    /* Badges */
    .badge-primary {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 700;
        display: inline-block;
    }
    
    /* Indicadores numéricos KPI */
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


# Funções de carregamento de dados com Cache e Dicionário Enriquecido
@st.cache_data
def load_data():
    enriched_parquet_path = "data/processed/enem_2025_enriched_parquet"
    raw_parquet_path = "data/processed/enem_2025_cleaned_parquet"
    dict_path = "data/dictionary/enem_2025_dict.json"
    insights_path = "data/processed/enem_2025_ml_insights.json"
    notas_uf_path = "data/processed/enem_2025_agg_notas_uf_parquet"
    notas_renda_path = "data/processed/enem_2025_agg_notas_renda_parquet"
    
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
                'TP_FAIXA_ETARIA', 'TP_FAIXA_ETARIA_DESC'
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
        
    ml_insights = {}
    if os.path.exists(insights_path):
        with open(insights_path, "r", encoding="utf-8") as f:
            ml_insights = json.load(f)
            
    return df, df_notas_uf, df_notas_renda, ml_insights, enem_dict


df_raw, df_notas_uf, df_notas_renda, ml_insights, enem_dict = load_data()

# Header da Aplicação
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; padding: 20px 0; border-bottom: 1px solid #E2E8F0;">
    <div>
        <span class="badge-primary">Projeto Integrador (PI4 Univesp)</span>
        <h1 style="margin-top: 10px; margin-bottom: 0; font-size: 2.2rem;">🎓 ENEM 2025 — Analytics & AI Dashboard</h1>
        <p style="color: #475569; font-size: 1.05rem; margin-top: 5px;">Visão executiva, geográfica, socioeconômica e preditiva enriquecida via dicionário de dados oficial</p>
    </div>
</div>
""", unsafe_allow_html=True)

if df_raw.empty:
    st.error("Erro: Dados do ENEM não foram encontrados em `data/processed/enem_2025_enriched_parquet` nem em `enem_2025_cleaned_parquet`.")
    st.stop()

# Mapeamento do tipo de candidato
treineiro_map = {"Não Treineiro": "0", "Treineiro": "1"}

# --- PAINEL LATERAL (SIDEBAR) OTIMIZADO COM TEMA CLARO E EXPANDERS ---
st.sidebar.image("https://img.icons8.com/isometric-line/100/education.png", width=55)
st.sidebar.title("🎛️ Filtros de Pesquisa")

st.sidebar.divider()

# 1. Bloco de Recorte Geográfico (Expandido por padrão)
with st.sidebar.expander("📍 Recorte Geográfico", expanded=True):
    all_ufs = sorted(df_raw["SG_UF_PROVA"].unique())
    select_all_ufs = st.checkbox("Selecionar Todos os Estados (UF)", value=True)

    if select_all_ufs:
        selected_ufs = all_ufs
    else:
        selected_ufs = st.multiselect("Filtrar por UF:", all_ufs, default=all_ufs[:5] if len(all_ufs) >= 5 else all_ufs)

# 2. Bloco de Perfil do Candidato
with st.sidebar.expander("👤 Perfil do Candidato", expanded=False):
    selected_treineiro_labels = st.multiselect(
        "Tipo de Candidato (IN_TREINEIRO):",
        options=["Não Treineiro", "Treineiro"],
        default=["Não Treineiro", "Treineiro"],
        help="Selecione 'Treineiro' para candidatos que fazem o exame apenas para teste e 'Não Treineiro' para os concorrentes às vagas regulares do Sisu/Prouni."
    )

# 3. Nota Explicativa de Negócio em Bloco Limpo
st.sidebar.divider()
st.sidebar.info(
    "💡 **Nota de Negócio (Treineiros):**\n\n"
    "Treineiros são estudantes do 1º ou 2º ano do Ensino Médio que realizam o exame apenas para autoavaliação "
    "e não concorrem a vagas no Sisu/Prouni."
)

if not selected_ufs or not selected_treineiro_labels:
    st.warning("Por favor, selecione pelo menos um Estado e um Tipo de Candidato nos filtros laterais.")
    st.stop()

# Conversão dos rótulos selecionados para os valores originais '0' e '1'
selected_treineiro_values = [treineiro_map[label] for label in selected_treineiro_labels]

# Aplicação Global dos Filtros antes da renderização de qualquer gráfico
filtered_df = df_raw[
    (df_raw["SG_UF_PROVA"].isin(selected_ufs)) &
    (df_raw["IN_TREINEIRO"].isin(selected_treineiro_values))
]

# Cartões KPI principais
c1, c2, c3, c4 = st.columns(4)

total_inscritos = len(filtered_df)
total_treineiros = len(filtered_df[filtered_df["IN_TREINEIRO"] == "1"])
total_nao_treineiros = len(filtered_df[filtered_df["IN_TREINEIRO"] == "0"])
pct_treineiros = (total_treineiros / total_inscritos * 100) if total_inscritos > 0 else 0

top_uf = filtered_df["SG_UF_PROVA"].value_counts().idxmax() if total_inscritos > 0 else "N/A"
top_uf_count = filtered_df["SG_UF_PROVA"].value_counts().max() if total_inscritos > 0 else 0

with c1:
    st.markdown(f"""
    <div class="clean-card">
        <div class="metric-label-clean">Total de Inscritos (Filtrados)</div>
        <div class="metric-value-clean">{total_inscritos:,.0f}</div>
        <span style="color: #2563eb; font-size: 0.85rem; font-weight: 600;">Base consolidada</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="clean-card">
        <div class="metric-label-clean">Total Treineiros</div>
        <div class="metric-value-clean">{total_treineiros:,.0f}</div>
        <span style="color: #7c3aed; font-size: 0.85rem; font-weight: 600;">{pct_treineiros:.1f}% do filtro</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="clean-card">
        <div class="metric-label-clean">Não Treineiros (Regulares)</div>
        <div class="metric-value-clean">{total_nao_treineiros:,.0f}</div>
        <span style="color: #059669; font-size: 0.85rem; font-weight: 600;">Concorrentes Sisu/Prouni</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="clean-card">
        <div class="metric-label-clean">Estado Líder</div>
        <div class="metric-value-clean">{top_uf}</div>
        <span style="color: #db2777; font-size: 0.85rem; font-weight: 600;">{top_uf_count:,.0f} candidatos</span>
    </div>
    """, unsafe_allow_html=True)

# Abas de navegação principal
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Panorama Geográfico (UF)",
    "💰 Perfil Socioeconômico & Demográfico",
    "📈 Desempenho & Notas (TRI)",
    "🤖 Machine Learning & IA"
])

# TAB 1: PANORAMA GEOGRÁFICO
with tab1:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.subheader("Inscritos por Estado (UF)")
        uf_counts = filtered_df["SG_UF_PROVA"].value_counts().reset_index()
        uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
        
        fig_uf = px.bar(
            uf_counts.sort_values(by="total_inscritos", ascending=True),
            x="total_inscritos",
            y="SG_UF_PROVA",
            orientation="h",
            text_auto=".2s",
            color="total_inscritos",
            color_continuous_scale="Blues",
            labels={"total_inscritos": "Inscritos", "SG_UF_PROVA": "UF"}
        )
        fig_uf.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=450,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_uf, use_container_width=True)

    with col_right:
        st.subheader("Distribuição por Sexo")
        sex_col = "TP_SEXO_DESC" if "TP_SEXO_DESC" in filtered_df.columns else "TP_SEXO"
        sex_counts = filtered_df[sex_col].value_counts()
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=sex_counts.index.tolist(),
            values=sex_counts.values.tolist(),
            hole=.5,
            marker_colors=["#ec4899", "#2563eb"]
        )])
        fig_pie.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=450
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Definição dinâmica do título e cálculo percentual
    set_labels = set(selected_treineiro_labels)
    if set_labels == {"Treineiro"}:
        chart_title = "Percentual de Treineiros por Estado (%)"
        pct_col_label = "% Treineiros"
        pct_df = filtered_df.groupby("SG_UF_PROVA")["IN_TREINEIRO"].apply(
            lambda x: (x == "1").sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
    elif set_labels == {"Não Treineiro"}:
        chart_title = "Percentual de Não Treineiros por Estado (%)"
        pct_col_label = "% Não Treineiros"
        pct_df = filtered_df.groupby("SG_UF_PROVA")["IN_TREINEIRO"].apply(
            lambda x: (x == "0").sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
    else:
        chart_title = "Distribuição de Candidatos (Treineiros e Não Treineiros) por Estado (%)"
        pct_col_label = "% Treineiros"
        pct_df = filtered_df.groupby("SG_UF_PROVA")["IN_TREINEIRO"].apply(
            lambda x: (x == "1").sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()

    pct_df.columns = ["SG_UF_PROVA", "pct_valor"]

    st.subheader(chart_title)
    fig_pct = px.bar(
        pct_df.sort_values(by="pct_valor", ascending=False),
        x="SG_UF_PROVA",
        y="pct_valor",
        color="pct_valor",
        color_continuous_scale="Purples",
        text_auto=".1f",
        labels={"pct_valor": pct_col_label, "SG_UF_PROVA": "UF"}
    )
    fig_pct.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_pct, use_container_width=True)

# TAB 2: PERFIL SOCIOECONÔMICO & DEMOGRÁFICO
with tab2:
    st.subheader("💰 Distribuição por Faixa de Renda Familiar (Q006)")
    
    # Preparação da coluna descritiva formatada
    if "Q006_DESC" in filtered_df.columns:
        display_series = filtered_df["Q006"] + " — " + filtered_df["Q006_DESC"]
    else:
        q006_map = enem_dict.get("Q006", {})
        display_series = filtered_df["Q006"].map(lambda c: f"{c} — {q006_map.get(c, c)}" if c in q006_map else c)
        
    renda_counts = display_series.value_counts().reset_index()
    renda_counts.columns = ["Faixa_Renda", "total_inscritos"]
    
    fig_renda = px.bar(
        renda_counts.sort_values(by="Faixa_Renda"),
        x="Faixa_Renda",
        y="total_inscritos",
        color="total_inscritos",
        color_continuous_scale="Blues",
        text_auto=".2s",
        labels={"Faixa_Renda": "Faixa de Renda Familiar", "total_inscritos": "Quantidade de Candidatos"}
    )
    fig_renda.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=420,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_renda, use_container_width=True)

    st.divider()
    
    # Gráficos Adicionais de Perfil Demográfico (Cor/Raça e Situação de Conclusão)
    d_col1, d_col2 = st.columns(2)
    
    with d_col1:
        st.subheader("🎨 Distribuição por Cor / Raça")
        if "TP_COR_RACA_DESC" in filtered_df.columns:
            raca_counts = filtered_df["TP_COR_RACA_DESC"].value_counts().reset_index()
            raca_counts.columns = ["Cor_Raca", "total_inscritos"]
            
            fig_raca = px.bar(
                raca_counts.sort_values(by="total_inscritos", ascending=True),
                x="total_inscritos",
                y="Cor_Raca",
                orientation="h",
                text_auto=".2s",
                color="total_inscritos",
                color_continuous_scale="Teal",
                labels={"total_inscritos": "Candidatos", "Cor_Raca": "Cor / Raça"}
            )
            fig_raca.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_raca, use_container_width=True)
            
    with d_col2:
        st.subheader("🎓 Situação de Conclusão do Ensino Médio")
        if "TP_ST_CONCLUSAO_DESC" in filtered_df.columns:
            st_counts = filtered_df["TP_ST_CONCLUSAO_DESC"].value_counts().reset_index()
            st_counts.columns = ["Situacao", "total_inscritos"]
            
            fig_st = px.bar(
                st_counts.sort_values(by="total_inscritos", ascending=True),
                x="total_inscritos",
                y="Situacao",
                orientation="h",
                text_auto=".2s",
                color="total_inscritos",
                color_continuous_scale="Purples",
                labels={"total_inscritos": "Candidatos", "Situacao": "Situação de Conclusão"}
            )
            fig_st.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=380,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_st, use_container_width=True)

# TAB 3: DESEMPENHO & NOTAS (TRI)
with tab3:
    st.subheader("📈 Análise de Desempenho e Notas Médias no ENEM 2025")
    
    if df_notas_uf.empty or df_notas_renda.empty:
        st.info("Dados de desempenho de notas não encontrados. Execute o pipeline de transformação para gerar os arquivos agregados.")
    else:
        # Filtragem das bases agregadas de notas com base nos filtros da barra lateral
        f_notas_uf = df_notas_uf[
            (df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)) &
            (df_notas_uf["IN_TREINEIRO"].isin(selected_treineiro_values))
        ]
        
        f_notas_renda = df_notas_renda[
            df_notas_renda["IN_TREINEIRO"].isin(selected_treineiro_values)
        ]
        
        # Média geral ponderada das notas no filtro atual
        if not f_notas_uf.empty and f_notas_uf["total_candidatos"].sum() > 0:
            tot_cand = f_notas_uf["total_candidatos"].sum()
            avg_redacao = (f_notas_uf["media_redacao"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_mt = (f_notas_uf["media_mt"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_lc = (f_notas_uf["media_lc"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_ch = (f_notas_uf["media_ch"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_cn = (f_notas_uf["media_cn"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            
            n1, n2, n3, n4, n5 = st.columns(5)
            with n1:
                st.metric("Redação (Média)", f"{avg_redacao:.1f}")
            with n2:
                st.metric("Matemática (Média)", f"{avg_mt:.1f}")
            with n3:
                st.metric("Linguagens (Média)", f"{avg_lc:.1f}")
            with n4:
                st.metric("Ciências Humanas (Média)", f"{avg_ch:.1f}")
            with n5:
                st.metric("Ciências da Natureza (Média)", f"{avg_cn:.1f}")
                
            st.markdown("---")
        
        # Gráfico 1: Renda vs Desempenho (Com rótulos legíveis do dicionário)
        st.subheader("💰 Gráfico 1: Desempenho Médio por Faixa de Renda Familiar")
        
        if not f_notas_renda.empty:
            q006_map = enem_dict.get("Q006", {})
            
            renda_avg = f_notas_renda.groupby("Q006").apply(
                lambda g: pd.Series({
                    "Redação": (g["media_redacao"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Matemática": (g["media_mt"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Linguagens": (g["media_lc"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Ciências Humanas": (g["media_ch"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Ciências da Natureza": (g["media_cn"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0
                }),
                include_groups=False
            ).reset_index()
            
            # Formatação de rótulos descritivos no eixo X
            renda_avg["Faixa_Renda_Label"] = renda_avg["Q006"].apply(
                lambda code: f"{code} — {q006_map.get(code, code)}" if code in q006_map else code
            )
            
            renda_melted = renda_avg.melt(
                id_vars=["Q006", "Faixa_Renda_Label"],
                var_name="Prova",
                value_name="Nota_Media"
            )
            
            fig_renda_notas = px.bar(
                renda_melted.sort_values(by="Q006"),
                x="Faixa_Renda_Label",
                y="Nota_Media",
                color="Prova",
                barmode="group",
                text_auto=".1f",
                labels={"Faixa_Renda_Label": "Faixa de Renda Familiar", "Nota_Media": "Nota Média"},
                color_discrete_sequence=["#db2777", "#2563eb", "#059669", "#d97706", "#7c3aed"]
            )
            fig_renda_notas.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=450
            )
            st.plotly_chart(fig_renda_notas, use_container_width=True)
        
        # Gráfico 2: Desempenho Geográfico por Estado (UF)
        st.subheader("🗺️ Gráfico 2: Desempenho Médio por Estado (SG_UF_PROVA)")
        
        if not f_notas_uf.empty:
            uf_avg = f_notas_uf.groupby("SG_UF_PROVA").apply(
                lambda g: pd.Series({
                    "Redação": (g["media_redacao"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Matemática": (g["media_mt"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Linguagens": (g["media_lc"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Ciências Humanas": (g["media_ch"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0,
                    "Ciências da Natureza": (g["media_cn"] * g["total_candidatos"]).sum() / g["total_candidatos"].sum() if g["total_candidatos"].sum() > 0 else 0
                }),
                include_groups=False
            ).reset_index()
            
            uf_melted = uf_avg.melt(id_vars=["SG_UF_PROVA"], var_name="Prova", value_name="Nota_Media")
            
            fig_uf_notas = px.bar(
                uf_melted.sort_values(by="Nota_Media", ascending=False),
                x="SG_UF_PROVA",
                y="Nota_Media",
                color="Prova",
                barmode="group",
                text_auto=".1f",
                labels={"SG_UF_PROVA": "UF", "Nota_Media": "Nota Média"},
                color_discrete_sequence=["#db2777", "#2563eb", "#059669", "#d97706", "#7c3aed"]
            )
            fig_uf_notas.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=450
            )
            st.plotly_chart(fig_uf_notas, use_container_width=True)

# TAB 4: MACHINE LEARNING & IA
with tab4:
    st.subheader("🧠 Performance do Modelo de Predição de Treineiros")
    
    if ml_insights and "modelo_machine_learning" in ml_insights:
        ml_data = ml_insights["modelo_machine_learning"]
        metrics = ml_data["metricas_avaliacao"]
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Acurácia do Modelo", value=f"{metrics['accuracy']*100:.2f}%")
        with m2:
            st.metric(label="Área sob a Curva ROC (AUC)", value=f"{metrics['roc_auc']:.4f}")
        with m3:
            st.metric(label="Precisão-Recall AUC", value=f"{metrics['pr_auc']:.4f}")
        with m4:
            st.metric(label="F1-Score", value=f"{metrics['f1_score']:.4f}")
            
        st.markdown("---")
        st.markdown(f"**Algoritmo**: `{ml_data['algoritmo']}`")
        st.markdown(f"**Variável Alvo**: `{ml_data['variavel_alvo']}`")
        st.markdown(f"**Atributos Preditivos (Features)**: `{', '.join(ml_data['features_utilizadas'])}`")
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics['accuracy'] * 100,
            title={'text': "Acurácia Global do Modelo PySpark ML (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#059669"},
                'steps': [
                    {'range': [0, 60], 'color': "#ef4444"},
                    {'range': [60, 80], 'color': "#f59e0b"},
                    {'range': [80, 100], 'color': "#d1fae5"}
                ]
            }
        ))
        fig_gauge.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.info("Relatório de Machine Learning não encontrado em `data/processed/enem_2025_ml_insights.json`.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem;">
    Desenvolvido com PySpark, Streamlit & Plotly — Projeto Integrador (PI4 Univesp)
</div>
""", unsafe_allow_html=True)