import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils.data_loader import get_global_filter_state, load_filtered_aggregate

def _agrupar_faixas_renda_macro(texto_renda):
    if not isinstance(texto_renda, str):
        return "Não Informado"
    t = texto_renda.lower()
    if any(k in t for k in ["nenhuma renda", "até r$ 1.100", "até r$ 1.320", "até r$ 1.650", "até r$ 2.200", "de r$ 1.", "de r$ 2."]):
        if any(k in t for k in ["de r$ 6.", "de r$ 7.", "de r$ 8.", "de r$ 9.", "de r$ 10."]):
            return "3. Classe Média (R$ 6k a R$ 12k)"
        return "1. Baixa Renda (Até ~R$ 3.300)"
    elif any(k in t for k in ["de r$ 3.", "de r$ 4.", "de r$ 5."]):
        return "2. Média-Baixa (R$ 3,3k a R$ 6k)"
    elif any(k in t for k in ["de r$ 6.", "de r$ 7.", "de r$ 8.", "de r$ 9.", "de r$ 10.", "de r$ 11.", "de r$ 12."]):
        return "3. Classe Média (R$ 6k a R$ 12k)"
    elif any(k in t for k in ["de r$ 13.", "de r$ 14.", "de r$ 15.", "de r$ 16.", "de r$ 18.", "de r$ 19.", "acima de r$ 1"]) or "acima de r$ 2" in t or "acima de r$ 1" in t:
        if "acima de r$ 22" in t or "acima de r$ 26" in t or "acima de r$ 18" in t or "acima de r$ 20" in t:
            return "5. Alta Renda (> R$ 20k)"
        return "4. Média-Alta (R$ 12k a R$ 20k)"
    elif "acima" in t:
        return "5. Alta Renda (> R$ 20k)"
    return "Outros / Não Informado"

def render():
    st.markdown("---")
    
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
        st.markdown("### ⚖️ 3. A Intersecção Estrutural: Renda Familiar x Raça/Cor e Desempenho")
    
    years, ufs, treineiros = get_global_filter_state()
    
    with st.expander("📖 Nota Metodológica: Consolidação das Faixas de Renda (Agrupamento Macro)", expanded=False):
        with st.container(border=True):
            st.markdown("""
            Para garantir a clareza analítica e evitar a poluição visual gerada pelas mais de 15 divisões granulares originais do questionário socioeconômico do ENEM (Q006), as faixas nominais foram agrupadas em **5 Blocos Macro de Renda**:
            * **1. Baixa Renda (Até ~R$ 3.300):** Engloba desde candidatos sem renda declarada até famílias com rendimento de aproximadamente 2,5 salários mínimos.
            * **2. Média-Baixa (R$ 3,3k a R$ 6k):** Faixas intermediárias iniciais de rendimento familiar.
            * **3. Classe Média (R$ 6k a R$ 12k):** Estrato central correspondente às classes médias tradicionais.
            * **4. Média-Alta (R$ 12k a R$ 20k):** Faixas de rendimento superior correspondentes às classes média-altas.
            * **5. Alta Renda (> R$ 20k):** Faixas de topo da pirâmide socioeconômica declarada e rendimentos superiores.
            """)
    
    df_raca = load_filtered_aggregate("agg_renda_raca")
    ano_label = ", ".join(map(str, years))
    if len(years) > 1:
        with st.container(border=True):
            st.markdown("<strong>📊 Visão Plurianual da Intersecção Renda x Raça (2021–2025):</strong>", unsafe_allow_html=True)
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>O "Efeito Raça" na Desigualdade:</strong> A análise plurianual comprova que as disparidades de desempenho não se explicam exclusivamente pela classe social. Mesmo dentro de uma mesma faixa macro de renda, persistem assimetrias notáveis entre candidatos de diferentes grupos étnico-raciais.</li>
            </ul>
            """, unsafe_allow_html=True)
        
        if not df_raca.empty:
            df_pluri_raca_total = df_raca.copy()
            if "RENDA_FAMILIAR_DESC" in df_pluri_raca_total.columns and "TP_COR_RACA_DESC" in df_pluri_raca_total.columns:
                df_pluri_raca_total["MACRO_RENDA"] = df_pluri_raca_total["RENDA_FAMILIAR_DESC"].apply(_agrupar_faixas_renda_macro)
                df_agrupado = (
                    df_pluri_raca_total.groupby(
                        ["MACRO_RENDA", "TP_COR_RACA_DESC"], as_index=False
                    )
                    .agg(
                        soma_notas_mt=("soma_notas_mt", "sum"),
                        total_notas_mt=("total_notas_mt", "sum"),
                    )
                )
                df_agrupado["media_mt"] = (
                    df_agrupado["soma_notas_mt"]
                    .div(df_agrupado["total_notas_mt"])
                    .where(df_agrupado["total_notas_mt"] > 0)
                )
                df_agrupado = df_agrupado.dropna(subset=["media_mt"])
                df_agrupado["percentual_media_mt"] = (
                    df_agrupado["media_mt"]
                    .div(
                        df_agrupado.groupby("MACRO_RENDA")["media_mt"].transform("sum")
                    )
                    .mul(100)
                )
                with st.container(border=True):
                    fig_raca_pluri = px.bar(
                        df_agrupado,
                        x="percentual_media_mt",
                        y="MACRO_RENDA",
                        color="TP_COR_RACA_DESC",
                        custom_data=["media_mt"],
                        barmode="stack",
                        orientation="h",
                        title="Distribuição Proporcional da Média Plurianual de Matemática por Bloco Macro de Renda e Raça/Cor",
                        labels={
                            "MACRO_RENDA": "Bloco Macro de Renda Familiar",
                            "percentual_media_mt": "Proporção da média de Matemática",
                            "TP_COR_RACA_DESC": "Raça / Cor",
                        },
                    )
                    fig_raca_pluri.update_traces(
                        hovertemplate=(
                            "Raça / Cor: %{fullData.name}<br>"
                            "Proporção da média no bloco: %{x:.1f}%<br>"
                            "Nota média de Matemática: %{customdata[0]:.1f}"
                            "<extra></extra>"
                        )
                    )
                    fig_raca_pluri.update_layout(
                        template="plotly_white", 
                        height=500,
                        margin=dict(l=20, r=15, t=60, b=120),
                        yaxis=dict(tickfont=dict(size=10), automargin=True),
                        xaxis=dict(range=[0, 100], ticksuffix="%", automargin=True),
                        legend=dict(
                            title_text="Raça / Cor",
                            orientation="h",
                            y=-0.3,
                            x=0.5,
                            xanchor="center",
                            yanchor="top",
                            font=dict(size=10),
                        ),
                    )
                    st.plotly_chart(fig_raca_pluri, width="stretch")
    elif not df_raca.empty:
        df_raca_ano = df_raca.copy()
        if not df_raca_ano.empty:
            st.success(f"✅ Dados agregados de Renda x Raça carregados para ENEM {ano_label}.")
            
            metrica_raca: str = st.selectbox(  # type: ignore[assignment]
                "Métrica de Desempenho:",
                options=["media_mt", "media_redacao", "media_cn", "media_ch", "media_lc"],
                format_func=lambda x: {
                    "media_mt": "Matemática",
                    "media_redacao": "Redação",
                    "media_cn": "Ciências da Natureza",
                    "media_ch": "Ciências Humanas",
                    "media_lc": "Linguagens e Códigos"
                }[x],
                key="select_metrica_raca"
            ) or "media_mt"
            
            if "RENDA_FAMILIAR_DESC" in df_raca_ano.columns and "TP_COR_RACA_DESC" in df_raca_ano.columns:
                df_raca_ano["MACRO_RENDA"] = df_raca_ano["RENDA_FAMILIAR_DESC"].apply(_agrupar_faixas_renda_macro)
                metric_suffix = {
                    "media_mt": "mt",
                    "media_redacao": "redacao",
                    "media_cn": "cn",
                    "media_ch": "ch",
                    "media_lc": "lc",
                }[metrica_raca]
                df_agrupado_ano = (
                    df_raca_ano.groupby(
                        ["MACRO_RENDA", "TP_COR_RACA_DESC"], as_index=False
                    )
                    .agg(
                        _score_sum=(f"soma_notas_{metric_suffix}", "sum"),
                        _score_count=(f"total_notas_{metric_suffix}", "sum"),
                    )
                )
                df_agrupado_ano[metrica_raca] = (
                    df_agrupado_ano["_score_sum"]
                    .div(df_agrupado_ano["_score_count"])
                    .where(df_agrupado_ano["_score_count"] > 0)
                )
                
                with st.container(border=True):
                    fig_raca_ano = px.bar(
                        df_agrupado_ano,
                        x="MACRO_RENDA", y=metrica_raca, color="TP_COR_RACA_DESC",
                        barmode="group",
                        title=f"Desempenho por Bloco Macro de Renda segmentado por Raça/Cor — ENEM {ano_label}",
                        labels={"MACRO_RENDA": "Bloco Macro de Renda Familiar", metrica_raca: "Nota Média TRI", "TP_COR_RACA_DESC": "Raça / Cor"}
                    )
                    fig_raca_ano.update_layout(
                        template="plotly_white", 
                        height=450, 
                        margin=dict(l=20, r=20, t=50, b=20),
                        xaxis=dict(tickangle=-15, tickfont=dict(size=11), automargin=True),
                        legend_title="Raça / Cor"
                    )
                    st.plotly_chart(fig_raca_ano, width="stretch")
    else:
        st.info("Não há dados de renda e raça para os filtros globais atuais.")

    # Containers laterais estruturados com bordas nativas
    col_critica_f3_raca, col_proposta_f3_raca = st.columns(2)
    with col_critica_f3_raca:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica da Intersecção Étnico-Racial")
            st.markdown("""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            O cruzamento revela que as barreiras estruturais afetam de maneira desproporcional candidatos negros e pardos, cujas notas médias muitas vezes ficam abaixo de candidatos brancos mesmo quando situados no <strong>mesmo bloco macro de renda</strong>. Isso evidencia que o capital econômico por si só não neutraliza as desigualdades de oportunidades educacionais decorrentes de vieses sistêmicos e históricos.
            </p>
            """, unsafe_allow_html=True)
        
    with col_proposta_f3_raca:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Fortalecimento e Aprimoramento de Ações Afirmativas:</strong> Manutenção e ampliação de políticas de cotas raciais e sociais nas universidades federais como ferramenta indispensável de justiça distributiva.</li>
                <li><strong>Programas de Tutoria Afirmativa Escolar:</strong> Fomento a políticas públicas voltadas à equidade racial nos ensinos fundamentais e médio das redes públicas.</li>
            </ul>
            """, unsafe_allow_html=True)