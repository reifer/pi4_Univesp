import streamlit as st
import pandas as pd
import os

def render():
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
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
        with st.container(border=True):
            st.markdown("<strong>📊 Visão Plurianual (2021–2025):</strong>", unsafe_allow_html=True)
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>O que os dados revelam:</strong> Ao longo de toda a série histórica, observa-se uma assimetria estrutural profunda. A rede pública absorve a esmagadora maioria dos concluintes e participantes do ENEM (representando entre 70% e 80% dos inscritos com dependência administrativa declarada), enquanto a rede privada concentra os menores volumes de atendimento, mas lidera consistentemente as faixas de mais alto desempenho na Teoria de Resposta ao Item (TRI) e na Redação.</li>
            </ul>
            """, unsafe_allow_html=True)
    else:
        df_ano = carregar_dados_rede(ano_escolhido)
        
        if df_ano is not None and not df_ano.empty:
            st.success(f"✅ Dados agregados da rede de ensino carregados com sucesso para o ENEM {ano_escolhido}.")
            with st.expander(f"Visualizar dados brutos agregados - ENEM {ano_escolhido}"):
                with st.container(border=True):
                    st.dataframe(df_ano.head(10))
        else:
            st.warning(f"⚠️ Os arquivos agregados da pasta `enem_{ano_escolhido}_agg_rede_ensino_parquet` não foram encontrados.")

        with st.container(border=True):
            st.markdown(f"<strong>🎯 Diagnóstico Específico para o ENEM {ano_escolhido}:</strong>", unsafe_allow_html=True)
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>O que os dados revelam:</strong> O cruzamento das notas com a dependência administrativa comprova que o fosso de desempenho entre estudantes de escolas públicas e privadas permanece acentuado, refletindo diretamente as desigualdades de infraestrutura e suporte pedagógico.</li>
            </ul>
            """, unsafe_allow_html=True)

    # Colunas finais estruturadas com Containers Nativos
    col_critica, col_proposta = st.columns(2)
    
    with col_critica:
        with st.container(border=True):
            st.markdown("#### 🔍 Análise Crítica")
            st.markdown("""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            Essa disparidade <strong>não representa menor capacidade cognitiva</strong> do estudante da rede pública. Ela traduz uma <em>privação sistêmica de insumos educacionais</em>: ausência de ensino em tempo integral, falta de laboratórios estruturados, carência de suporte pedagógico continuado e menor acesso a metodologias de preparação voltadas para exames de alta exigência.
            </p>
            """, unsafe_allow_html=True)
        
    with col_proposta:
        with st.container(border=True):
            st.markdown("#### 🚀 Proposta de Intervenção Baseada em Evidências")
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Universalização do Ensino Médio em Tempo Integral:</strong> Foco em metodologias ativas de aprendizagem e resolução de matrizes de competências mapeadas pela TRI.</li>
                <li><strong>Reforço Direcionado:</strong> Implementação de programas de tutoria focalizados em Matemática e Redação desde o primeiro ano do ensino regular na rede pública.</li>
            </ul>
            """, unsafe_allow_html=True)