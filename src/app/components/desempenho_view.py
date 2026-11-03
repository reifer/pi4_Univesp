import streamlit as st
import plotly.express as px

from app.utils.data_loader import filter_aggregate_frame, weighted_group_summary


SCORE_METRICS = {
    "media_mt": ("soma_notas_mt", "total_notas_mt"),
    "media_redacao": ("soma_notas_redacao", "total_notas_redacao"),
    "media_cn": ("soma_notas_cn", "total_notas_cn"),
    "media_ch": ("soma_notas_ch", "total_notas_ch"),
    "media_lc": ("soma_notas_lc", "total_notas_lc"),
}


def render_desempenho_view(
    selected_year,
    selected_ufs,
    df_notas_uf,
    selected_years=None,
    selected_treineiro_labels=None,
):
    """Renderiza o módulo de Desempenho e Notas Médias (TRI) utilizando containers nativos."""
    selected_years = selected_years or sorted(df_notas_uf["NU_ANO"].unique().tolist())
    selected_treineiro_labels = selected_treineiro_labels or ["Não Treineiro", "Treineiro"]
    
    with st.container(border=True):
        st.markdown(f"### 📈 Análise de Desempenho e Notas Médias no ENEM {selected_year}")
    
    if df_notas_uf.empty:
        st.info("Dados agregados de notas não encontrados.")
    else:
        f_notas_uf = filter_aggregate_frame(
            df_notas_uf,
            selected_years,
            selected_ufs,
            selected_treineiro_labels,
        )
        if not f_notas_uf.empty and f_notas_uf["total_candidatos"].sum() > 0:
            score_metrics = {
                name: columns
                for name, columns in SCORE_METRICS.items()
                if set(columns) <= set(f_notas_uf.columns)
            }
            scores = weighted_group_summary(f_notas_uf, [], score_metrics)
            score_values = scores.iloc[0]
            avg_redacao = score_values["media_redacao"]
            avg_mt = score_values["media_mt"]
            avg_cn = score_values["media_cn"]
            avg_ch = score_values["media_ch"]
            avg_lc = score_values["media_lc"]

            n1, n2, n3, n4, n5 = st.columns(5)
            with n1:
                with st.container(border=True):
                    st.metric("Matemática", f"{avg_mt:.1f}")
            with n2:
                with st.container(border=True):
                    st.metric("Redação", f"{avg_redacao:.1f}")
            with n3:
                with st.container(border=True):
                    st.metric("Natureza", f"{avg_cn:.1f}")
            with n4:
                with st.container(border=True):
                    st.metric("Humanas", f"{avg_ch:.1f}")
            with n5:
                with st.container(border=True):
                    st.metric("Linguagens", f"{avg_lc:.1f}")

            with st.container(border=True):
                st.markdown("##### Desempenho Médio por UF")
                
                df_grafico_uf = weighted_group_summary(
                    f_notas_uf,
                    ["SG_UF_PROVA"],
                    {
                        name: score_metrics[name]
                        for name in ("media_mt", "media_redacao")
                        if name in score_metrics
                    },
                )
                fig_notas_uf = px.bar(
                    df_grafico_uf,
                    x="SG_UF_PROVA", y=["media_mt", "media_redacao"],
                    barmode="group",
                    labels={"value": "Nota Média", "variable": "Disciplina", "SG_UF_PROVA": "Estado (UF)"}
                )
                fig_notas_uf.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_notas_uf, use_container_width=True)