import streamlit as st
import plotly.express as px
import pandas as pd

def render_rede_view(selected_year, selected_ufs, df_rede, df_rede_plurianual, df_socio_escola, COLOR_MAP_REDE):
    """Renderiza o módulo de Redes de Ensino e Análise Plurianual."""
    st.markdown(f"### 🏫 Granularidade e Desempenho por Rede de Ensino — ENEM {selected_year} & Plurianual")
    st.markdown(
        "Análise detalhada baseada no campo oficial **`TP_DEPENDENCIA_ADM_ESC`** (1 = Federal, 2 = Estadual, 3 = Municipal, 4 = Privada), "
        "permitindo avaliar a volumetria, as disparidades de desempenho e a evolução temporal das escolas públicas versus rede privada."
    )

    if df_rede.empty:
        st.warning(
            f"⚠️ Nenhum dado de rede de ensino encontrado para o ano **{selected_year}**. "
            "Execute `python src/data_pipeline/transform.py` para gerar os agregados."
        )
        return

    if "SG_UF_PROVA" in df_rede.columns:
        df_rede_filtered = df_rede[df_rede["SG_UF_PROVA"].isin(selected_ufs)].copy()
    else:
        df_rede_filtered = df_rede.copy()

    if df_rede_filtered.empty:
        st.warning(
            f"⚠️ Nenhum registro encontrado para os estados selecionados em {selected_year}. "
            "Verifique o filtro geográfico na barra lateral."
        )
        return

    def _media_pond(col_name, grp_df):
        def _calc(x):
            total = grp_df.loc[x.index, "total_candidatos"].sum()
            if total > 0:
                return (x * grp_df.loc[x.index, "total_candidatos"]).sum() / total
            return 0
        return (col_name, _calc)

    _nota_agg_cols = [c for c in ["media_mt", "media_redacao", "media_cn", "media_ch", "media_lc", "media_geral"] if c in df_rede_filtered.columns]

    rede_summary = df_rede_filtered.groupby("TP_DEPENDENCIA_ADM_ESC_DESC").agg(
        total_candidatos=("total_candidatos", "sum"),
        **{col: _media_pond(col, df_rede_filtered) for col in _nota_agg_cols}
    ).reset_index()

    total_geral_rede = rede_summary["total_candidatos"].sum()
    rede_summary["percentual_alunos"] = (
        (rede_summary["total_candidatos"] / total_geral_rede * 100).round(2)
        if total_geral_rede > 0 else 0
    )

    redes_identificadas = rede_summary[rede_summary["TP_DEPENDENCIA_ADM_ESC_DESC"] != "Não Informado"].copy()

    st.markdown("#### 📌 Destaques Executivos por Dependência Administrativa")
    k1, k2, k3, k4 = st.columns(4)

    cand_publica = rede_summary[rede_summary["TP_DEPENDENCIA_ADM_ESC_DESC"].isin(["Federal", "Estadual", "Municipal"])]["total_candidatos"].sum()
    cand_privada = rede_summary[rede_summary["TP_DEPENDENCIA_ADM_ESC_DESC"] == "Privada"]["total_candidatos"].sum()
    
    top_mt_rede = redes_identificadas.loc[redes_identificadas["media_mt"].idxmax()] if not redes_identificadas.empty else None
    top_red_rede = redes_identificadas.loc[redes_identificadas["media_redacao"].idxmax()] if not redes_identificadas.empty else None

    with k1:
        st.markdown(f"""
        <div class="clean-card">
            <div class="metric-label-clean">Alunos Rede Pública (Fed+Est+Mun)</div>
            <div class="metric-value-clean">{cand_publica:,.0f}</div>
            <div class="metric-sub-clean">{(cand_publica/total_geral_rede*100):.1f}% do total</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="clean-card">
            <div class="metric-label-clean">Alunos Rede Privada</div>
            <div class="metric-value-clean">{cand_privada:,.0f}</div>
            <div class="metric-sub-clean">{(cand_privada/total_geral_rede*100):.1f}% do total</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        val_mt = f"{top_mt_rede['media_mt']:.1f}" if top_mt_rede is not None else "N/A"
        nome_mt = top_mt_rede['TP_DEPENDENCIA_ADM_ESC_DESC'] if top_mt_rede is not None else "-"
        st.markdown(f"""
        <div class="clean-card">
            <div class="metric-label-clean">Maior Média Matemática</div>
            <div class="metric-value-clean">{val_mt}</div>
            <div class="metric-sub-clean">Líder: {nome_mt}</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        val_red = f"{top_red_rede['media_redacao']:.1f}" if top_red_rede is not None else "N/A"
        nome_red = top_red_rede['TP_DEPENDENCIA_ADM_ESC_DESC'] if top_red_rede is not None else "-"
        st.markdown(f"""
        <div class="clean-card">
            <div class="metric-label-clean">Maior Média Redação</div>
            <div class="metric-value-clean">{val_red}</div>
            <div class="metric-sub-clean">Líder: {nome_red}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 1️⃣ Volumetria de Alunos por Dependência Administrativa")
    col_v1, col_v2 = st.columns([5, 5])
    
    with col_v1:
        st.markdown("##### Total Absoluto de Inscritos")
        fig_vol = px.bar(
            redes_identificadas,
            x="TP_DEPENDENCIA_ADM_ESC_DESC",
            y="total_candidatos",
            color="TP_DEPENDENCIA_ADM_ESC_DESC",
            color_discrete_map=COLOR_MAP_REDE,
            text_auto=".2s",
            labels={"TP_DEPENDENCIA_ADM_ESC_DESC": "Rede de Ensino", "total_candidatos": "Total de Candidatos"}
        )
        fig_vol.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350, showlegend=False)
        st.plotly_chart(fig_vol, width="stretch")

    with col_v2:
        st.markdown("##### Proporção / Participação (%)")
        fig_donut = px.pie(
            redes_identificadas,
            names="TP_DEPENDENCIA_ADM_ESC_DESC",
            values="total_candidatos",
            hole=0.5,
            color="TP_DEPENDENCIA_ADM_ESC_DESC",
            color_discrete_map=COLOR_MAP_REDE
        )
        fig_donut.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
        st.plotly_chart(fig_donut, width="stretch")

    st.markdown("---")
    st.markdown("#### 2️⃣ Comparativo Multidisciplinar de Desempenho (Barras Agrupadas)")
    _nota_cols = [c for c in ["media_cn", "media_ch", "media_lc", "media_mt", "media_redacao"] if c in redes_identificadas.columns]
    melted_notas = redes_identificadas.melt(
        id_vars=["TP_DEPENDENCIA_ADM_ESC_DESC"],
        value_vars=_nota_cols,
        var_name="Area_Conhecimento",
        value_name="Nota_Media"
    )
    area_names = {
        "media_cn": "Ciências da Natureza",
        "media_ch": "Ciências Humanas",
        "media_lc": "Linguagens e Códigos",
        "media_mt": "Matemática",
        "media_redacao": "Redação"
    }
    melted_notas["Area_Desc"] = melted_notas["Area_Conhecimento"].map(area_names)

    fig_grouped_bar = px.bar(
        melted_notas,
        x="Area_Desc",
        y="Nota_Media",
        color="TP_DEPENDENCIA_ADM_ESC_DESC",
        barmode="group",
        color_discrete_map=COLOR_MAP_REDE,
        text_auto=".1f",
        labels={"Area_Desc": "Área de Conhecimento", "Nota_Media": "Nota Média (TRI)", "TP_DEPENDENCIA_ADM_ESC_DESC": "Dependência Administrativa"}
    )
    fig_grouped_bar.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_grouped_bar, width="stretch")

    st.markdown("---")
    st.markdown("#### 3️⃣ Evolução Histórica Plurianual por Rede de Ensino")
    if not df_rede_plurianual.empty and "NU_ANO" in df_rede_plurianual.columns:
        _uf_mask = (
            df_rede_plurianual["SG_UF_PROVA"].isin(selected_ufs)
            if "SG_UF_PROVA" in df_rede_plurianual.columns
            else pd.Series(True, index=df_rede_plurianual.index)
        )
        df_pluri_filtered = df_rede_plurianual[
            (df_rede_plurianual["TP_DEPENDENCIA_ADM_ESC_DESC"] != "Não Informado") & _uf_mask
        ].copy()

        if not df_pluri_filtered.empty:
            _pluri_nota_cols = [c for c in ["media_mt", "media_redacao", "media_cn", "media_ch", "media_lc", "media_geral"] if c in df_pluri_filtered.columns]

            def _pp(col):
                def _f(x):
                    total = df_pluri_filtered.loc[x.index, "total_candidatos"].sum()
                    return (x * df_pluri_filtered.loc[x.index, "total_candidatos"]).sum() / total if total > 0 else 0
                return (col, _f)

            pluri_summary = df_pluri_filtered.groupby(["NU_ANO", "TP_DEPENDENCIA_ADM_ESC_DESC"]).agg(
                total_candidatos=("total_candidatos", "sum"),
                **{col: _pp(col) for col in _pluri_nota_cols}
            ).reset_index().sort_values(by="NU_ANO")

            col_line1, col_line2 = st.columns(2)
            with col_line1:
                metric_to_plot = st.selectbox(
                    "Selecione a Métrica para Série Temporal:",
                    options=["media_mt", "media_redacao", "media_geral", "media_cn", "media_ch", "media_lc"],
                    format_func=lambda x: {
                        "media_mt": "Matemática",
                        "media_redacao": "Redação",
                        "media_geral": "Média Geral",
                        "media_cn": "Ciências da Natureza",
                        "media_ch": "Ciências Humanas",
                        "media_lc": "Linguagens e Códigos"
                    }[x]
                )
                fig_line_notas = px.line(
                    pluri_summary,
                    x="NU_ANO",
                    y=metric_to_plot,
                    color="TP_DEPENDENCIA_ADM_ESC_DESC",
                    markers=True,
                    color_discrete_map=COLOR_MAP_REDE,
                    title=f"Evolução das Notas ({metric_to_plot})",
                    labels={"NU_ANO": "Ano do Exame", metric_to_plot: "Nota Média", "TP_DEPENDENCIA_ADM_ESC_DESC": "Rede"}
                )
                fig_line_notas.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
                st.plotly_chart(fig_line_notas, width="stretch")

            with col_line2:
                fig_line_vol = px.line(
                    pluri_summary,
                    x="NU_ANO",
                    y="total_candidatos",
                    color="TP_DEPENDENCIA_ADM_ESC_DESC",
                    markers=True,
                    color_discrete_map=COLOR_MAP_REDE,
                    title="Evolução de Inscritos por Rede",
                    labels={"NU_ANO": "Ano do Exame", "total_candidatos": "Total de Candidatos", "TP_DEPENDENCIA_ADM_ESC_DESC": "Rede"}
                )
                fig_line_vol.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=400)
                st.plotly_chart(fig_line_vol, width="stretch")

    st.markdown("---")
    st.markdown("#### 4️⃣ 🔬 Raio-X Avançado: Impacto Socioeconômico na Escola (`Q006` x `Q007` x Rede)")
    
    if not df_socio_escola.empty:
        opcoes_redes = [r for r in df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"].unique() if r != "Não Informado"]
        if not opcoes_redes:
            opcoes_redes = df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"].unique()

        selected_rede_filter = st.selectbox(
            "Filtrar por Dependência Administrativa da Escola:",
            options=opcoes_redes
        )
        df_filtered_socio = df_socio_escola[df_socio_escola["TP_DEPENDENCIA_ADM_ESC_DESC"] == selected_rede_filter]
        
        fig_socio = px.scatter(
            df_filtered_socio,
            x="Q006_DESC",
            y="media_matematica",
            size="total_candidatos",
            color="Q007_DESC",
            hover_name="Q006_DESC",
            title=f"Desempenho em Matemática vs Renda Familiar ({selected_rede_filter})",
            labels={"Q006_DESC": "Faixa de Renda", "media_matematica": "Média Matemática", "Q007_DESC": "Trabalho (Q007)"}
        )
        fig_socio.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
        fig_socio.update_xaxes(tickangle=45)
        st.plotly_chart(fig_socio, width="stretch")