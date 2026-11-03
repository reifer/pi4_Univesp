import streamlit as st
import pandas as pd
import plotly.express as px
import textwrap
from app.utils.data_loader import get_global_filter_state, load_filtered_aggregate

def render():
    st.markdown("---")
    
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
        st.markdown("### 🛠️ 4. A Infraestrutura e o Trabalho: O Peso da Jornada e do Apoio Escolar")
    
    selected_years, selected_ufs, selected_treineiros = get_global_filter_state()
    df_pluri_socio = load_filtered_aggregate("agg_socio_escola")
    year_label = ", ".join(map(str, selected_years))
    st.caption(
        f"Filtros globais — ENEM {year_label}; UFs {', '.join(selected_ufs)}; "
        f"candidatos {', '.join(selected_treineiros)}."
    )

    if len(selected_years) > 1:
        with st.container(border=True):
            st.markdown("<strong>📊 Visão Plurianual de Infraestrutura e Condições de Trabalho (2021–2025):</strong>", unsafe_allow_html=True)
            st.markdown("""
            A média ponderada da TRI em Matemática é a soma das notas válidas dividida pela quantidade dessas notas, para que cada candidato com nota tenha o mesmo peso. A TRI não é porcentagem de acertos: considera também a dificuldade e a coerência do padrão de respostas.
            """, unsafe_allow_html=True)
        
        if not df_pluri_socio.empty:
            if "Q007_DESC" in df_pluri_socio.columns and "media_matematica" in df_pluri_socio.columns:
                df_pluri_socio["Q007_DESC"] = (
                    df_pluri_socio["Q007_DESC"]
                    .astype("string")
                    .str.strip()
                    .str.rstrip(".")
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
                )
                df_pluri_socio = df_pluri_socio.dropna(subset=["Q007_DESC", "NU_ANO", "media_matematica"])
                descricao_condicao = df_pluri_socio["Q007_DESC"].str.casefold()
                de_para_condicoes = {
                    "não": "nao_trabalha",
                    "não informado": "nao_informado",
                    "sim": "trabalha_frequencia_nao_informada",
                    "sim, um ou dois dias por semana": "trabalha_1_2_dias",
                    "sim, três ou quatro dias por semana": "trabalha_3_4_dias",
                    "sim, pelo menos cinco dias por semana": "trabalha_5_mais_dias",
                }
                df_pluri_socio["_condicao_chave"] = descricao_condicao.map(
                    de_para_condicoes
                ).fillna(descricao_condicao)
                rotulos_condicoes = {
                    "nao_trabalha": "Não trabalha",
                    "nao_informado": "Não informado",
                    "trabalha_frequencia_nao_informada": "Trabalha (frequência não informada)",
                    "trabalha_1_2_dias": "1–2 dias por semana",
                    "trabalha_3_4_dias": "3–4 dias por semana",
                    "trabalha_5_mais_dias": "5+ dias por semana",
                }
                ordem_condicoes = [
                    "nao_trabalha",
                    "trabalha_1_2_dias",
                    "trabalha_3_4_dias",
                    "trabalha_5_mais_dias",
                    "trabalha_frequencia_nao_informada",
                    "nao_informado",
                ]
                anos_disponiveis = sorted(df_pluri_socio["NU_ANO"].astype(int).unique().tolist())
                ano_trabalho = st.selectbox(
                    "Ano dentro do recorte global:",
                    options=anos_disponiveis,
                    index=len(anos_disponiveis) - 1,
                    key="fase4_ano_trabalho_plurianual",
                )
                df_ano_trabalho = df_pluri_socio[
                    df_pluri_socio["NU_ANO"].astype(int) == ano_trabalho
                ].copy()
                if "TP_DEPENDENCIA_ADM_ESC_DESC" in df_ano_trabalho.columns:
                    df_ano_trabalho["TP_DEPENDENCIA_ADM_ESC_DESC"] = (
                        df_ano_trabalho["TP_DEPENDENCIA_ADM_ESC_DESC"]
                        .astype("string")
                        .str.strip()
                    )
                    opcoes_rede = [
                        "Todas as redes",
                        "Pública (estadual, federal e municipal)",
                        "Privada",
                        "Não informada",
                    ]
                    rede_trabalho = st.selectbox(
                        "Recorte por dependência administrativa:",
                        options=opcoes_rede,
                        key=f"fase4_rede_trabalho_{ano_trabalho}",
                    )
                    total_ano = df_ano_trabalho["total_candidatos"].sum()
                    total_rede_nao_informada = df_ano_trabalho.loc[
                        df_ano_trabalho["TP_DEPENDENCIA_ADM_ESC_DESC"] == "Não Informado",
                        "total_candidatos",
                    ].sum()
                    percentual_rede_nao_informada = (
                        total_rede_nao_informada / total_ano if total_ano > 0 else 0
                    )
                    st.warning(
                        f"Leitura descritiva, não causal: a média inclui somente candidatos "
                        f"com nota válida e não ajusta simultaneamente renda, idade ou comparecimento. "
                        f"Neste ano, a rede escolar não está informada para "
                        f"{percentual_rede_nao_informada:.1%} dos registros; os recortes por rede "
                        "abrangem apenas os registros classificados. "
                        + (
                            "A resposta informa a frequência semanal de trabalho."
                            if ano_trabalho <= 2023
                            else "A resposta é apenas Sim/Não e não informa frequência ou horas trabalhadas."
                        )
                    )
                    if rede_trabalho == "Pública (estadual, federal e municipal)":
                        df_ano_trabalho = df_ano_trabalho[
                            df_ano_trabalho["TP_DEPENDENCIA_ADM_ESC_DESC"].isin(
                                ["Estadual", "Federal", "Municipal"]
                            )
                        ].copy()
                    elif rede_trabalho == "Privada":
                        df_ano_trabalho = df_ano_trabalho[
                            df_ano_trabalho["TP_DEPENDENCIA_ADM_ESC_DESC"] == "Privada"
                        ].copy()
                    elif rede_trabalho == "Não informada":
                        df_ano_trabalho = df_ano_trabalho[
                            df_ano_trabalho["TP_DEPENDENCIA_ADM_ESC_DESC"] == "Não Informado"
                        ].copy()
                else:
                    rede_trabalho = "Todas as redes"
                    st.warning(
                        "O agregado não contém a dependência administrativa; o gráfico não pode "
                        "ser segmentado por rede de ensino."
                    )

                if {"total_notas_matematica", "soma_notas_matematica"}.issubset(
                    df_ano_trabalho.columns
                ):
                    df_trabalho_agrupado = (
                        df_ano_trabalho.groupby("_condicao_chave", as_index=False)
                        .agg(
                            total_candidatos=("total_candidatos", "sum"),
                            total_notas_matematica=("total_notas_matematica", "sum"),
                            soma_notas_matematica=("soma_notas_matematica", "sum"),
                        )
                    )
                    df_trabalho_agrupado["media_matematica"] = (
                        df_trabalho_agrupado["soma_notas_matematica"]
                        .div(df_trabalho_agrupado["total_notas_matematica"])
                    )
                    df_trabalho_agrupado = df_trabalho_agrupado[
                        df_trabalho_agrupado["total_notas_matematica"] > 0
                    ]
                else:
                    st.error(
                        "Não é possível calcular a média exata: o agregado não contém "
                        "somas e contagens de notas válidas de Matemática."
                    )
                    df_trabalho_agrupado = pd.DataFrame()

                if not df_trabalho_agrupado.empty:
                    df_trabalho_agrupado["Condição de Trabalho"] = df_trabalho_agrupado[
                        "_condicao_chave"
                    ].map(rotulos_condicoes).fillna(df_trabalho_agrupado["_condicao_chave"])
                    df_trabalho_agrupado["Condição de Trabalho (completa)"] = (
                        df_trabalho_agrupado["Condição de Trabalho"]
                    )
                    df_trabalho_agrupado["Condição de Trabalho"] = (
                        df_trabalho_agrupado["Condição de Trabalho"]
                        .map(lambda descricao: "<br>".join(textwrap.wrap(descricao, width=20)))
                    )
                    if rede_trabalho == "Pública (estadual, federal e municipal)":
                        sufixo_rede = "Rede pública"
                    elif rede_trabalho == "Privada":
                        sufixo_rede = "Rede privada"
                    elif rede_trabalho == "Não informada":
                        sufixo_rede = "Rede não informada"
                    else:
                        sufixo_rede = "Todas as redes"
                    with st.container(border=True):
                        fig_f4_hist = px.bar(
                            df_trabalho_agrupado,
                            x="media_matematica",
                            y="Condição de Trabalho",
                            color="Condição de Trabalho",
                            color_discrete_sequence=px.colors.qualitative.Safe,
                            orientation="h",
                            title=(
                                f"Média ponderada exata de Matemática por Condição de Trabalho — "
                                f"ENEM {ano_trabalho} · {sufixo_rede}"
                            ),
                            category_orders={
                                "Condição de Trabalho": [
                                    "<br>".join(
                                        textwrap.wrap(rotulos_condicoes[chave], width=20)
                                    )
                                    for chave in ordem_condicoes
                                    if chave in df_trabalho_agrupado["_condicao_chave"].values
                                ]
                            },
                            labels={
                                "Condição de Trabalho": "Condição de Trabalho",
                                "media_matematica": "Média Matemática (TRI)",
                            },
                            hover_data={
                                key: True
                                for key in (
                                    "Condição de Trabalho (completa)",
                                    "total_candidatos",
                                    "total_notas_matematica",
                                )
                                if key in df_trabalho_agrupado.columns
                            },
                        )
                        fig_f4_hist.update_traces(
                            texttemplate="%{x:.2f}",
                            textposition="outside",
                            cliponaxis=False,
                        )
                        fig_f4_hist.update_layout(
                            template="plotly_white",
                            height=max(360, 100 + 55 * len(df_trabalho_agrupado)),
                            margin=dict(l=20, r=50, t=60, b=30),
                            showlegend=False,
                            yaxis=dict(tickfont=dict(size=10), automargin=True),
                            xaxis=dict(
                                automargin=True,
                                range=[
                                    0,
                                    df_trabalho_agrupado["media_matematica"].max() * 1.12,
                                ],
                            ),
                        )
                        st.plotly_chart(fig_f4_hist, width="stretch")
                else:
                    st.info(
                        "Não há notas válidas para exibir nas condições de trabalho deste recorte."
                    )
    else:
        df_socio_ano = df_pluri_socio.copy()
        if not df_socio_ano.empty:
            st.success(f"✅ Dados de infraestrutura e socioeconomia carregados para ENEM {year_label}.")
            
            if "TP_DEPENDENCIA_ADM_ESC_DESC" in df_socio_ano.columns:
                redes_disp: list[str] = df_socio_ano["TP_DEPENDENCIA_ADM_ESC_DESC"].unique().tolist()
                rede_sel = st.selectbox("Filtrar por Dependência Administrativa:", options=redes_disp, key="f4_rede")
                df_socio_ano = df_socio_ano[df_socio_ano["TP_DEPENDENCIA_ADM_ESC_DESC"] == rede_sel]
            
            if "Q006_DESC" in df_socio_ano.columns and "media_matematica" in df_socio_ano.columns and "Q007_DESC" in df_socio_ano.columns:
                if {
                    "soma_notas_matematica",
                    "total_notas_matematica",
                }.issubset(df_socio_ano.columns):
                    df_socio_ano = (
                        df_socio_ano.groupby(
                            ["Q006_DESC", "Q007_DESC"], as_index=False, dropna=False
                        )
                        .agg(
                            total_candidatos=("total_candidatos", "sum"),
                            soma_notas_matematica=("soma_notas_matematica", "sum"),
                            total_notas_matematica=("total_notas_matematica", "sum"),
                        )
                    )
                    df_socio_ano["media_matematica"] = (
                        df_socio_ano["soma_notas_matematica"]
                        .div(df_socio_ano["total_notas_matematica"])
                        .where(df_socio_ano["total_notas_matematica"] > 0)
                    )
                with st.container(border=True):
                    fig_scatter_f4 = px.scatter(
                        df_socio_ano, x="Q006_DESC", y="media_matematica",
                        size="total_candidatos" if "total_candidatos" in df_socio_ano.columns else None,
                        color="Q007_DESC", hover_name="Q006_DESC",
                        title=f"Matriz de Impacto: Renda, Trabalho e Desempenho — ENEM {year_label}",
                        labels={"Q006_DESC": "Faixa de Renda", "media_matematica": "Média Matemática", "Q007_DESC": "Condição de Trabalho"}
                    )
                    fig_scatter_f4.update_layout(
                        template="plotly_white", 
                        height=420,
                        margin=dict(l=20, r=20, t=50, b=20),
                        xaxis=dict(tickangle=-35, tickfont=dict(size=10), automargin=True)
                    )
                    st.plotly_chart(fig_scatter_f4, width="stretch")
        else:
            st.info("Não há dados socioeconômicos para os filtros globais atuais.")

    # Colunas finais estruturadas com Containers Nativos
    col_critica_f4, col_proposta_f4 = st.columns(2)
    with col_critica_f4:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica do Eixo de Trabalho e Infraestrutura")
            st.markdown("""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            Os dados demonstram que a exigência laboral precoce atua como um <strong>fator limitante crítico</strong> ao rendimento acadêmico. A ausência de suporte estrutural adequado nas instituições públicas compromete a retenção e o aproveitamento de discentes que acumulam funções profissionais e acadêmicas.
            </p>
            """, unsafe_allow_html=True)
        
    with col_proposta_f4:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Flexibilização Curricular e Apoio ao Estudante Trabalhador:</strong> Oferta de turnos alternativos e programas institucionais de mentoria voltados à gestão de tempo e apoio pedagógico direcionado.</li>
                <li><strong>Modernização Tecnológica Escolar:</strong> Expansão de infraestrutura digital e laboratórios de estudo autônomo nas unidades de ensino público periféricas.</li>
            </ul>
            """, unsafe_allow_html=True)