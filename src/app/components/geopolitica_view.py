import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_geopolitica_view(df_notas_uf, df_rede_plurianual):
    """Renderiza o módulo de Geopolítica & Séries Temporais com design fluido e responsivo."""
    
    # Cabeçalho encapsulado em Clean Card
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top: 0; color: #0F172A; font-size: 1.4rem;">🌎 Geopolítica e Séries Temporais Plurianual</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("""
        <div class="clean-card" style="min-height: 500px;">
            <h4 style="margin-top: 0; color: #0F172A; font-size: 1.1rem;">📍 Desempenho por Macrorregião</h4>
        """, unsafe_allow_html=True)
        
        uf_to_regiao = {
            'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
            'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
            'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
            'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
        }
        if not df_notas_uf.empty:
            df_regiao = df_notas_uf.copy()
            df_regiao["Regiao"] = df_regiao["SG_UF_PROVA"].map(uf_to_regiao)
            df_regiao_agg = df_regiao.groupby("Regiao").agg(
                media_matematica=("media_mt", "mean"),
                media_redacao=("media_redacao", "mean")
            ).reset_index()
            
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
            
        st.markdown("</div>", unsafe_allow_html=True)
            
    with col_g2:
        st.markdown("""
        <div class="clean-card" style="min-height: 500px;">
            <h4 style="margin-top: 0; color: #0F172A; font-size: 1.1rem;">📈 Evolução Histórica Nacional Plurianual</h4>
        """, unsafe_allow_html=True)
        
        if not df_rede_plurianual.empty and "NU_ANO" in df_rede_plurianual.columns:
            nat_series = df_rede_plurianual.groupby("NU_ANO").agg(
                Matematica=("media_mt", lambda x: (x * df_rede_plurianual.loc[x.index, "total_candidatos"]).sum() / df_rede_plurianual.loc[x.index, "total_candidatos"].sum() if df_rede_plurianual.loc[x.index, "total_candidatos"].sum() > 0 else 0),
                Redacao=("media_redacao", lambda x: (x * df_rede_plurianual.loc[x.index, "total_candidatos"]).sum() / df_rede_plurianual.loc[x.index, "total_candidatos"].sum() if df_rede_plurianual.loc[x.index, "total_candidatos"].sum() > 0 else 0)
            ).reset_index()
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
            
        st.markdown("</div>", unsafe_allow_html=True)