import streamlit as st
import plotly.express as px
import pandas as pd

def render_ml_view(ml_insights):
    """Renderiza o módulo de Machine Learning & IA."""
    st.subheader("🧠 Performance do Modelo Preditivo")
    if ml_insights and "modelo_machine_learning" in ml_insights:
        metrics = ml_insights["modelo_machine_learning"]["metricas_avaliacao"]
        m1, m2, m3 = st.columns(3)
        with m1: st.metric(label="Acurácia Global", value=f"{metrics.get('accuracy', 0)*100:.2f}%")
        with m2: st.metric(label="ROC AUC", value=f"{metrics.get('roc_auc', 0):.4f}")
        with m3: st.metric(label="F1-Score", value=f"{metrics.get('f1_score', 0):.4f}")
        
        st.markdown("---")
        st.markdown("##### Importância das Variáveis")
        if "features_importantes" in ml_insights["modelo_machine_learning"]:
            feat_df = pd.DataFrame(ml_insights["modelo_machine_learning"]["features_importantes"])
            fig_feat = px.bar(feat_df, x="importancia", y="feature", orientation="h", title="Top Features Preditivas")
            fig_feat.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig_feat, width="stretch")
    else:
        st.info("Insights de Machine Learning não encontrados.")