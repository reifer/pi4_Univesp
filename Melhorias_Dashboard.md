# 📋 Roadmap de Execução & Checklist de Progresso: Dashboard ENEM Reativo

Este documento consolida o planejamento arquitetural e serve como o guia oficial de acompanhamento e auditoria para a implementação da **Reatividade Global Inteligente** no Dashboard do ENEM (PI4 Univesp).

---

## 🎯 Visão Geral da Arquitetura Reativa

O objetivo desta refatoração é transformar o dashboard em uma aplicação analítica de alta performance e reatividade instantânea, orientada por três filtros transversais:
1. **Recorte Temporal (Ano):** Suporte a seleção de ano único, série histórica contínua (ex: 2021–2025) ou anos mistos personalizados (ex: 2021, 2023, 2025).
2. **Tipo de Candidato:** Filtro universal (Treineiros vs. Não Treineiros / Regulares).
3. **Unidades Federativas (UFs):** Seleção flexível de múltiplos estados (ou Brasil inteiro).

### ⚡ Estratégia de Performance (Anti-OOM)
Para evitar o consumo excessivo de memória RAM (>15 GB) e lentidão ao processar ~20 milhões de registros em tempo de execução, a aplicação adotará **Cubos OLAP Pré-Agregados no PySpark**. Todas as agregações incluirão nativamente as dimensões `(NU_ANO, SG_UF_PROVA, IN_TREINEIRO)`, gerando arquivos compactos (<3 MB) que permitem reagregações ponderadas instantâneas em Pandas.

---

## 🏗️ Fases de Implementação & Checklist

---

### Fase 1: Engenharia de Dados & Cubos OLAP no PySpark

> **Objetivo:** Enriquecer e padronizar as tabelas agregadas no pipeline PySpark para que todas contenham as dimensões de UF, Treineiro e Ano, além das métricas necessárias para médias ponderadas.

- [x] **1.1. Refatoração do Schema de Agregações em `src/data_pipeline/parser.py`**
  - [x] Adicionar `IN_TREINEIRO` e `IN_TREINEIRO_DESC` na agregação de Rede de Ensino (`agg_rede_ensino_parquet`).
  - [x] Adicionar `SG_UF_PROVA` na agregação de Notas por Renda Canônica (`agg_notas_renda_parquet`).
  - [x] Adicionar `SG_UF_PROVA`, `IN_TREINEIRO` e `IN_TREINEIRO_DESC` na agregação de Renda x Raça/Cor (`agg_renda_raca_parquet`).
  - [x] Adicionar `SG_UF_PROVA`, `IN_TREINEIRO` e `IN_TREINEIRO_DESC` na agregação Socioeconômica da Escola (`agg_socio_escola_parquet`).
  - [x] Incluir numeradores de apoio (ex: contagem de provas válidas e somatórios de notas) para permitir reagregações ponderadas exatas em tempo de execução.

- [x] **1.2. Reexecução do Pipeline de Transformação Histórica**
  - [x] Executar o pipeline `transform.py` para os anos de 2021, 2022, 2023, 2024 e 2025.
  - [x] Validar a integridade dos schemas gerados em `data/processed/enem_{ANO}_agg_*_parquet`.
  - [x] Auditar a volumetria e o tamanho dos arquivos Parquet resultantes (garantir tamanho < 5 MB no total consolidado).

- [x] **1.3. Porta de Qualidade 1 (Validação de Dados)**
  - [x] Verificar ausência de valores nulos críticos nas chaves dimensionais (`NU_ANO`, `SG_UF_PROVA`, `IN_TREINEIRO`).
  - [x] Validar consistência entre o total de candidatos por UF nos cubos agregados e o total real dos microdados.

---

### Fase 2: Arquitetura de Estado Global & Data Loader

> **Objetivo:** Estabelecer o gerenciamento de estado via `st.session_state` e modernizar o carregador de dados para suportar múltiplos anos de forma leve e segura.

- [x] **2.1. Centralização do Estado no `dashboard.py`**
  - [x] Inicializar e padronizar as chaves no `st.session_state`:
    - `st.session_state["filter_years"]`: Lista de anos selecionados.
    - `st.session_state["filter_ufs"]`: Lista de siglas de UFs selecionadas.
    - `st.session_state["filter_treineiro"]`: Lista de rótulos/valores selecionados ("Treineiro", "Não Treineiro").
  - [x] Implementar seletor temporal flexível na barra superior:
    - Botões rápidos/Presets: `[Ano Mais Recente (2025)]`, `[Série Completa (2021–2025)]`, `[Personalizado]`.
    - Multiselect dinâmico de anos suportando seleções arbitrárias (ex: 2021 + 2024).

- [x] **2.2. Reestruturação do Carregador em `src/app/utils/data_loader.py`**
  - [x] Descontinuar a amostragem truncada de 100.000 linhas de `df_raw` via `scanner.to_batches()`.
  - [x] Criar função `@st.cache_data` para carregar e concatenar sob demanda apenas os arquivos agregados dos anos ativos em `st.session_state["filter_years"]`.
  - [x] Implementar utilitário padronizado de **Média Ponderada Dinâmica** (`calc_weighted_mean`) para recomputação segura em Pandas sem incorrer no Paradoxo de Simpson.

- [x] **2.3. Adaptação dos Cards KPI do Topo**
  - [x] Conectar os 4 cartões de KPI (Total de Inscritos, Treineiros, Regulares e Estado Destaque) à matriz tridimensional filtrada em memória.
  - [x] Validar comportamento dos KPIs na seleção de múltiplos anos e estados.

- [x] **2.4. Porta de Qualidade 2 (Validação de Estado)**
  - [x] Confirmar que alterações nos filtros de topo disparam recálculo instantâneo sem vazamento de memória ou erros de chave.

---

### Fase 3: Propagação Reativa nos Módulos de Visualização

> **Objetivo:** Atualizar todos os componentes para consumirem o estado global e reagirem em uníssono aos filtros de Ano, UF e Treineiro.

- [x] **3.1. Módulo: 📊 Panorama Geográfico (`src/app/components/geo_view.py`)**
  - [x] Suportar filtragem combinada de múltiplos anos, recalculando o ranking de UFs por soma ponderada.
  - [x] Atualizar o gráfico de distribuição por sexo (`TP_SEXO_DESC`) para respeitar a seleção de treineiros e anos mistos.

- [x] **3.2. Módulo: 💰 Perfil Socioeconômico (`src/app/components/socio_view.py`)**
  - [x] Conectar a visualização de faixas de renda (`Q006` / `RENDA_FAMILIAR`) ao filtro geográfico de UFs (habilitado pela Fase 1).
  - [x] Garantir ordenação correta das classes econômicas na consolidação de múltiplos anos.

- [x] **3.3. Módulo: 🏫 Redes de Ensino (`src/app/components/rede_view.py`)**
  - [x] Aplicar o filtro de Tipo de Candidato (Treineiro vs. Regular) em todas as seções (Volumetria, Donut e Barras Agrupadas).
  - [x] Atualizar a série histórica temporal para destacar ou restringir-se aos anos ativos no filtro global.
  - [x] Adequar o Raio-X Avançado (`Q006` x `Q007` x Rede) para respeitar os filtros de UF e Treineiro.

- [x] **3.4. Módulo: 📈 Desempenho TRI (`src/app/components/desempenho_view.py`)**
  - [x] Aplicar o filtro de Treineiros nas métricas de topo e nos gráficos por disciplina.
  - [x] Substituir agregações `.mean()` simples por agregação ponderada pelo volume de candidatos.
  - [x] Viabilizar comparativo de desempenho agregado para seleções plurianuais.

- [x] **3.5. Módulo: 🌎 Geopolítica (`src/app/components/geopolitica_view.py`)**
  - [x] Conectar o agrupamento regional (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) aos filtros de UFs e Treineiros.
  - [x] Substituir média aritmética das regiões por ponderação demográfica real.
  - [x] Sincronizar o gráfico de evolução nacional plurianual com a janela temporal selecionada no painel.

- [x] **3.6. Módulo: 🤖 Machine Learning (`src/app/components/ml_view.py`)**
  - [x] Ajustar carregamento do modelo preditivo para o ano correspondente quando selecionado ano único, ou exibir metadados do modelo de referência (2025) com aviso contextual quando em série plurianual.

- [x] **3.7. Porta de Qualidade 3 (Validação Visual)**
  - [x] Testar navegação entre todas as abas com combinações extremas (ex: 1 estado + apenas treineiros; todos os estados + 5 anos mistos).

---

### Fase 4: Harmonização da Conclusão Estratégica & Blindagem de Testes

> **Objetivo:** Integrar a narrativa qualitativa e as diretrizes de políticas públicas ao contexto analítico do dashboard, finalizando com validação por testes automatizados.

- [x] **4.1. Refatoração dos Submódulos da Conclusão Estratégica (`src/app/pages/conclusao_modules/`)**
  - [x] `rede_estrategica.py`: Remover `st.selectbox` redundante e conectar os diagnósticos ao recorte temporal e geográfico global.
  - [x] `renda_estrategica.py`: Harmonizar o carregamento com a base tratada de renda por UF/Treineiro.
  - [x] `raca_estrategica.py`: Integrar aos filtros transversais ativos.
  - [x] `trabalho_estrategica.py`: Conectar a matriz trabalho/renda aos dados reativos.
  - [x] `demografia_estrategica.py`: Sincronizar pirâmide e distribuição demográfica com o estado global.
  - [x] `sintese_estrategica.py`: Manter alinhamento contextual das diretrizes executivas e do modelo preditivo.

- [x] **4.2. Atualização e Ampliação da Suíte de Testes (`tests/`)**
  - [x] Atualizar `tests/test_views.py` para validar a renderização de todas as views com o novo contrato de estado.
  - [x] Criar testes unitários para a função de cálculo de média ponderada (`test_weighted_aggregations`).
  - [x] Criar testes para validar que nenhuma view lança exceção quando filtros resultam em subconjuntos vazios ou unitários.
  - [x] Executar bateria completa com `pytest` e garantir 100% de aprovação.

- [x] **4.3. Porta de Qualidade 4 (Homologação Final)**
  - [x] Verificação da responsividade da interface e validação final de desempenho.

---

## 📌 Registro de Atualizações e Mudanças

| Data | Fase / Item | Responsável | Descrição do Avanço |
| :---: | :---: | :---: | :--- |
| *24/10/2026* | Inicialização | Engenharia / PI4 | Criação do Roadmap oficial e checklist após conclusão da auditoria técnica. |
| *24/10/2026* | Fase 1 | Engenharia / PI4 | Cubos atualizados para 2021–2025; Porta 1 aprovada e agregados consolidados em 4,35 MB. |
| *24/10/2026* | Fase 2 | Engenharia / PI4 | Filtros globais e loader cacheado de agregados implementados; Porta 2 validada com AppTest. |
| *24/10/2026* | Fase 3 | Engenharia / PI4 | Filtros propagados às views centrais; médias reagregadas por somas/contagens de notas válidas e Porta 3 validada em cenários extremos. |
| *24/10/2026* | Fase 4 | Engenharia / PI4 | Submódulos estratégicos harmonizados; suíte completa com 52 testes aprovada, compilação e diff sem erros; aplicação respondeu HTTP 200 e Porta 4 aprovada. |
