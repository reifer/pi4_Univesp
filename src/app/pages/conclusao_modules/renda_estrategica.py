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
                tem_codigo_renda = "RENDA_FAMILIAR_COD" in df_pluri_renda.columns
                coluna_faixa = "RENDA_FAMILIAR_COD" if tem_codigo_renda else "RENDA_FAMILIAR_DESC"
                df_pluri_renda[coluna_faixa] = df_pluri_renda[coluna_faixa].astype("string")
                opcoes_faixas = sorted(df_pluri_renda[coluna_faixa].dropna().unique().tolist())
                rotulos_faixas = (
                    df_pluri_renda.sort_values("NU_ANO", ascending=False)
                    .drop_duplicates(coluna_faixa)
                    .set_index(coluna_faixa)["RENDA_FAMILIAR_DESC"]
                    .astype(str)
                    .to_dict()
                )
                indices_iniciais = (
                    sorted({0, len(opcoes_faixas) // 2, len(opcoes_faixas) - 1})
                    if opcoes_faixas
                    else []
                )
                faixas_iniciais = [opcoes_faixas[indice] for indice in indices_iniciais]
                faixas_selecionadas = st.multiselect(
                    "Faixas de renda para comparar:",
                    options=opcoes_faixas,
                    default=faixas_iniciais,
                    format_func=lambda faixa: rotulos_faixas.get(faixa, faixa),
                    help="As opções iniciais mostram faixas baixa, intermediária e alta. Selecione poucas faixas para manter o gráfico legível no celular.",
                    key="fase2_faixas_renda_plurianual",
                )

                if faixas_selecionadas:
                    df_grafico_renda = df_pluri_renda[
                        df_pluri_renda[coluna_faixa].isin(faixas_selecionadas)
                    ].copy()
                    chaves_agrupamento = ["NU_ANO", coluna_faixa]
                    agregacoes: dict[str, tuple[str, str]] = {}
                    if "total_candidatos" in df_grafico_renda.columns:
                        agregacoes["total_candidatos"] = ("total_candidatos", "sum")
                    if "media_geral" in df_grafico_renda.columns:
                        if "total_candidatos" in df_grafico_renda.columns:
                            df_grafico_renda["_media_ponderada"] = (
                                df_grafico_renda["media_geral"] * df_grafico_renda["total_candidatos"]
                            )
                            agregacoes["_media_ponderada"] = ("_media_ponderada", "sum")
                        else:
                            agregacoes["media_geral"] = ("media_geral", "mean")

                    if agregacoes:
                        df_grafico_renda = (
                            df_grafico_renda.groupby(chaves_agrupamento, as_index=False)
                            .agg(**agregacoes)
                        )
                        if "_media_ponderada" in df_grafico_renda.columns:
                            df_grafico_renda["media_geral"] = (
                                df_grafico_renda["_media_ponderada"]
                                .div(df_grafico_renda["total_candidatos"])
                                .where(df_grafico_renda["total_candidatos"] != 0)
                            )
                            df_grafico_renda = df_grafico_renda.drop(columns="_media_ponderada")

                    metrica_pluri = "media_geral" if "media_geral" in df_grafico_renda.columns else "total_candidatos"
                    rotulo_metrica_pluri = "Média Geral TRI" if metrica_pluri == "media_geral" else "Total de Candidatos"
                    df_grafico_renda["Faixa de Renda"] = df_grafico_renda[coluna_faixa].map(rotulos_faixas)
                    with st.container(border=True):
                        fig_hist = px.line(
                            df_grafico_renda,
                            x="NU_ANO",
                            y=metrica_pluri,
                            color="Faixa de Renda",
                            markers=True,
                            title="Evolução Plurianual do Desempenho por Faixa de Renda",
                            labels={
                                "NU_ANO": "Ano do Exame",
                                metrica_pluri: rotulo_metrica_pluri,
                                "Faixa de Renda": "Faixa de Renda Familiar",
                            },
                            hover_data={coluna_faixa: True},
                        )
                        fig_hist.update_layout(
                            template="plotly_white",
                            height=400,
                            margin=dict(l=20, r=15, t=60, b=100),
                            legend=dict(
                                orientation="h",
                                y=-0.22,
                                x=0.5,
                                xanchor="center",
                                yanchor="top",
                                font=dict(size=9),
                            ),
                        )
                        st.plotly_chart(fig_hist, width="stretch")
                else:
                    st.info("Selecione ao menos uma faixa de renda para exibir a comparação.")
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