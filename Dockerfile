# Contexto: Imagem oficial base do Python (Leve)
# Objetivo: Conteinerizar a aplicação Streamlit e PySpark para garantir portabilidade (Fase 5.5)
# Formato: Dockerfile otimizado
# Regras: COFRE, injeção da assinatura cicd@gaaj e boas práticas de containerização
# Execução: Instruções sequenciais para construção da imagem docker

FROM python:3.11-slim

# Instala o Java (dependência obrigatória e indispensável para a execução do PySpark)
RUN apt-get update && \
    apt-get install -y default-jre && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configura o diretório de trabalho padrão do container
WORKDIR /app

# Copia a lista de requisitos para aproveitar a camada de cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código e os datasets do projeto para o container
COPY . .

# Expõe a porta padrão onde o Streamlit irá rodar
EXPOSE 8501

# [GOVERNANÇA] Variável de ambiente injetando a assinatura/identificação da chave local
ENV DEPLOY_SIGNATURE="cicd@gaaj"

# Ponto de entrada: Inicializa o Dashboard Streamlit
CMD ["streamlit", "run", "src/app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
