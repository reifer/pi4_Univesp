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

AVAILABLE_YEARS = [2021, 2022, 2023, 2024, 2025]
TREINEIRO_LABELS = ["Não Treineiro", "Treineiro"]


def _apply_year_preset() -> None:
    preset = st.session_state["year_preset"]
    if preset == "Ano mais recente":
        st.session_state["filter_years"] = [AVAILABLE_YEARS[-1]]
    elif preset == "Série completa":
        st.session_state["filter_years"] = AVAILABLE_YEARS.copy()


def _mark_years_as_custom() -> None:
    st.session_state["year_preset"] = "Personalizado"


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

    st.session_state.setdefault("year_preset", "Ano mais recente")
    st.session_state.setdefault("filter_years", [AVAILABLE_YEARS[-1]])
    year_preset_col, years_col = st.columns([1, 1])
    with year_preset_col:
        st.segmented_control(
            "Recorte temporal",
            options=["Ano mais recente", "Série completa", "Personalizado"],
            key="year_preset",
            on_change=_apply_year_preset,
        )
    with years_col:
        st.multiselect(
            "Anos do ENEM",
            options=AVAILABLE_YEARS,
            key="filter_years",
            on_change=_mark_years_as_custom,
        )

    selected_years = tuple(st.session_state["filter_years"])
    if not selected_years:
        st.warning("Selecione pelo menos um ano do ENEM.")
        st.stop()

    dashboard_data = load_data(selected_years)
    df_notas_uf = dashboard_data["df_notas_uf"]
    df_notas_renda = dashboard_data["df_notas_renda"]
    df_rede = dashboard_data["df_rede"]
    df_rede_plurianual = dashboard_data["df_rede_plurianual"]
    df_socio_escola = dashboard_data["df_socio_escola"]
    df_demografia = dashboard_data["df_demografia"]
    ml_insights = dashboard_data["ml_insights"]
    df_renda_raca = dashboard_data["df_renda_raca"]
    selected_year = ", ".join(str(year) for year in selected_years)

    all_ufs = sorted(df_notas_uf["SG_UF_PROVA"].dropna().unique().tolist())
    st.session_state.setdefault("filter_ufs", all_ufs)
    st.session_state["filter_ufs"] = [
        uf for uf in st.session_state["filter_ufs"] if uf in all_ufs
    ]
    st.session_state.setdefault("filter_treineiro", TREINEIRO_LABELS.copy())

    col_ufs, col_treineiro = st.columns([3, 2])
    with col_ufs:
        st.multiselect(
            "📍 Selecione as UFs (Estados)",
            options=all_ufs,
            key="filter_ufs",
        )
    with col_treineiro:
        st.pills(
            "👤 Tipo de candidato",
            options=TREINEIRO_LABELS,
            selection_mode="multi",
            key="filter_treineiro",
        )

    selected_ufs = st.session_state["filter_ufs"]
    selected_treineiro_labels = st.session_state["filter_treineiro"]
    selected_treineiro_values = [
        "1" if label == "Treineiro" else "0"
        for label in selected_treineiro_labels
    ]

    st.markdown("---")
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
    menu_opcao: str = st.pills(
        "Módulos de Análise",
        options=modulos_disponiveis,
        default="📊 Panorama Geográfico",
        key="module_selection",
        label_visibility="collapsed"
    ) or "📊 Panorama Geográfico"

    st.markdown("---")
    if not selected_ufs or not selected_treineiro_labels:
        st.warning("⚠️ Selecione pelo menos um Estado e um Tipo de Candidato nos filtros acima.")
        st.stop()

    filtered_df = pd.DataFrame()

    # --- CARDS KPI GERAIS DO TOPO ---
    c1, c2, c3, c4 = st.columns(4)
    df_kpi_uf = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)]
    df_kpi_filtered = df_kpi_uf[
        df_kpi_uf["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)
    ]
    total_inscritos = int(df_kpi_filtered["total_candidatos"].sum())
    total_treineiros = int(
        df_kpi_uf.loc[
            df_kpi_uf["IN_TREINEIRO_DESC"] == "Treineiro", "total_candidatos"
        ].sum()
    )
    total_nao_treineiros = int(
        df_kpi_uf.loc[
            df_kpi_uf["IN_TREINEIRO_DESC"] == "Não Treineiro", "total_candidatos"
        ].sum()
    )
    uf_totals = df_kpi_filtered.groupby("SG_UF_PROVA")["total_candidatos"].sum()
    top_uf = str(uf_totals.idxmax()) if not uf_totals.empty else selected_ufs[0]

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
        render_geo_view(
            selected_ufs,
            selected_treineiro_labels,
            selected_treineiro_values,
            df_notas_uf,
            df_demografia,
            filtered_df,
            selected_years,
        )

    elif menu_opcao == "💰 Perfil Socioeconômico":
        render_socio_view(
            df_notas_renda,
            selected_treineiro_labels,
            selected_treineiro_values,
            filtered_df,
            selected_years,
            selected_ufs,
        )

    elif menu_opcao == "🏫 Redes de Ensino":
        render_rede_view(
            selected_year,
            selected_ufs,
            df_rede,
            df_rede_plurianual,
            df_socio_escola,
            COLOR_MAP_REDE,
            selected_years,
            selected_treineiro_labels,
        )

    elif menu_opcao == "📈 Desempenho TRI":
        render_desempenho_view(
            selected_year,
            selected_ufs,
            df_notas_uf,
            selected_years,
            selected_treineiro_labels,
        )

    elif menu_opcao == "🤖 Machine Learning":
        render_ml_view(ml_insights, selected_years)

    elif menu_opcao == "🌎 Geopolítica":
        render_geopolitica_view(
            df_notas_uf,
            df_rede_plurianual,
            selected_years,
            selected_ufs,
            selected_treineiro_labels,
        )

    elif menu_opcao == "🎓 Conclusão Estratégica":
        render_conclusao_estrategica()

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>Desenvolvido com PySpark, Streamlit & Plotly — Projeto Integrador PI4 Univesp</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("Erro Crítico na Execução do Painel")
    st.exception(e)