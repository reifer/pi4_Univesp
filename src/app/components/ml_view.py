import streamlit as st
import plotly.express as px
import pandas as pd

def render_ml_view(ml_insights, selected_years=None):
    """Renderiza o módulo de Machine Learning & IA com containers nativos responsivos."""
    selected_years = selected_years or [2025]
    
    with st.container(border=True):
        st.markdown("### 🧠 Performance do Modelo Preditivo")

    if len(selected_years) > 1:
        st.info(
            "O modelo preditivo disponível é uma referência treinada para 2025; "
            "as métricas abaixo não são recalculadas para a série plurianual."
        )
    elif selected_years[0] != 2025:
        st.warning(
            f"Não há modelo específico para {selected_years[0]}. "
            "As métricas exibidas correspondem ao modelo de referência de 2025."
        )
    
    if ml_insights and "modelo_machine_learning" in ml_insights:
        metrics = ml_insights["modelo_machine_learning"]["metricas_avaliacao"]
        
        m1, m2, m3 = st.columns(3)
        with m1:
            with st.container(border=True):
                st.metric(label="Acurácia Global", value=f"{metrics.get('accuracy', 0)*100:.2f}%")
        with m2:
            with st.container(border=True):
                st.metric(label="ROC AUC", value=f"{metrics.get('roc_auc', 0):.4f}")
        with m3:
            with st.container(border=True):
                st.metric(label="F1-Score", value=f"{metrics.get('f1_score', 0):.4f}")
        
        if "features_importantes" in ml_insights["modelo_machine_learning"]:
            with st.container(border=True):
                st.markdown("##### Importância das Variáveis")
                
                feat_df = pd.DataFrame(ml_insights["modelo_machine_learning"]["features_importantes"])
                fig_feat = px.bar(feat_df, x="importancia", y="feature", orientation="h", title="Top Features Preditivas")
                fig_feat.update_layout(
                    template="plotly_white", 
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0)", 
                    height=380,
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                st.plotly_chart(fig_feat, use_container_width=True)
    else:
        st.info("Insights de Machine Learning não encontrados.")