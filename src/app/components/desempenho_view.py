import streamlit as st
import plotly.express as px

def render_desempenho_view(selected_year, selected_ufs, df_notas_uf):
    """Renderiza o módulo de Desempenho e Notas Médias (TRI)."""
    st.subheader(f"📈 Análise de Desempenho e Notas Médias no ENEM {selected_year}")
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

            n1, n2, n3, n4, n5 = st.columns(5)
            with n1: st.metric("Matemática", f"{avg_mt:.1f}")
            with n2: st.metric("Redação", f"{avg_redacao:.1f}")
            with n3: st.metric("Natureza", f"{avg_cn:.1f}")
            with n4: st.metric("Humanas", f"{avg_ch:.1f}")
            with n5: st.metric("Linguagens", f"{avg_lc:.1f}")

            st.markdown("##### Desempenho Médio por UF")
            fig_notas_uf = px.bar(
                f_notas_uf.groupby("SG_UF_PROVA")[["media_mt", "media_redacao"]].mean().reset_index(),
                x="SG_UF_PROVA", y=["media_mt", "media_redacao"],
                barmode="group",
                labels={"value": "Nota Média", "variable": "Disciplina", "SG_UF_PROVA": "Estado (UF)"}
            )
            fig_notas_uf.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
            st.plotly_chart(fig_notas_uf, width="stretch")