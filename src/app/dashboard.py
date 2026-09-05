import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parents[1]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import pandas as pd
import streamlit as st
from app.config.settings import COLOR_MAP_REDE, apply_custom_css
from app.utils.data_loader import load_data
from app.pages.conclusao_estrategica import render as render_conclusao_estrategica

# Importação dos Componentes Modulares
from app.components.geo_view import render_geo_view
from app.components.socio_view import render_socio_view
from app.components.rede_view import render_rede_view
from app.components.desempenho_view import render_desempenho_view
from app.components.ml_view import render_ml_view
from app.components.geopolitica_view import render_geopolitica_view

# Configuração inicial da página (Layout Wide & Sidebar Oculta)
st.set_page_config(
    page_title="ENEM Analytics & AI — Plurianual PI4",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplica a estilização CSS personalizada centralizada
apply_custom_css()

# --- CSS SÊNIOR: COMPACTAÇÃO EXTREMA DE MULTISELECT (ESTILO COMBOBOX OCULTO) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    button[kind="header"] {
        display: none !important;
    }
    
    /* Força o multiselect a se comportar como um combobox compacto com scroll interno restrito */
    div[data-baseweb="select"] > div:first-child {
        max-height: 42px !important;
        overflow-y: auto !important;
        flex-wrap: nowrap !important;
    }
    
    /* Esconde as pílulas gigantes e otimiza o espaço no mobile */
    div[data-baseweb="tag"] {
        transform: scale(0.9);
        margin: 1px !important;
    }
</style>
""", unsafe_allow_html=True)

try:
    # --- CABEÇALHO PRINCIPAL INSTITUCIONAL ---
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; padding: 10px 0 2px 0; border-bottom: 1px solid #E2E8F0;">
        <div>
            <span class="badge-primary">Projeto Integrador (PI4 Univesp)</span>
            <h1 style="margin-top: 4px; margin-bottom: 0; font-size: 1.8rem; font-weight: 800; color: #0F172A;">🎓 ENEM Analytics & AI Dashboard</h1>
            <p style="color: #64748b; font-size: 0.9rem; margin-top: 2px;">Análise plurianual de desempenho, perfil socioeconômico e granularidade por redes de ensino</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Carregamento prévio dos dados
    selected_year = st.selectbox("📅 Recorte Temporal (Ano):", ["2025", "2024", "2023", "2022", "2021"], index=0, key="global_year")
    df_raw, df_notas_uf, df_notas_renda, df_rede, df_rede_plurianual, df_socio_escola, df_demografia, ml_insights, enem_dict, df_renda_raca = load_data(selected_year)

    if df_raw.empty and df_rede.empty:
        st.error(f"Erro: Dados do ENEM {selected_year} não encontrados. Execute o pipeline de transformação primeiro.")
        st.stop()

    treineiro_map = {"Não Treineiro": "0", "Treineiro": "1"}

    if not df_raw.empty and "SG_UF_PROVA" in df_raw.columns:
        all_ufs = sorted(df_raw["SG_UF_PROVA"].dropna().unique())  # type: ignore[reportAttributeAccessIssue]
    elif not df_rede.empty and "SG_UF_PROVA" in df_rede.columns:
        all_ufs = sorted(df_rede["SG_UF_PROVA"].dropna().unique())  # type: ignore[reportAttributeAccessIssue]
    else:
        all_ufs = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

    # --- BARRA DE AÇÕES GLOBAIS (TOOLBAR SUPERIOR COMPACTA) ---
    col_tb1, col_tb2 = st.columns([3, 2])

    with col_tb1:
        selected_ufs = st.multiselect("📍 Selecione as UFs (Estados):", options=all_ufs, default=all_ufs)

    with col_tb2:
        selected_treineiro_labels = st.multiselect(
            "👤 Tipo de Candidato:",
            options=["Não Treineiro", "Treineiro"],
            default=["Não Treineiro", "Treineiro"]
        )

    st.markdown("---")

    # --- NAVEGAÇÃO SUPERIOR POR PÍLULAS MODERNAS (MODERN PILLS) ---
    st.markdown("##### 🧭 Módulos de Análise:")
    
    modulos_disponiveis = [
        "📊 Panorama Geográfico",
        "💰 Perfil Socioeconômico",
        "🏫 Redes de Ensino",
        "📈 Desempenho TRI",
        "🤖 Machine Learning",
        "🌎 Geopolítica",
        "🎓 Conclusão Estratégica"
    ]
    
    menu_opcao: str = st.pills(  # type: ignore[assignment]
        "Módulos de Análise",
        options=modulos_disponiveis,
        default="📊 Panorama Geográfico",
        label_visibility="collapsed"
    ) or "📊 Panorama Geográfico"

    st.markdown("---")

    if not selected_ufs or not selected_treineiro_labels:
        st.warning("⚠️ Selecione pelo menos um Estado e um Tipo de Candidato nos filtros acima.")
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

    # --- CARDS KPI GERAIS DO TOPO ---
    c1, c2, c3, c4 = st.columns(4)
    if not df_notas_uf.empty and "SG_UF_PROVA" in df_notas_uf.columns:
        df_kpi_uf = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)].copy()  # type: ignore[reportAttributeAccessIssue]
        if "IN_TREINEIRO_DESC" in df_kpi_uf.columns:
            df_kpi_filtered = df_kpi_uf[df_kpi_uf["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]  # type: ignore[reportAttributeAccessIssue]
            total_inscritos = int(df_kpi_filtered["total_candidatos"].sum())  # type: ignore[reportArgumentType]
            total_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO_DESC"] == "Treineiro"]["total_candidatos"].sum())  # type: ignore[reportArgumentType]
            total_nao_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO_DESC"] == "Não Treineiro"]["total_candidatos"].sum())  # type: ignore[reportArgumentType]
        elif "IN_TREINEIRO" in df_kpi_uf.columns:
            df_kpi_uf["IN_TREINEIRO"] = df_kpi_uf["IN_TREINEIRO"].astype(str)
            df_kpi_filtered = df_kpi_uf[df_kpi_uf["IN_TREINEIRO"].isin(selected_treineiro_values)]  # type: ignore[reportAttributeAccessIssue]
            total_inscritos = int(df_kpi_filtered["total_candidatos"].sum())  # type: ignore[reportArgumentType]
            total_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO"] == "1"]["total_candidatos"].sum())  # type: ignore[reportArgumentType]
            total_nao_treineiros = int(df_kpi_uf[df_kpi_uf["IN_TREINEIRO"] == "0"]["total_candidatos"].sum())  # type: ignore[reportArgumentType]
        else:
            df_kpi_filtered = df_kpi_uf
            total_inscritos = int(df_kpi_uf["total_candidatos"].sum())  # type: ignore[reportArgumentType]
            total_treineiros = 0
            total_nao_treineiros = total_inscritos
            
        uf_totals = df_kpi_filtered.groupby("SG_UF_PROVA")["total_candidatos"].sum()  # type: ignore[reportAttributeAccessIssue]
        top_uf: str = str(uf_totals.idxmax()) if not uf_totals.empty else (selected_ufs[0] if selected_ufs else "SP")  # type: ignore[reportAttributeAccessIssue]
    else:
        total_inscritos = int(df_rede["total_candidatos"].sum()) if not df_rede.empty else len(filtered_df)  # type: ignore[reportArgumentType]
        total_treineiros = int(filtered_df[filtered_df["IN_TREINEIRO"] == "1"].shape[0]) if not filtered_df.empty and "IN_TREINEIRO" in filtered_df.columns else 0
        total_nao_treineiros = int(filtered_df[filtered_df["IN_TREINEIRO"] == "0"].shape[0]) if not filtered_df.empty and "IN_TREINEIRO" in filtered_df.columns else total_inscritos
        top_uf = str(filtered_df["SG_UF_PROVA"].value_counts().idxmax()) if not filtered_df.empty and "SG_UF_PROVA" in filtered_df.columns else (selected_ufs[0] if selected_ufs else "SP")  # type: ignore[reportAttributeAccessIssue]

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
    if menu_opcao == "📊 Panorama Geográfico":
        render_geo_view(selected_ufs, selected_treineiro_labels, selected_treineiro_values, df_notas_uf, df_demografia, filtered_df)

    elif menu_opcao == "💰 Perfil Socioeconômico":
        render_socio_view(df_notas_renda, selected_treineiro_labels, selected_treineiro_values, filtered_df)

    elif menu_opcao == "🏫 Redes de Ensino":
        render_rede_view(selected_year, selected_ufs, df_rede, df_rede_plurianual, df_socio_escola, COLOR_MAP_REDE)

    elif menu_opcao == "📈 Desempenho TRI":
        render_desempenho_view(selected_year, selected_ufs, df_notas_uf)

    elif menu_opcao == "🤖 Machine Learning":
        render_ml_view(ml_insights)

    elif menu_opcao == "🌎 Geopolítica":
        render_geopolitica_view(df_notas_uf, df_rede_plurianual)

    elif menu_opcao == "🎓 Conclusão Estratégica":
        render_conclusao_estrategica()

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>Desenvolvido com PySpark, Streamlit & Plotly — Projeto Integrador PI4 Univesp</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Erro Crítico na Execução do Painel")
    st.exception(e)