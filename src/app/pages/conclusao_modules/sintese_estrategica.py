import streamlit as st
import os
import json

def render():
    st.markdown("---")
    
    # Cabeçalho encapsulado em Clean Card
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top: 0; color: #0F172A;">🚀 6. Visão Consolidada Plurianual (2021–2025) e o Panorama Pós-Pandemia</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="clean-card">
        <strong>🎯 A Grande Síntese Executiva:</strong>
        <p style="margin-top: 6px; margin-bottom: 0; color: #334155;">
        Esta seção consolida a trajetória educacional brasileira no ciclo <strong>2021–2025</strong>, mapeando os efeitos estruturais da retomada pós-pandemia, o peso dos fatores socioeconômicos e a capacidade preditiva dos algoritmos de Inteligência Artificial aplicados ao ENEM.
        </p>
    </div>
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
        
        st.markdown(f"""
        <div class="clean-card" style="border-left: 4px solid #2563EB; background-color: #EFF6FF;">
            <h4 style="margin-top: 0; color: #1E40AF;">🧠 Validação Preditiva via Machine Learning (PI4)</h4>
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #1E3A8A;">
            O modelo preditivo treinado atinge uma acurácia global de <strong>{acc:.2f}%</strong> (com ROC AUC de <strong>{auc:.4f}</strong>), atestando cientificamente que as variáveis socioeconômicas (<code>Q006</code>, <code>Q007</code>) e a dependência administrativa (<code>TP_DEPENDENCIA_ADM_ESC</code>) são os pilares determinantes para a modelagem do sucesso acadêmico.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Colunas finais estruturadas com Clean Cards fluidos
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("""
        <div class="clean-card" style="border-left: 4px solid #EF4444; height: 100%;">
            <h4 style="margin-top: 0; color: #991B1B;">🔍 Conclusão Diagnóstica Plurianual</h4>
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            A análise longitudinal de 2021 a 2025 evidencia que <strong>as assimetrias estruturais não são acidentais, mas sistêmicas</strong>. A lentidão na recuperação dos indicadores de aprendizagem da rede pública pós-pandemia reflete a escassez crônica de investimentos contínuos em infraestrutura digital e apoio integral aos estudantes em situação de vulnerabilidade.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_s2:
        st.markdown("""
        <div class="clean-card" style="border-left: 4px solid #10B981; height: 100%;">
            <h4 style="margin-top: 0; color: #065F46;">📋 Plano Diretor de Políticas Públicas (Diretrizes Finais)</h4>
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Investimento Dirigido por Evidências de IA:</strong> Alocação orçamentária prioritária para municípios e escolas identificados pelo modelo preditivo como de altíssimo risco de evasão ou baixo desempenho.</li>
                <li><strong>Ecossistema de Oportunidades Integrado:</strong> Políticas de Estado unificando assistência financeira, suporte tecnológico e contra turno escolar para romper o ciclo de reprodução das desigualdades evidenciado na série histórica.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)