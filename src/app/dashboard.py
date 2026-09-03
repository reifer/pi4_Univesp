import pandas as pd
import streamlit as st
from config.settings import COLOR_MAP_REDE, apply_custom_css
from utils.data_loader import load_data
from pages.conclusao_estrategica import render as render_conclusao_estrategica

# Importação dos Componentes Modulares
from components.geo_view import render_geo_view
from components.socio_view import render_socio_view
from components.rede_view import render_rede_view
from components.desempenho_view import render_desempenho_view
from components.ml_view import render_ml_view
from components.geopolitica_view import render_geopolitica_view

# Configuração inicial da página (Tema claro profissional & responsivo)
st.set_page_config(
    page_title="ENEM Analytics & AI — Plurianual PI4",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplica a estilização CSS personalizada centralizada
apply_custom_css()

try:
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

    # === ROTEAMENTO DOS MÓDULOS MODULARIZADOS ===
    if menu_opcao == "📊 Panorama Geográfico (UF)":
        render_geo_view(selected_ufs, selected_treineiro_labels, selected_treineiro_values, df_notas_uf, df_demografia, filtered_df)

    elif menu_opcao == "💰 Perfil Socioeconômico & Demográfico":
        render_socio_view(df_notas_renda, selected_treineiro_labels, selected_treineiro_values, filtered_df)

    elif menu_opcao == "🏫 Redes de Ensino & Plurianual":
        render_rede_view(selected_year, selected_ufs, df_rede, df_rede_plurianual, df_socio_escola, COLOR_MAP_REDE)

    elif menu_opcao == "📈 Desempenho & Notas (TRI)":
        render_desempenho_view(selected_year, selected_ufs, df_notas_uf)

    elif menu_opcao == "🤖 Machine Learning & IA":
        render_ml_view(ml_insights)

    elif menu_opcao == "🌎 Geopolítica & Séries Temporais":
        render_geopolitica_view(df_notas_uf, df_rede_plurianual)

    elif menu_opcao == "🎓 Conclusão Estratégica":
        render_conclusao_estrategica()

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>Desenvolvido com PySpark, Streamlit & Plotly — Metodologia COFRE — Projeto Integrador (PI4 Univesp)</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Erro Crítico na Execução do Painel")
    st.exception(e)