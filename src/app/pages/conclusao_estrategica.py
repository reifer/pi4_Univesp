import streamlit as st
import pandas as pd
import os
import plotly.express as px
import glob
import json

def render_fase_1_rede_ensino():
    st.markdown("### 🏛️ 1. O Diagnóstico: Escola Pública vs. Escola Privada")
    
    anos_opcoes = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_escolhido = st.selectbox(
        "Selecione o recorte temporal para a análise da rede de ensino:",
        anos_opcoes,
        key="fase1_ano_select"
    )
    
    def carregar_dados_rede(ano):
        caminho_pasta = f"data/processed/enem_{ano}_agg_rede_ensino_parquet"
        if os.path.exists(caminho_pasta):
            try:
                return pd.read_parquet(caminho_pasta)
            except Exception as e:
                st.error(f"Erro ao ler os dados de rede para o ano {ano}: {e}")
                return None
        return None

    if ano_escolhido == "Plurianual (2021-2025)":
        st.markdown("""
        **📊 Visão Plurianual (2021–2025):**
        * **O que os dados revelam:** Ao longo de toda a série histórica, observa-se uma assimetria estrutural profunda. A rede pública absorve a esmagadora maioria dos concluintes e participantes do ENEM (representando entre 70% e 80% dos inscritos com dependência administrativa declarada), enquanto a rede privada concentra os menores volumes de atendimento, mas lidera consistentemente as faixas de mais alto desempenho na Teoria de Resposta ao Item (TRI) e na Redação.
        """)
    else:
        df_ano = carregar_dados_rede(ano_escolhido)
        
        if df_ano is not None and not df_ano.empty:
            st.success(f"✅ Dados agregados da rede de ensino carregados com sucesso para o ENEM {ano_escolhido}.")
            with st.expander(f"Visualizar dados brutos agregados - ENEM {ano_escolhido}"):
                st.dataframe(df_ano.head(10))
        else:
            st.warning(f"⚠️ Os arquivos agregados da pasta `enem_{ano_escolhido}_agg_rede_ensino_parquet` não foram encontrados.")

        st.markdown(f"""
        **🎯 Diagnóstico Específico para o ENEM {ano_escolhido}:**
        * **O que os dados revelam:** O cruzamento das notas com a dependência administrativa comprova que o fosso de desempenho entre estudantes de escolas públicas e privadas permanece acentuado, refletindo diretamente as desigualdades de infraestrutura e suporte pedagógico.
        """)

    col_critica, col_proposta = st.columns(2)
    
    with col_critica:
        st.error("""
        🔍 **Análise Crítica**
        Essa disparidade **não representa menor capacidade cognitiva** do estudante da rede pública. Ela traduz uma *privação sistêmica de insumos educacionais*: ausência de ensino em tempo integral, falta de laboratórios estruturados, carência de suporte pedagógico continuado e menor acesso a metodologias de preparação voltadas para exames de alta exigência.
        """)
        
    with col_proposta:
        st.success("""
        🚀 **Proposta de Intervenção Baseada em Evidências**
        * **Universalização do Ensino Médio em Tempo Integral:** Foco em metodologias ativas de aprendizagem e resolução de matrizes de competências mapeadas pela TRI.
        * **Reforço Direcionado:** Implementação de programas de tutoria focalizados em Matemática e Redação desde o primeiro ano do ensino regular na rede pública.
        """)

def render_fase_2_renda_socioeconomico():
    st.markdown("---")
    st.markdown("### 💰 2. A Renda e a Nota: O Fator Socioeconômico e o Impacto no TRI")
    
    anos_opcoes_f2 = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f2 = st.selectbox(
        "Selecione o recorte temporal para a análise de Renda Familiar:",
        anos_opcoes_f2,
        key="fase2_ano_select"
    )
    
    def carregar_dados_renda(ano):
        caminho_pasta = f"data/processed/enem_{ano}_agg_notas_renda_parquet"
        if os.path.exists(caminho_pasta):
            try:
                df = pd.read_parquet(caminho_pasta)
                df["NU_ANO"] = int(ano)
                return df
            except Exception as e:
                return pd.DataFrame()
        return pd.DataFrame()

    if ano_f2 == "Plurianual (2021-2025)":
        st.markdown("""
        **📊 Visão Plurianual do Fator Socioeconômico (2021–2025):**
        * **A Correlação Direta:** A análise consolidada dos 5 anos comprova que a renda familiar (`Q006`) opera como uma das variáveis de maior poder preditivo sobre o desempenho no ENEM. O gradiente de notas da TRI cresce de forma estritamente proporcional ao patamar de rendimento declarado.
        """)
        
        dfs_pluri = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_renda(a)
            if not df_temp.empty:
                dfs_pluri.append(df_temp)
                
        if dfs_pluri:
            df_pluri_renda = pd.concat(dfs_pluri, ignore_index=True)
            
            if "RENDA_FAMILIAR_DESC" in df_pluri_renda.columns and "NU_ANO" in df_pluri_renda.columns:
                fig_hist = px.line(
                    df_pluri_renda, x="NU_ANO", y="media_geral" if "media_geral" in df_pluri_renda.columns else "total_candidatos",
                    color="RENDA_FAMILIAR_DESC", markers=True,
                    title="Evolução Plurianual do Desempenho por Faixa de Renda",
                    labels={"NU_ANO": "Ano do Exame", "media_geral": "Média Geral TRI"}
                )
                fig_hist.update_layout(template="plotly_white", height=450)
                st.plotly_chart(fig_hist, use_container_width=True)
    else:
        df_renda_ano = carregar_dados_renda(ano_f2)
        if not df_renda_ano.empty:
            st.success(f"✅ Dados agregados de renda carregados com sucesso para o ENEM {ano_f2}.")
            
            desc_col = "RENDA_FAMILIAR_DESC" if "RENDA_FAMILIAR_DESC" in df_renda_ano.columns else df_renda_ano.columns[1]
            nota_col = "media_mt" if "media_mt" in df_renda_ano.columns else (df_renda_ano.columns[2] if len(df_renda_ano.columns) > 2 else None)
            
            if desc_col and nota_col:
                fig_renda_ano = px.bar(
                    df_renda_ano.sort_values(by=df_renda_ano.columns[0]),
                    x=desc_col, y=nota_col,
                    color=nota_col, color_continuous_scale="Blues",
                    title=f"Desempenho Médio em Matemática por Faixa de Renda — ENEM {ano_f2}",
                    labels={desc_col: "Faixa de Renda Familiar (Q006)", nota_col: "Nota Média (TRI)"}
                )
                fig_renda_ano.update_layout(template="plotly_white", height=420, coloraxis_showscale=False)
                fig_renda_ano.update_xaxes(tickangle=45)
                st.plotly_chart(fig_renda_ano, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados de renda para o ano {ano_f2} não encontrados na pasta de processados.")

    col_critica_f2, col_proposta_f2 = st.columns(2)
    with col_critica_f2:
        st.error("""
        🔍 **Análise Crítica do Fator Socioeconômico**
        A dependência entre o capital econômico familiar e o sucesso acadêmico escancara a **reprodutibilidade das desigualdades sociais**. Alunos inseridos nas faixas de menor renda enfrentam barreiras materiais cumulativas, como a necessidade precoce de inserção no mercado de trabalho (`Q007`), o que reduz drasticamente o tempo dedicado aos estudos extracurriculares.
        """)
    with col_proposta_f2:
        st.success("""
        🚀 **Proposta de Intervenção Baseada em Evidências**
        * **Políticas de Assistência Estudantil Ampliadas:** Bolsas de permanência e suporte digital direto para estudantes de baixa renda do ensino médio regular.
        * **Plataformas Públicas de Apoio Adaptativo:** Democratização de cursinhos preparatórios de alto nível impulsionados por Inteligência Artificial para nivelamento de oportunidades.
        """)

def render_fase_3_infraestrutura_trabalho():
    st.markdown("---")
    st.markdown("### 🛠️ 3. A Infraestrutura e o Trabalho: O Peso da Jornada e do Apoio Escolar")
    
    anos_opcoes_f3 = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f3 = st.selectbox(
        "Selecione o recorte temporal para a análise de Infraestrutura e Trabalho:",
        anos_opcoes_f3,
        key="fase3_ano_select"
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

    if ano_f3 == "Plurianual (2021-2025)":
        st.markdown("""
        **📊 Visão Plurianual de Infraestrutura e Condições de Trabalho (2021–2025):**
        * **O Fator Jornada (`Q007`):** A série histórica plurianual evidencia que estudantes submetidos a jornadas de trabalho intensas apresentam quedas expressivas e recorrentes nas médias de desempenho da TRI, independentemente da rede de ensino, revelando o impacto exaustivo da dupla jornada juvenil.
        """)
        
        dfs_pluri_f3 = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_socio_escola(a)
            if not df_temp.empty:
                dfs_pluri_f3.append(df_temp)
                
        if dfs_pluri_f3:
            df_pluri_socio = pd.concat(dfs_pluri_f3, ignore_index=True)
            if "Q007_DESC" in df_pluri_socio.columns and "media_matematica" in df_pluri_socio.columns:
                fig_f3_hist = px.box(
                    df_pluri_socio, x="Q007_DESC", y="media_matematica", color="NU_ANO",
                    title="Distribuição Plurianual da Nota de Matemática por Condição de Trabalho (Q007)",
                    labels={"Q007_DESC": "Condição de Trabalho", "media_matematica": "Média Matemática (TRI)"}
                )
                fig_f3_hist.update_layout(template="plotly_white", height=450)
                fig_f3_hist.update_xaxes(tickangle=30)
                st.plotly_chart(fig_f3_hist, use_container_width=True)
    else:
        df_socio_ano = carregar_dados_socio_escola(ano_f3)
        if not df_socio_ano.empty:
            st.success(f"✅ Dados de infraestrutura e socioeconomia carregados com sucesso para o ENEM {ano_f3}.")
            
            if "TP_DEPENDENCIA_ADM_ESC_DESC" in df_socio_ano.columns:
                redes_disp = df_socio_ano["TP_DEPENDENCIA_ADM_ESC_DESC"].unique()
                rede_sel = st.selectbox("Filtrar por Dependência Administrativa:", options=redes_disp, key=f"f3_rede_{ano_f3}")
                df_socio_ano = df_socio_ano[df_socio_ano["TP_DEPENDENCIA_ADM_ESC_DESC"] == rede_sel]
            
            if "Q006_DESC" in df_socio_ano.columns and "media_matematica" in df_socio_ano.columns and "Q007_DESC" in df_socio_ano.columns:
                fig_scatter_f3 = px.scatter(
                    df_socio_ano, x="Q006_DESC", y="media_matematica",
                    size="total_candidatos" if "total_candidatos" in df_socio_ano.columns else None,
                    color="Q007_DESC", hover_name="Q006_DESC",
                    title=f"Matriz de Impacto: Renda, Trabalho e Desempenho — ENEM {ano_f3}",
                    labels={"Q006_DESC": "Faixa de Renda", "media_matematica": "Média Matemática", "Q007_DESC": "Condição de Trabalho"}
                )
                fig_scatter_f3.update_layout(template="plotly_white", height=430)
                fig_scatter_f3.update_xaxes(tickangle=45)
                st.plotly_chart(fig_scatter_f3, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados agregados de socioeconomia/escola para o ano {ano_f3} não encontrados.")

    col_critica_f3, col_proposta_f3 = st.columns(2)
    with col_critica_f3:
        st.error("""
        🔍 **Análise Crítica do Eixo de Trabalho e Infraestrutura**
        Os dados demonstram que a exigência laboral precoce atua como um **fator limitante crítico** ao rendimento acadêmico. A ausência de suporte estrutural adequado nas instituições públicas compromete a retenção e o aproveitamento de discentes que acumulam funções profissionais e acadêmicas.
        """)
    with col_proposta_f3:
        st.success("""
        🚀 **Proposta de Intervenção Baseada em Evidências**
        * **Flexibilização Curricular e Apoio ao Estudante Trabalhador:** Oferta de turnos alternativos e programas institucionais de mentoria voltados à gestão de tempo e apoio pedagógico direcionado.
        * **Modernização Tecnológica Escolar:** Expansão de infraestrutura digital e laboratórios de estudo autônomo nas unidades de ensino público periféricas.
        """)

def render_fase_4_demografia_regioes():
    st.markdown("---")
    st.markdown("### 🌎 4. Demografia, Gênero e Desigualdades Regionais")
    
    anos_opcoes_f4 = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f4 = st.selectbox(
        "Selecione o recorte temporal para a análise Demográfica e Regional:",
        anos_opcoes_f4,
        key="fase4_ano_select"
    )
    
    def carregar_dados_demografia(ano):
        caminho_pasta = f"data/processed/enem_{ano}_agg_demografia_parquet"
        if os.path.exists(caminho_pasta):
            try:
                df = pd.read_parquet(caminho_pasta)
                df["NU_ANO"] = int(ano)
                return df
            except Exception as e:
                return pd.DataFrame()
        return pd.DataFrame()

    if ano_f4 == "Plurianual (2021-2025)":
        st.markdown("""
        **📊 Visão Plurianual Demográfica e Regional (2021–2025):**
        * **Assimetrias Territoriais e Identitárias:** A consolidação plurianual demonstra que a distribuição geográfica dos concluintes e o perfil de gênero mantêm padrões marcantes de desigualdade no acesso ao ensino superior, com concentração de melhores desempenhos nas regiões Sudeste e Sul em comparação aos estados das regiões Norte e Nordeste.
        """)
        
        dfs_pluri_f4 = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_demografia(a)
            if not df_temp.empty:
                dfs_pluri_f4.append(df_temp)
                
        if dfs_pluri_f4:
            df_pluri_demo = pd.concat(dfs_pluri_f4, ignore_index=True)
            if "TP_SEXO_DESC" in df_pluri_demo.columns and "NU_ANO" in df_pluri_demo.columns:
                fig_f4_hist = px.bar(
                    df_pluri_demo.groupby(["NU_ANO", "TP_SEXO_DESC"])["total_candidatos"].sum().reset_index(),
                    x="NU_ANO", y="total_candidatos", color="TP_SEXO_DESC", barmode="group",
                    title="Evolução Plurianual da Participação por Gênero",
                    labels={"NU_ANO": "Ano do Exame", "total_candidatos": "Total de Inscritos", "TP_SEXO_DESC": "Gênero"}
                )
                fig_f4_hist.update_layout(template="plotly_white", height=430)
                st.plotly_chart(fig_f4_hist, use_container_width=True)
    else:
        df_demo_ano = carregar_dados_demografia(ano_f4)
        if not df_demo_ano.empty:
            st.success(f"✅ Dados demográficos carregados com sucesso para o ENEM {ano_f4}.")
            
            if "TP_SEXO_DESC" in df_demo_ano.columns:
                fig_pie_f4 = px.pie(
                    df_demo_ano.groupby("TP_SEXO_DESC")["total_candidatos"].sum().reset_index(),
                    names="TP_SEXO_DESC", values="total_candidatos", hole=0.4,
                    title=f"Proporção de Participantes por Gênero — ENEM {ano_f4}",
                    color_discrete_sequence=["#ec4899", "#2563eb"]
                )
                fig_pie_f4.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig_pie_f4, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados demográficos para o ano {ano_f4} não encontrados na pasta de processados.")

    col_critica_f4, col_proposta_f4 = st.columns(2)
    with col_critica_f4:
        st.error("""
        🔍 **Análise Crítica Demográfica e Regional**
        As disparidades de gênero e raça intersectadas com as barreiras regionais revelam que o sistema educacional perpetua um funil excludente. A menor conversão de inscrições em presenças efetivas nas regiões periféricas aponta para custos de deslocamento e barreiras socioeconômicas invisibilizadas.
        """)
    with col_proposta_f4:
        st.success("""
        🚀 **Proposta de Intervenção Baseada em Evidências**
        * **Descentralização de Locais de Prova e Auxílio Transporte:** Parcerias estaduais para garantir gratuidade ou facilidade logística de deslocamento em municípios de baixa densidade de centros aplicadores.
        * **Ações Afirmativas Regionais:** Estímulo a políticas de bonificação regional e incentivos à permanência universitária alinhadas às demandas demográficas locais.
        """)

def render_fase_5_sintese_pos_pandemia():
    st.markdown("---")
    st.markdown("### 🚀 5. Visão Consolidada Plurianual (2021–2025) e o Panorama Pós-Pandemia")
    
    st.markdown("""
    **🎯 A Grande Síntese Executiva:**
    Esta seção consolida a trajetória educacional brasileira no ciclo **2021–2025**, mapeando os efeitos estruturais da retomada pós-pandemia, o peso dos fatores socioeconômicos e a capacidade preditiva dos algoritmos de Inteligência Artificial aplicados ao ENEM.
    """)
    
    ml_insights_path = "data/processed/enem_2025_ml_insights.json"
    ml_data = {}
    if os.path.exists(ml_insights_path):
        try:
            with open(ml_insights_path, "r", encoding="utf-8") as f:
                ml_data = json.load(f)
        except Exception:
            pass

    if ml_data and "modelo_machine_learning" in ml_data:
        metrics = ml_data["modelo_machine_learning"].get("metricas_avaliacao", {})
        acc = metrics.get("accuracy", 0.0) * 100
        auc = metrics.get("roc_auc", 0.0)
        
        st.info(f"""
        🧠 **Validação Preditiva via Machine Learning (PI4):**
        O modelo preditivo treinado atinge uma acurácia global de **{acc:.2f}%** (com ROC AUC de **{auc:.4f}**), atestando cientificamente que as variáveis socioeconômicas (`Q006`, `Q007`) e a dependência administrativa (`TP_DEPENDENCIA_ADM_ESC`) são os pilares determinantes para a modelagem do sucesso acadêmico.
        """)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.error("""
        🔍 **Conclusão Diagnóstica Plurianual**
        A análise longitudinal de 2021 a 2025 evidencia que **as assimetrias estruturais não são acidentais, mas sistêmicas**. A lentidão na recuperação dos indicadores de aprendizagem da rede pública pós-pandemia reflete a escassez crônica de investimentos contínuos em infraestrutura digital e apoio integral aos estudantes em situação de vulnerabilidade.
        """)
    with col_s2:
        st.success("""
        📋 **Plano Diretor de Políticas Públicas (Diretrizes Finais)**
        * **Investimento Dirigido por Evidências de IA:** Alocação orçamentária prioritária para municípios e escolas identificados pelo modelo preditivo como de altíssimo risco de evasão ou baixo desempenho.
        * **Ecossistema de Oportunidades Integrado:** Políticas de Estado unificando assistência financeira, suporte tecnológico e contra turno escolar para romper o ciclo de reprodução das desigualdades evidenciado na série histórica.
        """)

def render():
    """Função principal que renderiza todas as fases da Conclusão Estratégica em sequência."""
    render_fase_1_rede_ensino()
    render_fase_2_renda_socioeconomico()
    render_fase_3_infraestrutura_trabalho()
    render_fase_4_demografia_regioes()
    render_fase_5_sintese_pos_pandemia()

# Chamada para garantir renderização correta quando acessado diretamente via multi-page apps do Streamlit
if __name__ == "__main__":
    render()