import streamlit as st
import plotly.express as px
import pandas as pd

def render_socio_view(df_notas_renda, selected_treineiro_labels, selected_treineiro_values, filtered_df):
    """Renderiza o módulo de Perfil Socioeconômico (Renda Familiar) com design fluido e responsivo."""
    
    # Cabeçalho encapsulado em Clean Card
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top: 0; color: #0F172A; font-size: 1.4rem;">💰 Distribuição por Faixa de Renda Familiar</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_notas_renda.empty:
        st.markdown("""
        <div class="clean-card">
        """, unsafe_allow_html=True)
        
        df_renda_filt = df_notas_renda.copy()
        if "IN_TREINEIRO_DESC" in df_renda_filt.columns:
            df_renda_filt = df_renda_filt[df_renda_filt["IN_TREINEIRO_DESC"].isin(selected_treineiro_labels)]
        elif "IN_TREINEIRO" in df_renda_filt.columns:
            df_renda_filt["IN_TREINEIRO"] = df_renda_filt["IN_TREINEIRO"].astype(str)
            df_renda_filt = df_renda_filt[df_renda_filt["IN_TREINEIRO"].isin(selected_treineiro_values)]
        
        cod_col = "RENDA_FAMILIAR_COD" if "RENDA_FAMILIAR_COD" in df_renda_filt.columns else ("Q006" if "Q006" in df_renda_filt.columns else df_renda_filt.columns[1])
        desc_col = "RENDA_FAMILIAR_DESC" if "RENDA_FAMILIAR_DESC" in df_renda_filt.columns else ("Q006_DESC" if "Q006_DESC" in df_renda_filt.columns else cod_col)
        
        df_renda_agg = df_renda_filt.groupby([cod_col, desc_col])["total_candidatos"].sum().reset_index()
        df_renda_agg["Faixa_Renda"] = df_renda_agg[cod_col].astype(str) + " — " + df_renda_agg[desc_col].astype(str)
        df_renda_agg = df_renda_agg.sort_values(by=cod_col)
        
        fig_renda = px.bar(
            df_renda_agg,
            x="Faixa_Renda", y="total_candidatos",
            color="total_candidatos", color_continuous_scale="Blues", text_auto=".2s",
            labels={"Faixa_Renda": "Faixa de Renda Familiar", "total_candidatos": "Total de Candidatos"}
        )
        fig_renda.update_layout(
            template="plotly_white", 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            height=420, 
            margin=dict(l=10, r=10, t=30, b=20),
            coloraxis_showscale=False
        )
        fig_renda.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_renda, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif not filtered_df.empty:
        cod_col = "RENDA_FAMILIAR_COD" if "RENDA_FAMILIAR_COD" in filtered_df.columns else "Q006"
        desc_col = "RENDA_FAMILIAR_DESC" if "RENDA_FAMILIAR_DESC" in filtered_df.columns else "Q006_DESC"
        
        if cod_col in filtered_df.columns and desc_col in filtered_df.columns:
            display_series = filtered_df[cod_col].astype(str) + " — " + filtered_df[desc_col].astype(str)
        elif cod_col in filtered_df.columns:
            display_series = filtered_df[cod_col].astype(str)
        else:
            display_series = pd.Series(dtype=str)
        
        if not display_series.empty:
            st.markdown("""
            <div class="clean-card">
            """, unsafe_allow_html=True)
            renda_counts = display_series.value_counts().reset_index()
            renda_counts.columns = ["Faixa_Renda", "total_inscritos"]
            fig_renda = px.bar(
                renda_counts.sort_values(by="Faixa_Renda"),
                x="Faixa_Renda", y="total_inscritos",
                color="total_inscritos", color_continuous_scale="Blues", text_auto=".2s"
            )
            fig_renda.update_layout(
                template="plotly_white", 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                height=420, 
                margin=dict(l=10, r=10, t=30, b=20),
                coloraxis_showscale=False
            )
            fig_renda.update_xaxes(tickangle=-30)
            st.plotly_chart(fig_renda, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Dados de renda familiar não disponíveis no recorte atual.")
    else:
        st.info("Dados de renda familiar não disponíveis no recorte atual.")