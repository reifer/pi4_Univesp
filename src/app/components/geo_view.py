import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_geo_view(selected_ufs, selected_treineiro_labels, selected_treineiro_values, df_notas_uf, df_demografia, filtered_df):
    """Renderiza o módulo de Panorama Geográfico (UF) e Distribuição por Sexo com design fluido e responsivo."""
    
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.markdown("""
        <div class="clean-card" style="min-height: 530px;">
            <h3 style="margin-top: 0; color: #0F172A; font-size: 1.25rem;">Inscritos por Estado (UF)</h3>
        """, unsafe_allow_html=True)
        
        if not df_notas_uf.empty and "SG_UF_PROVA" in df_notas_uf.columns:
            df_uf_agg = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)].copy()
            if "IN_TREINEIRO_DESC" in df_uf_agg.columns:
                df_uf_agg = df_uf_agg[df_uf_agg["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
            elif "IN_TREINEIRO" in df_uf_agg.columns:
                df_uf_agg["IN_TREINEIRO"] = df_uf_agg["IN_TREINEIRO"].astype(str)
                df_uf_agg = df_uf_agg[df_uf_agg["IN_TREINEIRO"].isin(selected_treineiro_values)]
            
            uf_counts = df_uf_agg.groupby("SG_UF_PROVA")["total_candidatos"].sum().reset_index()
            uf_counts.columns = ["SG_UF_PROVA", "total_inscritos"]
            fig_uf = px.bar(
                uf_counts.sort_values(by="total_inscritos", ascending=True),
                x="total_inscritos", y="SG_UF_PROVA", orientation="h",
                text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues"
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
                text_auto=".2s", color="total_inscritos", color_continuous_scale="Blues"
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
            
        st.markdown("</div>", unsafe_allow_html=True)
            
    with col_right:
        st.markdown("""
        <div class="clean-card" style="min-height: 530px;">
            <h3 style="margin-top: 0; color: #0F172A; font-size: 1.25rem;">Distribuição por Sexo</h3>
        """, unsafe_allow_html=True)
        
        if not df_demografia.empty and "TP_SEXO_DESC" in df_demografia.columns:
            df_demo_filt = df_demografia[df_demografia["SG_UF_PROVA"].isin(selected_ufs)].copy()
            if "IN_TREINEIRO_DESC" in df_demo_filt.columns:
                df_demo_filt = df_demo_filt[df_demo_filt["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
            elif "IN_TREINEIRO" in df_demo_filt.columns:
                df_demo_filt["IN_TREINEIRO"] = df_demo_filt["IN_TREINEIRO"].astype(str)
                df_demo_filt = df_demo_filt[df_demo_filt["IN_TREINEIRO"].isin(selected_treineiro_values)]
            
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
            
        st.markdown("</div>", unsafe_allow_html=True)