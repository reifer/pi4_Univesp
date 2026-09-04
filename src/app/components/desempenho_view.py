import streamlit as st
import plotly.express as px

def render_desempenho_view(selected_year, selected_ufs, df_notas_uf):
    """Renderiza o módulo de Desempenho e Notas Médias (TRI)."""
    
    # Cabeçalho encapsulado em Clean Card
    st.markdown(f"""
    <div class="clean-card">
        <h3 style="margin-top: 0; color: #0F172A;">📈 Análise de Desempenho e Notas Médias no ENEM {selected_year}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if df_notas_uf.empty:
        st.info("Dados agregados de notas não encontrados.")
    else:
        f_notas_uf = df_notas_uf[df_notas_uf["SG_UF_PROVA"].isin(selected_ufs)]
        if not f_notas_uf.empty and f_notas_uf["total_candidatos"].sum() > 0:
            tot_cand = f_notas_uf["total_candidatos"].sum()
            avg_redacao = (f_notas_uf["media_redacao"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_mt = (f_notas_uf["media_mt"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_cn = (f_notas_uf["media_cn"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_ch = (f_notas_uf["media_ch"] * f_notas_uf["total_candidatos"]).sum() / tot_cand
            avg_lc = (f_notas_uf["media_lc"] * f_notas_uf["total_candidatos"]).sum() / tot_cand

            # Cards de Métricas Estilizados com o Padrão Clean
            n1, n2, n3, n4, n5 = st.columns(5)
            with n1:
                st.markdown(f'<div class="clean-card" style="text-align: center; padding: 12px;"><div class="metric-label-clean">Matemática</div><div class="metric-value-clean" style="font-size: 1.4rem;">{avg_mt:.1f}</div></div>', unsafe_allow_html=True)
            with n2:
                st.markdown(f'<div class="clean-card" style="text-align: center; padding: 12px;"><div class="metric-label-clean">Redação</div><div class="metric-value-clean" style="font-size: 1.4rem;">{avg_redacao:.1f}</div></div>', unsafe_allow_html=True)
            with n3:
                st.markdown(f'<div class="clean-card" style="text-align: center; padding: 12px;"><div class="metric-label-clean">Natureza</div><div class="metric-value-clean" style="font-size: 1.4rem;">{avg_cn:.1f}</div></div>', unsafe_allow_html=True)
            with n4:
                st.markdown(f'<div class="clean-card" style="text-align: center; padding: 12px;"><div class="metric-label-clean">Humanas</div><div class="metric-value-clean" style="font-size: 1.4rem;">{avg_ch:.1f}</div></div>', unsafe_allow_html=True)
            with n5:
                st.markdown(f'<div class="clean-card" style="text-align: center; padding: 12px;"><div class="metric-label-clean">Linguagens</div><div class="metric-value-clean" style="font-size: 1.4rem;">{avg_lc:.1f}</div></div>', unsafe_allow_html=True)

            st.markdown("##### Desempenho Médio por UF")
            
            df_grafico_uf = f_notas_uf.groupby("SG_UF_PROVA")[["media_mt", "media_redacao"]].mean().reset_index()
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