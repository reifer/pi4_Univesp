import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.utils.data_loader import get_global_filter_state, load_filtered_aggregate


def _income_sort_key(value):
    value = str(value)
    return (0, int(value)) if value.isdigit() else (1, value)


def render():
    st.markdown("---")
    with st.container(border=True):
        st.markdown("### 💰 2. A Renda e a Nota: O Fator Socioeconômico e o Impacto no TRI")

    years, ufs, treineiros = get_global_filter_state()
    df_renda = load_filtered_aggregate("agg_notas_renda")
    if df_renda.empty:
        st.info("Não há dados de renda para os filtros globais atuais.")
    else:
        code_column = (
            "RENDA_FAMILIAR_COD"
            if "RENDA_FAMILIAR_COD" in df_renda.columns
            else "Q006"
        )
        description_column = (
            "RENDA_FAMILIAR_DESC"
            if "RENDA_FAMILIAR_DESC" in df_renda.columns
            else "Q006_DESC"
        )
        sum_column = "soma_notas_mt"
        count_column = "total_notas_mt"
        if not {code_column, description_column, sum_column, count_column} <= set(df_renda):
            st.error("O agregado de renda não contém as colunas necessárias para a média ponderada.")
            return

        df_renda = df_renda.copy()
        df_renda[code_column] = df_renda[code_column].astype("string")
        descriptions = (
            df_renda.sort_values("NU_ANO", ascending=False)
            .drop_duplicates(code_column)
            .set_index(code_column)[description_column]
            .astype(str)
            .to_dict()
        )
        df_renda["Faixa de renda"] = (
            df_renda[description_column].fillna("Não Informado").astype(str)
        )
        summary = (
            df_renda.groupby(
                ["NU_ANO", code_column, "Faixa de renda"],
                as_index=False,
                dropna=False,
            )
            .agg(
                soma_notas_mt=(sum_column, "sum"),
                total_notas_mt=(count_column, "sum"),
                total_candidatos=("total_candidatos", "sum"),
            )
        )
        summary["Média de Matemática"] = (
            summary["soma_notas_mt"]
            .div(summary["total_notas_mt"])
            .where(summary["total_notas_mt"] > 0)
        )
        income_order = sorted(
            summary[code_column].dropna().unique(),
            key=_income_sort_key,
        )
        summary[code_column] = pd.Categorical(
            summary[code_column],
            categories=income_order,
            ordered=True,
        )
        summary = summary.sort_values(["NU_ANO", code_column])

        with st.container(border=True):
            st.markdown(
                f"Recorte global: ENEM {', '.join(map(str, years))}; "
                f"UFs {', '.join(ufs)}; candidatos {', '.join(treineiros)}."
            )
            heatmap_summary = summary.copy()
            heatmap_summary[code_column] = heatmap_summary[code_column].astype(str)
            heatmap_summary["Ano do ENEM"] = (
                heatmap_summary["NU_ANO"].astype(int).astype(str)
            )
            year_order = [
                str(year) for year in sorted(heatmap_summary["NU_ANO"].astype(int).unique())
            ]
            income_codes = sorted(
                heatmap_summary[code_column].dropna().unique(),
                key=_income_sort_key,
            )
            income_labels = [
                f"{code} — {descriptions.get(code, 'Não Informado')}"
                for code in income_codes
            ]
            score_matrix = (
                heatmap_summary.pivot(
                    index=code_column,
                    columns="Ano do ENEM",
                    values="Média de Matemática",
                )
                .reindex(index=income_codes, columns=year_order)
            )
            detail_lookup = heatmap_summary.set_index(
                [code_column, "Ano do ENEM"]
            ).to_dict("index")
            customdata = [
                [
                    [
                        detail_lookup.get((code, year), {}).get(
                            "Faixa de renda", "Sem dados"
                        ),
                        int(
                            detail_lookup.get((code, year), {}).get(
                                "total_notas_mt", 0
                            )
                        ),
                    ]
                    for year in year_order
                ]
                for code in income_codes
            ]
            fig = go.Figure(
                data=go.Heatmap(
                    x=year_order,
                    y=income_labels,
                    z=score_matrix.to_numpy(),
                    customdata=customdata,
                    colorscale="Viridis",
                    colorbar=dict(title="Média TRI", thickness=12),
                    xgap=2,
                    ygap=2,
                    hoverongaps=False,
                    hovertemplate=(
                        "Ano: %{x}<br>"
                        "Faixa de renda: %{y}<br>"
                        "Descrição da edição: %{customdata[0]}<br>"
                        "Média de Matemática: %{z:.2f}<br>"
                        "Total de notas válidas: %{customdata[1]:,}"
                        "<extra></extra>"
                    ),
                )
            )
            fig.update_layout(
                template="plotly_white",
                title="Média de Matemática por faixa de renda e ano",
                height=max(500, 30 * len(income_labels) + 150),
                margin=dict(l=20, r=20, t=60, b=40),
                xaxis=dict(
                    title="Ano do ENEM",
                    type="category",
                    categoryorder="array",
                    categoryarray=year_order,
                ),
                yaxis=dict(
                    title="Faixa de renda familiar",
                    type="category",
                    categoryorder="array",
                    categoryarray=income_labels,
                    autorange=True,
                    tickfont=dict(size=10),
                    automargin=True,
                ),
            )
            st.plotly_chart(fig, width="stretch")
            if any(year in (2024, 2025) for year in years):
                st.info(
                    "**Nota metodológica — comparabilidade das faixas:** em 2024 e 2025, "
                    "a renda familiar passou a ser identificada pela questão Q007; nas "
                    "edições anteriores, era registrada pela Q006. A mudança estrutural "
                    "redefiniu as faixas e exige cautela na comparação direta entre "
                    "edições. A aproximação das médias em 2024–2025 está presente nos "
                    "dados observados, mas não se deve concluir que a troca de questão, "
                    "por si só, a causou."
                )

    col_critica, col_proposta = st.columns(2)
    with col_critica:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica do Fator Socioeconômico")
            st.markdown(
                "A relação entre renda familiar e desempenho deve ser interpretada como "
                "associação, não causalidade. O recorte atual permite comparar as faixas "
                "entre os anos, estados e tipos de candidato selecionados."
            )
    with col_proposta:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown(
                "Políticas de assistência estudantil e apoio pedagógico podem priorizar "
                "estudantes em situação de vulnerabilidade, acompanhando resultados em "
                "cada recorte local."
            )
