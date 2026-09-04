import streamlit as st
import pandas as pd
import os
import plotly.express as px

def render():
    st.markdown("---")
    
    # Bloco do Cabeçalho encapsulado em Clean Card para manter o espaçamento fluido
    st.markdown("""
    <div class="clean-card">
        <h3 style="margin-top: 0; color: #0F172A;">🌎 5. Demografia, Gênero e Desigualdades Regionais</h3>
    </div>
    """, unsafe_allow_html=True)
    
    anos_opcoes_f5 = ["Plurianual (2021-2025)", 2025, 2024, 2023, 2022, 2021]
    ano_f5 = st.selectbox(
        "Selecione o recorte temporal para a análise Demográfica e Regional:",
        anos_opcoes_f5,
        key="fase5_ano_select"
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

    if ano_f5 == "Plurianual (2021-2025)":
        st.markdown("""
        <div class="clean-card">
            <strong>📊 Visão Plurianual Demográfica e Regional (2021–2025):</strong>
            <ul style="margin-bottom: 0; padding-left: 20px;">
                <li><strong>Assimetrias Territoriais e Identitárias:</strong> A consolidação plurianual demonstra que a distribuição geográfica dos concluintes e o perfil de gênero mantêm padrões marcantes de desigualdade no acesso ao ensino superior, com concentração de melhores desempenhos nas regiões Sudeste e Sul em comparação aos estados das regiões Norte e Nordeste.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        dfs_pluri_f5 = []
        for a in [2021, 2022, 2023, 2024, 2025]:
            df_temp = carregar_dados_demografia(a)
            if not df_temp.empty:
                dfs_pluri_f5.append(df_temp)
                
        if dfs_pluri_f5:
            df_pluri_demo = pd.concat(dfs_pluri_f5, ignore_index=True)
            if "TP_SEXO_DESC" in df_pluri_demo.columns and "NU_ANO" in df_pluri_demo.columns:
                fig_f5_hist = px.bar(
                    df_pluri_demo.groupby(["NU_ANO", "TP_SEXO_DESC"])["total_candidatos"].sum().reset_index(),
                    x="NU_ANO", y="total_candidatos", color="TP_SEXO_DESC", barmode="group",
                    title="Evolução Plurianual da Participação por Gênero",
                    labels={"NU_ANO": "Ano do Exame", "total_candidatos": "Total de Inscritos", "TP_SEXO_DESC": "Gênero"}
                )
                fig_f5_hist.update_layout(
                    template="plotly_white", 
                    height=400,
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis=dict(tickfont=dict(size=11), automargin=True)
                )
                st.plotly_chart(fig_f5_hist, use_container_width=True)
    else:
        df_demo_ano = carregar_dados_demografia(ano_f5)
        if not df_demo_ano.empty:
            st.success(f"✅ Dados demográficos carregados com sucesso para o ENEM {ano_f5}.")
            
            if "TP_SEXO_DESC" in df_demo_ano.columns:
                fig_pie_f5 = px.pie(
                    df_demo_ano.groupby("TP_SEXO_DESC")["total_candidatos"].sum().reset_index(),
                    names="TP_SEXO_DESC", values="total_candidatos", hole=0.4,
                    title=f"Proporção de Participantes por Gênero — ENEM {ano_f5}",
                    color_discrete_sequence=["#ec4899", "#2563eb"]
                )
                fig_pie_f5.update_layout(
                    template="plotly_white", 
                    height=380,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig_pie_f5, use_container_width=True)
        else:
            st.warning(f"⚠️ Dados demográficos para o ano {ano_f5} não encontrados na pasta de processados.")

    # Container fluido organizado para a Análise Crítica e Proposta
    col_critica_f5, col_proposta_f5 = st.columns(2)
    with col_critica_f5:
        st.markdown("""
        <div class="clean-card" style="border-left: 4px solid #EF4444; height: 100%;">
            <h4 style="margin-top: 0; color: #991B1B;">🔍 Análise Crítica Demográfica e Regional</h4>
            <p style="margin-bottom: 0; font-size: 0.92rem; color: #334155;">
            As disparidades de gênero e raça intersectadas com as barreiras regionais revelam que o sistema educacional perpetua um funil excludente. A menor conversão de inscrições em presenças efetivas nas regiões periféricas aponta para custos de deslocamento e barreiras socioeconômicas invisibilizadas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_proposta_f5:
        st.markdown("""
        <div class="clean-card" style="border-left: 4px solid #10B981; height: 100%;">
            <h4 style="margin-top: 0; color: #065F46;">🚀 Proposta de Intervenção Baseada em Evidências</h4>
            <ul style="margin-bottom: 0; padding-left: 18px; font-size: 0.92rem; color: #334155;">
                <li><strong>Descentralização de Locais de Prova e Auxílio Transporte:</strong> Parcerias estaduais para garantir gratuidade ou facilidade logística de deslocamento em municípios de baixa densidade.</li>
                <li><strong>Ações Afirmativas Regionais:</strong> Estímulo a políticas de bonificação regional e incentivos à permanência universitária alinhadas às demandas locais.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)