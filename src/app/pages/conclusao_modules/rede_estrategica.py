import streamlit as st
from app.utils.data_loader import get_global_filter_state, load_filtered_aggregate

def render():
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
        st.markdown("### 🏛️ 1. O Diagnóstico: Escola Pública vs. Escola Privada")
    
    selected_years, selected_ufs, selected_treineiros = get_global_filter_state()
    df_rede = load_filtered_aggregate("agg_rede_ensino")
    if df_rede.empty:
        st.info("Não há dados de rede de ensino para os filtros globais atuais.")
    else:
        years_label = ", ".join(str(year) for year in selected_years)
        with st.container(border=True):
            st.markdown(
                f"<strong>📊 Diagnóstico do recorte global ({years_label}):</strong>",
                unsafe_allow_html=True,
            )
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>O que os dados revelam:</strong> A comparação entre dependências administrativas permite identificar diferenças de participação e desempenho dentro do recorte de ano, UF e tipo de candidato selecionado no painel.</li>
            </ul>
            """, unsafe_allow_html=True)
        summary = df_rede.groupby(
            "TP_DEPENDENCIA_ADM_ESC_DESC", as_index=False
        )["total_candidatos"].sum()
        st.dataframe(summary, hide_index=True, width="stretch")
        st.caption(
            f"Filtros globais — UFs: {', '.join(selected_ufs)} · "
            f"candidatos: {', '.join(selected_treineiros)}"
        )

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