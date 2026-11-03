import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.utils.data_loader import filter_aggregate_frame, weighted_group_summary


SCORE_METRICS = {
    "media_matematica": ("soma_notas_mt", "total_notas_mt"),
    "media_redacao": ("soma_notas_redacao", "total_notas_redacao"),
}


def render_geopolitica_view(
    df_notas_uf,
    df_rede_plurianual,
    selected_years=None,
    selected_ufs=None,
    selected_treineiro_labels=None,
):
    """Renderiza o módulo de Geopolítica & Séries Temporais com containers nativos responsivos."""
    selected_years = selected_years or sorted(df_notas_uf["NU_ANO"].unique().tolist())
    selected_ufs = selected_ufs or sorted(df_notas_uf["SG_UF_PROVA"].unique().tolist())
    selected_treineiro_labels = selected_treineiro_labels or ["Não Treineiro", "Treineiro"]
    
    with st.container(border=True):
        st.markdown("### 🌎 Geopolítica e Séries Temporais Plurianual")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        with st.container(border=True):
            st.markdown("##### 📍 Desempenho por Macrorregião")
            
            uf_to_regiao = {
                'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
                'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
                'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
                'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
                'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
            }
            if not df_notas_uf.empty:
                df_regiao = filter_aggregate_frame(
                    df_notas_uf,
                    selected_years,
                    selected_ufs,
                    selected_treineiro_labels,
                )
                df_regiao["Regiao"] = df_regiao["SG_UF_PROVA"].map(uf_to_regiao)
                metrics = {
                    name: columns
                    for name, columns in SCORE_METRICS.items()
                    if set(columns) <= set(df_regiao.columns)
                }
                df_regiao_agg = weighted_group_summary(df_regiao, ["Regiao"], metrics)
                
                fig_reg = px.bar(
                    df_regiao_agg, x="Regiao", y=["media_matematica", "media_redacao"], barmode="group",
                    title="Médias por Região", labels={"value": "Média", "variable": "Área"}
                )
                fig_reg.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=380,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_reg, use_container_width=True)
            else:
                st.info("Dados regionais não disponíveis.")
            
    with col_g2:
        with st.container(border=True):
            st.markdown("##### 📈 Evolução Histórica Nacional Plurianual")
            
            if not df_rede_plurianual.empty and "NU_ANO" in df_rede_plurianual.columns:
                df_national = filter_aggregate_frame(
                    df_rede_plurianual,
                    selected_years,
                    selected_ufs,
                    selected_treineiro_labels,
                )
                metrics = {
                    "Matematica": SCORE_METRICS["media_matematica"],
                    "Redacao": SCORE_METRICS["media_redacao"],
                }
                metrics = {
                    name: columns
                    for name, columns in metrics.items()
                    if set(columns) <= set(df_national.columns)
                }
                nat_series = weighted_group_summary(df_national, ["NU_ANO"], metrics)
                fig_time = px.line(
                    nat_series, x="NU_ANO", y=["Matematica", "Redacao"], markers=True,
                    title="Evolução Nacional", labels={"value": "Média", "variable": "Componente"}
                )
                fig_time.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=380,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("Série temporal nacional não disponível.")