import streamlit as st
import pandas as pd
import os
import plotly.express as px
import textwrap

def render():
    st.markdown("---")
    
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
        st.markdown("### 🛠️ 4. A Infraestrutura e o Trabalho: O Peso da Jornada e do Apoio Escolar")
    
    anos_opcoes_f4 = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f4 = st.selectbox(
        "Selecione o recorte temporal para a análise de Infraestrutura e Trabalho:",
        anos_opcoes_f4,
        key="fase4_ano_select"
    )
    
    def carregar_dados_socio_escola(ano):
        caminho_pasta = f"data/processed/enem_{ano}_agg_socio_escola_parquet"
        if os.path.exists(caminho_pasta):
            try:
                df = pd.read_parquet(caminho_pasta)
                df["NU_ANO"] = int(ano)
                return df
            except Exception as e:
                return pd.DataFrame()
        return pd.DataFrame()

    if ano_f4 == "Plurianual (2021-2025)":
        with st.container(border=True):
            st.markdown("<strong>📊 Visão Plurianual de Infraestrutura e Condições de Trabalho (2021–2025):</strong>", unsafe_allow_html=True)
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>O Fator Jornada (<code>Q007</code>):</strong> A série histórica plurianual evidencia que estudantes submetidos a jornadas de trabalho intensas apresentam quedas expressivas e recorrentes nas médias de desempenho da TRI, independentemente da rede de ensino, revelando o impacto exaustivo da dupla jornada juvenil.</li>
            </ul>
            """, unsafe_allow_html=True)
        
        dfs_pluri_f4 = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_socio_escola(a)
            if not df_temp.empty:
                dfs_pluri_f4.append(df_temp)
                
        if dfs_pluri_f4:
            df_pluri_socio = pd.concat(dfs_pluri_f4, ignore_index=True)
            if "Q007_DESC" in df_pluri_socio.columns and "media_matematica" in df_pluri_socio.columns:
                df_pluri_socio["Q007_DESC"] = (
                    df_pluri_socio["Q007_DESC"]
                    .astype("string")
                    .str.strip()
                    .str.rstrip(".")
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
                )
                df_pluri_socio = df_pluri_socio.dropna(subset=["Q007_DESC", "NU_ANO", "media_matematica"])
                df_pluri_socio["_condicao_chave"] = df_pluri_socio["Q007_DESC"].str.casefold()
                rotulos_condicoes = (
                    df_pluri_socio.drop_duplicates("_condicao_chave")
                    .set_index("_condicao_chave")["Q007_DESC"]
                    .to_dict()
                )
                anos_disponiveis = sorted(df_pluri_socio["NU_ANO"].astype(int).unique().tolist())
                ano_trabalho = st.selectbox(
                    "Ano para comparar as condições de trabalho:",
                    options=anos_disponiveis,
                    index=len(anos_disponiveis) - 1,
                    key="fase4_ano_trabalho_plurianual",
                )
                df_ano_trabalho = df_pluri_socio[
                    df_pluri_socio["NU_ANO"].astype(int) == ano_trabalho
                ].copy()

                if "total_candidatos" in df_ano_trabalho.columns:
                    df_ano_trabalho["_nota_ponderada"] = (
                        df_ano_trabalho["media_matematica"] * df_ano_trabalho["total_candidatos"]
                    )
                    df_trabalho_agrupado = (
                        df_ano_trabalho.groupby("_condicao_chave", as_index=False)
                        .agg(
                            total_candidatos=("total_candidatos", "sum"),
                            nota_ponderada=("_nota_ponderada", "sum"),
                        )
                    )
                    df_trabalho_agrupado["media_matematica"] = (
                        df_trabalho_agrupado["nota_ponderada"]
                        / df_trabalho_agrupado["total_candidatos"]
                    )
                else:
                    df_trabalho_agrupado = (
                        df_ano_trabalho.groupby("_condicao_chave", as_index=False)
                        .agg(media_matematica=("media_matematica", "mean"))
                    )

                df_trabalho_agrupado["Condição de Trabalho"] = df_trabalho_agrupado[
                    "_condicao_chave"
                ].map(rotulos_condicoes)
                df_trabalho_agrupado["Condição de Trabalho (completa)"] = (
                    df_trabalho_agrupado["Condição de Trabalho"]
                )
                df_trabalho_agrupado["Condição de Trabalho"] = (
                    df_trabalho_agrupado["Condição de Trabalho"]
                    .map(lambda descricao: "<br>".join(textwrap.wrap(descricao, width=24)))
                )
                with st.container(border=True):
                    fig_f4_hist = px.bar(
                        df_trabalho_agrupado,
                        x="media_matematica",
                        y="Condição de Trabalho",
                        orientation="h",
                        title=f"Média Ponderada de Matemática por Condição de Trabalho — ENEM {ano_trabalho}",
                        labels={
                            "Condição de Trabalho": "Condição de Trabalho",
                            "media_matematica": "Média Matemática (TRI)",
                        },
                        hover_data={
                            "Condição de Trabalho (completa)": True,
                            "total_candidatos": True,
                        }
                        if "total_candidatos" in df_trabalho_agrupado.columns
                        else {"Condição de Trabalho (completa)": True},
                    )
                    fig_f4_hist.update_layout(
                        template="plotly_white",
                        height=max(360, 100 + 55 * len(df_trabalho_agrupado)),
                        margin=dict(l=15, r=15, t=60, b=30),
                        showlegend=False,
                        yaxis=dict(tickfont=dict(size=10), automargin=True),
                    )
                    st.plotly_chart(fig_f4_hist, width="stretch")
    else:
        df_socio_ano = carregar_dados_socio_escola(ano_f4)
        if not df_socio_ano.empty:
            st.success(f"✅ Dados de infraestrutura e socioeconomia carregados com sucesso para o ENEM {ano_f4}.")
            
            if "TP_DEPENDENCIA_ADM_ESC_DESC" in df_socio_ano.columns:
                redes_disp: list[str] = df_socio_ano["TP_DEPENDENCIA_ADM_ESC_DESC"].unique().tolist()
                rede_sel = st.selectbox("Filtrar por Dependência Administrativa:", options=redes_disp, key=f"f4_rede_{ano_f4}")
                df_socio_ano = df_socio_ano[df_socio_ano["TP_DEPENDENCIA_ADM_ESC_DESC"] == rede_sel]
            
            if "Q006_DESC" in df_socio_ano.columns and "media_matematica" in df_socio_ano.columns and "Q007_DESC" in df_socio_ano.columns:
                with st.container(border=True):
                    fig_scatter_f4 = px.scatter(
                        df_socio_ano, x="Q006_DESC", y="media_matematica",
                        size="total_candidatos" if "total_candidatos" in df_socio_ano.columns else None,
                        color="Q007_DESC", hover_name="Q006_DESC",
                        title=f"Matriz de Impacto: Renda, Trabalho e Desempenho — ENEM {ano_f4}",
                        labels={"Q006_DESC": "Faixa de Renda", "media_matematica": "Média Matemática", "Q007_DESC": "Condição de Trabalho"}
                    )
                    fig_scatter_f4.update_layout(
                        template="plotly_white", 
                        height=420,
                        margin=dict(l=20, r=20, t=50, b=20),
                        xaxis=dict(tickangle=-35, tickfont=dict(size=10), automargin=True)
                    )
                    st.plotly_chart(fig_scatter_f4, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados agregados de socioeconomia/escola para o ano {ano_f4} não encontrados.")

    # Colunas finais estruturadas com Containers Nativos
    col_critica_f4, col_proposta_f4 = st.columns(2)
    with col_critica_f4:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica do Eixo de Trabalho e Infraestrutura")
            st.markdown("""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            Os dados demonstram que a exigência laboral precoce atua como um <strong>fator limitante crítico</strong> ao rendimento acadêmico. A ausência de suporte estrutural adequado nas instituições públicas compromete a retenção e o aproveitamento de discentes que acumulam funções profissionais e acadêmicas.
            </p>
            """, unsafe_allow_html=True)
        
    with col_proposta_f4:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Flexibilização Curricular e Apoio ao Estudante Trabalhador:</strong> Oferta de turnos alternativos e programas institucionais de mentoria voltados à gestão de tempo e apoio pedagógico direcionado.</li>
                <li><strong>Modernização Tecnológica Escolar:</strong> Expansão de infraestrutura digital e laboratórios de estudo autônomo nas unidades de ensino público periféricas.</li>
            </ul>
            """, unsafe_allow_html=True)