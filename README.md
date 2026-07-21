# 🚀 Cluster Apache Spark & Repositório de Projetos

Este repositório centraliza a infraestrutura de um **cluster Apache Spark rodando em containers Docker**, servindo como ambiente para o desenvolvimento e execução de projetos práticos de Engenharia de Dados, Análise Preditiva e Séries Temporais.

---

## 🛠️ Arquitetura e Infraestrutura do Cluster

O ambiente foi configurado para simular um ecossistema de processamento distribuído utilizando **Docker Compose**:

* **Apache Spark (Master & Workers):** Processamento distribuído e escalável em lote (batch).
* **Jupyter Lab / Python:** Ambiente integrado para desenvolvimento, prototipagem e execução de scripts PySpark.
* **Mapeamento de Volumes:** Integração e persistência entre o sistema operacional local e o ambiente isolado do Linux nos containers (`/projetos` e `/datasets`).

---

## 📂 Estrutura do Repositório

projetos-cluster-spark/
├── config/                  # Configurações internas do ambiente Spark
├── datasets/                # Conjuntos de dados dos projetos
│   └── projeto_trafego_internet/
│       └── previsoesdeploy/ # Saídas do modelo: arquivos CSV e gráficos gerados
├── projetos/                # Código-fonte e scripts de processamento
│   └── projeto_trafego_internet/
│       ├── treino.py        # Pipeline de pré-processamento e treinamento do modelo
│       └── deploy.py        # Inferência/previsão em lote
├── requirements/            # Dependências Python instaladas no cluster
├── .gitignore               # Regras de exclusão do Git
├── docker-compose.yml       # Orquestração dos containers Docker do Spark
└── README.md                # Documentação do repositório

---

## 📊 Projetos Incluídos

### 1. Previsão de Tráfego e Consumo de Dados de Internet (Séries Temporais)

* **Problema de Negócio:** Projetar a demanda futura de tráfego de dados em redes de internet é fundamental para prever gargalos de infraestrutura, otimizar a alocação de largura de banda e evitar quedas no serviço durante picos de consumo.
* **Abordagem Técnica:** 
  * Desenvolvimento de pipeline preditivo em PySpark/Python utilizando técnicas de análise de séries temporais.
  * Execução distribuída do treinamento e geração de inferências em ambiente clusterizado Spark.
* **Entregáveis do Pipeline:**
  * `treino.py`: Carregamento do histórico de tráfego, tratamento da série temporal e treinamento do modelo estatístico/preditivo.
  * `deploy.py`: Execução das previsões em lote e exportação do resultado consolidado em formato CSV (`previsoes_consumo_dados.csv`).
  * `dataviz.py`: Script de suporte para validação visual, gerando o gráfico comparativo entre valores reais e previstos (`projeto-consumo-dados.png`).

---

## ⚡ Como Executar o Ambiente

1. **Subir o Cluster Spark:**
   `docker compose up -d`

2. **Acessar/Verificar Containers:**
   `docker ps`

3. **Executar Scripts no Cluster:**
   `docker exec -it <NOME_DO_CONTAINER_MASTER> spark-submit /projetos/projeto_trafego_internet/deploy.py`