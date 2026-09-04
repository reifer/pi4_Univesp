import streamlit as st
import plotly.express as px
import pandas as pd

def render_ml_view(ml_insights):
    """Renderiza o módulo de Machine Learning & IA com design fluido e responsivo."""
    
    # Cabeçalho encapsulado em Clean Card
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top: 0; color: #0F172A; font-size: 1.4rem;">🧠 Performance do Modelo Preditivo</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if ml_insights and "modelo_machine_learning" in ml_insights:
        metrics = ml_insights["modelo_machine_learning"]["metricas_avaliacao"]
        
        # Cards de Métricas Estilizados com o Padrão Clean
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="clean-card" style="text-align: center; padding: 14px;"><div class="metric-label-clean">Acurácia Global</div><div class="metric-value-clean" style="font-size: 1.5rem;">{metrics.get("accuracy", 0)*100:.2f}%</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="clean-card" style="text-align: center; padding: 14px;"><div class="metric-label-clean">ROC AUC</div><div class="metric-value-clean" style="font-size: 1.5rem;">{metrics.get("roc_auc", 0):.4f}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="clean-card" style="text-align: center; padding: 14px;"><div class="metric-label-clean">F1-Score</div><div class="metric-value-clean" style="font-size: 1.5rem;">{metrics.get("f1_score", 0):.4f}</div></div>', unsafe_allow_html=True)
        
        if "features_importantes" in ml_insights["modelo_machine_learning"]:
            st.markdown("""
            <div class="clean-card">
                <h4 style="margin-top: 0; color: #0F172A; font-size: 1.1rem;">Importância das Variáveis</h4>
            """, unsafe_allow_html=True)
            
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
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Insights de Machine Learning não encontrados.")