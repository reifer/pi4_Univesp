import streamlit as st
import pandas as pd
import os
import plotly.express as px

def render():
    st.markdown("---")
    
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
        st.markdown("### 💰 2. A Renda e a Nota: O Fator Socioeconômico e o Impacto no TRI")
    
    anos_opcoes_f2 = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f2 = st.selectbox(
        "Selecione o recorte temporal para a análise de Renda Familiar:",
        anos_opcoes_f2,
        key="fase2_ano_select"
    )
    
    def carregar_dados_renda(ano):
        caminho_pasta = f"data/processed/enem_{ano}_agg_notas_renda_parquet"
        if os.path.exists(caminho_pasta):
            try:
                df = pd.read_parquet(caminho_pasta)
                df["NU_ANO"] = int(ano)
                return df
            except Exception as e:
                return pd.DataFrame()
        return pd.DataFrame()

    if ano_f2 == "Plurianual (2021-2025)":
        with st.container(border=True):
            st.markdown("<strong>📊 Visão Plurianual do Fator Socioeconômico (2021–2025):</strong>", unsafe_allow_html=True)
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>A Correlação Direta:</strong> A análise consolidada dos 5 anos comprova que a renda familiar (<code>Q006</code>) opera como uma das variáveis de maior poder preditivo sobre o desempenho no ENEM. O gradiente de notas da TRI cresce de forma estritamente proporcional ao patamar de rendimento declarado.</li>
            </ul>
            """, unsafe_allow_html=True)
        
        dfs_pluri = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_renda(a)
            if not df_temp.empty:
                dfs_pluri.append(df_temp)
                
        if dfs_pluri:
            df_pluri_renda = pd.concat(dfs_pluri, ignore_index=True)
            
            if "RENDA_FAMILIAR_DESC" in df_pluri_renda.columns and "NU_ANO" in df_pluri_renda.columns:
                with st.container(border=True):
                    fig_hist = px.line(
                        df_pluri_renda, x="NU_ANO", y="media_geral" if "media_geral" in df_pluri_renda.columns else "total_candidatos",
                        color="RENDA_FAMILIAR_DESC", markers=True,
                        title="Evolução Plurianual do Desempenho por Faixa de Renda",
                        labels={"NU_ANO": "Ano do Exame", "media_geral": "Média Geral TRI"}
                    )
                    fig_hist.update_layout(
                        template="plotly_white", 
                        height=420,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
    else:
        df_renda_ano = carregar_dados_renda(ano_f2)
        if not df_renda_ano.empty:
            st.success(f"✅ Dados agregados de renda carregados com sucesso para o ENEM {ano_f2}.")
            
            desc_col: str | None = "RENDA_FAMILIAR_DESC" if "RENDA_FAMILIAR_DESC" in df_renda_ano.columns else (str(df_renda_ano.columns[1]) if len(df_renda_ano.columns) > 1 else None)
            nota_col: str | None = "media_mt" if "media_mt" in df_renda_ano.columns else (str(df_renda_ano.columns[2]) if len(df_renda_ano.columns) > 2 else None)
            
            if desc_col is not None and nota_col is not None:
                with st.container(border=True):
                    fig_renda_ano = px.bar(
                        df_renda_ano.sort_values(by=desc_col),
                        x=desc_col, y=nota_col,
                        color=nota_col, color_continuous_scale="Blues",
                        title=f"Desempenho Médio em Matemática por Faixa de Renda — ENEM {ano_f2}",
                        labels={desc_col: "Faixa de Renda Familiar (Q006)", nota_col: "Nota Média (TRI)"}
                    )
                    fig_renda_ano.update_layout(
                        template="plotly_white", 
                        height=420, 
                        coloraxis_showscale=False,
                        margin=dict(l=20, r=20, t=50, b=20),
                        xaxis=dict(tickangle=-30, tickfont=dict(size=10), automargin=True)
                    )
                    st.plotly_chart(fig_renda_ano, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados de renda para o ano {ano_f2} não encontrados na pasta de processados.")

    # Colunas finais estruturadas com Containers Nativos
    col_critica_f2, col_proposta_f2 = st.columns(2)
    with col_critica_f2:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica do Fator Socioeconômico")
            st.markdown("""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            A dependência entre o capital econômico familiar e o sucesso acadêmico escancara a <strong>reprodutibilidade das desigualdades sociais</strong>. Alunos inseridos nas faixas de menor renda enfrentam barreiras materiais cumulativas, como a necessidade precoce de inserção no mercado de trabalho (<code>Q007</code>), o que reduz drasticamente o tempo dedicado aos estudos extracurriculares.
            </p>
            """, unsafe_allow_html=True)
        
    with col_proposta_f2:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Políticas de Assistência Estudantil Ampliadas:</strong> Bolsas de permanência e suporte digital direto para estudantes de baixa renda do ensino médio regular.</li>
                <li><strong>Plataformas Públicas de Apoio Adaptativo:</strong> Democratização de cursinhos preparatórios de alto nível impulsionados por Inteligência Artificial para nivelamento de oportunidades.</li>
            </ul>
            """, unsafe_allow_html=True)