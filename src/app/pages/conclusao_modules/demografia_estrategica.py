import plotly.express as px
import streamlit as st

from app.utils.data_loader import get_global_filter_state, load_filtered_aggregate


def render():
    st.markdown("---")
    with st.container(border=True):
        st.markdown("### 🌎 5. Demografia, Gênero e Desigualdades Regionais")

    years, ufs, treineiros = get_global_filter_state()
    df_demo = load_filtered_aggregate("agg_demografia")
    if df_demo.empty:
        st.info("Não há dados demográficos para os filtros globais atuais.")
    elif "TP_SEXO_DESC" in df_demo.columns:
        recorte_label = ", ".join(map(str, years))
        st.caption(
            f"Recorte global — ENEM {recorte_label}; UFs {', '.join(ufs)}; "
            f"candidatos {', '.join(treineiros)}."
        )
        if len(years) > 1:
            chart_data = (
                df_demo.groupby(
                    ["NU_ANO", "TP_SEXO_DESC"], as_index=False
                )["total_candidatos"]
                .sum()
            )
            fig = px.bar(
                chart_data,
                x="NU_ANO",
                y="total_candidatos",
                color="TP_SEXO_DESC",
                barmode="group",
                title="Participação por gênero no recorte plurianual selecionado",
                labels={
                    "NU_ANO": "Ano do exame",
                    "total_candidatos": "Total de inscritos",
                    "TP_SEXO_DESC": "Gênero",
                },
            )
        else:
            chart_data = (
                df_demo.groupby("TP_SEXO_DESC", as_index=False)["total_candidatos"]
                .sum()
            )
            fig = px.pie(
                chart_data,
                names="TP_SEXO_DESC",
                values="total_candidatos",
                hole=0.4,
                title=f"Proporção de participantes por gênero — ENEM {years[0]}",
                color_discrete_sequence=["#ec4899", "#2563eb"],
            )
        fig.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig, width="stretch")

    col_critica, col_proposta = st.columns(2)
    with col_critica:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica Demográfica e Regional")
            st.markdown(
                "A distribuição observada descreve os participantes do recorte selecionado; "
                "ela não representa, isoladamente, a população elegível nem a conversão de "
                "inscrições em presença."
            )
    with col_proposta:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown(
                "Ações de acesso devem considerar diferenças territoriais e acompanhar "
                "indicadores locais antes de orientar a alocação de recursos."
            )
