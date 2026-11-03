import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.utils.data_loader import filter_aggregate_frame


def render_geo_view(
    selected_ufs,
    selected_treineiro_labels,
    selected_treineiro_values,
    df_notas_uf,
    df_demografia,
    filtered_df,
    selected_years=None,
):
    """Renderiza o módulo de Panorama Geográfico (UF) e Distribuição por Sexo com containers nativos responsivos."""
    selected_years = selected_years or sorted(df_notas_uf["NU_ANO"].unique().tolist())
    
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        with st.container(border=True):
            st.markdown("##### 📍 Inscritos por Estado (UF)")
            
            if not df_notas_uf.empty and "SG_UF_PROVA" in df_notas_uf.columns:
                df_uf_agg = filter_aggregate_frame(
                    df_notas_uf,
                    selected_years,
                    selected_ufs,
                    selected_treineiro_labels,
                )
                
                uf_counts = df_uf_agg.groupby("SG_UF_PROVA")["total_candidatos"].sum().reset_index()
                uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
                fig_uf = px.bar(
                    uf_counts.sort_values(by="total_inscritos", ascending=True),
                    x="total_inscritos", y="SG_UF_PROVA", orientation="h",
                    text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues"  # type: ignore[reportArgumentType]
                )
                fig_uf.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=420, 
                    margin=dict(l=10, r=10, t=30, b=10),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_uf, use_container_width=True)
            elif not filtered_df.empty:
                uf_counts = filtered_df["SG_UF_PROVA"].value_counts().reset_index()
                uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
                fig_uf = px.bar(
                    uf_counts.sort_values(by="total_inscritos", ascending=True),
                    x="total_inscritos", y="SG_UF_PROVA", orientation="h",
                    text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues"  # type: ignore[reportArgumentType]
                )
                fig_uf.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=420, 
                    margin=dict(l=10, r=10, t=30, b=10),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_uf, use_container_width=True)
            else:
                st.info("Dados detalhados por UF não carregados.")
            
    with col_right:
        with st.container(border=True):
            st.markdown("##### 👥 Distribuição por Sexo")
            
            if not df_demografia.empty and "TP_SEXO_DESC" in df_demografia.columns:
                df_demo_filt = filter_aggregate_frame(
                    df_demografia,
                    selected_years,
                    selected_ufs,
                    selected_treineiro_labels,
                )
                
                sex_counts = df_demo_filt.groupby("TP_SEXO_DESC")["total_candidatos"].sum()
                fig_pie = go.Figure(data=[go.Pie(labels=sex_counts.index.tolist(), values=sex_counts.values.tolist(), hole=.5, marker_colors=["#ec4899", "#2563eb"])])
                fig_pie.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=420,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            elif not filtered_df.empty:
                sex_col = "TP_SEXO_DESC" if "TP_SEXO_DESC" in filtered_df.columns else "TP_SEXO"
                sex_counts = filtered_df[sex_col].value_counts()
                fig_pie = go.Figure(data=[go.Pie(labels=sex_counts.index.tolist(), values=sex_counts.values.tolist(), hole=.5, marker_colors=["#ec4899", "#2563eb"])])
                fig_pie.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=420,
                    margin=dict(l=10, r=10, t=30, b=10),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Distribuição de sexo não disponível.")