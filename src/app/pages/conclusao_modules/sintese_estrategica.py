import streamlit as st
import pandas as pd
import os
import json

def render():
    st.markdown("---")
    
    # Cabeçalho encapsulado em Container Nativo
    with st.container(border=True):
        st.markdown("### 🚀 6. Visão Consolidada Plurianual (2021–2025) e o Panorama Pós-Pandemia")
    
    with st.container(border=True):
        st.markdown("<strong>🎯 A Grande Síntese Executiva:</strong>", unsafe_allow_html=True)
        st.markdown("""
        <p style="margin-top: 6px; margin-bottom: 0; color: #334155;">
        Esta seção consolida a trajetória educacional brasileira no ciclo <strong>2021–2025</strong>, mapeando os efeitos estruturais da retomada pós-pandemia, o peso dos fatores socioeconômicos e a capacidade preditiva dos algoritmos de Inteligência Artificial aplicados ao ENEM.
        </p>
        """, unsafe_allow_html=True)
    
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
        
        with st.container(border=True):
            st.markdown("#### 🧠 Validação Preditiva via Machine Learning (PI4)")
            st.markdown(f"""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #1E3A8A;">
            O modelo preditivo treinado atinge uma acurácia global de <strong>{acc:.2f}%</strong> (com ROC AUC de <strong>{auc:.4f}</strong>), atestando cientificamente que as variáveis socioeconômicas (<code>Q006</code>, <code>Q007</code>) e a dependência administrativa (<code>TP_DEPENDENCIA_ADM_ESC</code>) são os pilares determinantes para a modelagem do sucesso acadêmico.
            </p>
            """, unsafe_allow_html=True)

    # Colunas finais estruturadas com Containers Nativos
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        with st.container(border=True):
            st.markdown("#### 🔍 Conclusão Diagnóstica Plurianual")
            st.markdown("""
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            A análise longitudinal de 2021 a 2025 evidencia que <strong>as assimetrias estruturais não são acidentais, mas sistêmicas</strong>. A lentidão na recuperação dos indicadores de aprendizagem da rede pública pós-pandemia reflete a escassez crônica de investimentos contínuos em infraestrutura digital e apoio integral aos estudantes em situação de vulnerabilidade.
            </p>
            """, unsafe_allow_html=True)
        
    with col_s2:
        with st.container(border=True):
            st.markdown("#### 📋 Plano Diretor de Políticas Públicas (Diretrizes Finais)")
            st.markdown("""
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Investimento Dirigido por Evidências de IA:</strong> Alocação orçamentária prioritária para municípios e escolas identificados pelo modelo preditivo como de altíssimo risco de evasão ou baixo desempenho.</li>
                <li><strong>Ecossistema de Oportunidades Integrado:</strong> Políticas de Estado unificando assistência financeira, suporte tecnológico e contra turno escolar para romper o ciclo de reprodução das desigualdades evidenciado na série histórica.</li>
            </ul>
            """, unsafe_allow_html=True)