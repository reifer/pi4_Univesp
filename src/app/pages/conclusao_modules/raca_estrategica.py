import streamlit as st
import pandas as pd
import os
import plotly.express as px

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
    
    anos_opcoes_f3_raca = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f3_raca = st.selectbox(
        "Selecione o recorte temporal para a análise de Renda x Raça:",
        anos_opcoes_f3_raca,
        key="fase_raca_ano_select"
    )
    
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
    
    def carregar_dados_renda_raca(ano):
        caminho_pasta = f"data/processed/enem_{ano}_agg_renda_raca_parquet"
        if os.path.exists(caminho_pasta):
            try:
                df = pd.read_parquet(caminho_pasta)
                df["NU_ANO"] = int(ano)
                return df
            except Exception as e:
                return pd.DataFrame()
        return pd.DataFrame()

    if ano_f3_raca == "Plurianual (2021-2025)":
        with st.container(border=True):
            st.markdown("<strong>📊 Visão Plurianual da Intersecção Renda x Raça (2021–2025):</strong>", unsafe_allow_html=True)
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>O "Efeito Raça" na Desigualdade:</strong> A análise plurianual comprova que as disparidades de desempenho não se explicam exclusivamente pela classe social. Mesmo dentro de uma mesma faixa macro de renda, persistem assimetrias notáveis entre candidatos de diferentes grupos étnico-raciais.</li>
            </ul>
            """, unsafe_allow_html=True)
        
        dfs_pluri_raca = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_renda_raca(a)
            if not df_temp.empty:
                dfs_pluri_raca.append(df_temp)
                
        if dfs_pluri_raca:
            df_pluri_raca_total = pd.concat(dfs_pluri_raca, ignore_index=True)
            if "RENDA_FAMILIAR_DESC" in df_pluri_raca_total.columns and "TP_COR_RACA_DESC" in df_pluri_raca_total.columns:
                df_pluri_raca_total["MACRO_RENDA"] = df_pluri_raca_total["RENDA_FAMILIAR_DESC"].apply(_agrupar_faixas_renda_macro)
                df_agrupado = df_pluri_raca_total.groupby(["MACRO_RENDA", "TP_COR_RACA_DESC"])["media_mt"].mean().reset_index()
                
                with st.container(border=True):
                    fig_raca_pluri = px.bar(
                        df_agrupado,
                        x="MACRO_RENDA", y="media_mt", color="TP_COR_RACA_DESC", barmode="group",
                        title="Média Plurianual de Matemática por Bloco Macro de Renda e Raça/Cor",
                        labels={"MACRO_RENDA": "Bloco Macro de Renda Familiar", "media_mt": "Nota Média Matemática", "TP_COR_RACA_DESC": "Raça / Cor"}
                    )
                    fig_raca_pluri.update_layout(
                        template="plotly_white", 
                        height=450, 
                        margin=dict(l=20, r=20, t=50, b=20),
                        xaxis=dict(tickangle=-15, tickfont=dict(size=11), automargin=True),
                        legend_title="Raça / Cor"
                    )
                    st.plotly_chart(fig_raca_pluri, use_container_width=True)
    else:
        df_raca_ano = carregar_dados_renda_raca(ano_f3_raca)
        if not df_raca_ano.empty:
            st.success(f"✅ Dados agregados de Renda x Raça carregados com sucesso para o ENEM {ano_f3_raca}.")
            
            metrica_raca = st.selectbox(
                "Métrica de Desempenho:",
                options=["media_mt", "media_redacao", "media_cn", "media_ch", "media_lc"],
                format_func=lambda x: {
                    "media_mt": "Matemática",
                    "media_redacao": "Redação",
                    "media_cn": "Ciências da Natureza",
                    "media_ch": "Ciências Humanas",
                    "media_lc": "Linguagens e Códigos"
                }[x],
                key=f"select_metrica_raca_{ano_f3_raca}"
            )
            
            if "RENDA_FAMILIAR_DESC" in df_raca_ano.columns and "TP_COR_RACA_DESC" in df_raca_ano.columns:
                df_raca_ano["MACRO_RENDA"] = df_raca_ano["RENDA_FAMILIAR_DESC"].apply(_agrupar_faixas_renda_macro)
                df_agrupado_ano = df_raca_ano.groupby(["MACRO_RENDA", "TP_COR_RACA_DESC"])[metrica_raca].mean().reset_index()
                
                with st.container(border=True):
                    fig_raca_ano = px.bar(
                        df_agrupado_ano,
                        x="MACRO_RENDA", y=metrica_raca, color="TP_COR_RACA_DESC",
                        barmode="group",
                        title=f"Desempenho por Bloco Macro de Renda segmentado por Raça/Cor — ENEM {ano_f3_raca}",
                        labels={"MACRO_RENDA": "Bloco Macro de Renda Familiar", metrica_raca: "Nota Média TRI", "TP_COR_RACA_DESC": "Raça / Cor"}
                    )
                    fig_raca_ano.update_layout(
                        template="plotly_white", 
                        height=450, 
                        margin=dict(l=20, r=20, t=50, b=20),
                        xaxis=dict(tickangle=-15, tickfont=dict(size=11), automargin=True),
                        legend_title="Raça / Cor"
                    )
                    st.plotly_chart(fig_raca_ano, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados de Renda x Raça para o ano {ano_f3_raca} não encontrados na pasta de processados.")

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