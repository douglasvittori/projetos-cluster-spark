# 🌾 AgroGrain Global: Previsão Preditiva do Volume de Processamento de Soja

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Apache_Spark-3.x-E25A1C.svg)](https://spark.apache.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)

Sistema de inteligência preditiva voltado ao agronegócio, desenvolvido para analisar e prever o volume diário de processamento/moagem de soja. A solução utiliza **Apache Spark** para ingestão e decomposição da série temporal, **Auto-ARIMA** para modelagem preditiva e **Streamlit** para exibição executiva.

---

## 🎯 Objetivo de Negócio

No setor agroindustrial, prever com precisão o volume diário de processamento de grãos é crucial para:
* **Otimização Logística:** Mitigar gargalos no recebimento de cargas e tempo de espera de caminhões nas moegas.
* **Planejamento de Armazenamento:** Gerenciar a capacidade estática e rotatividade de silos.
* **Governança Operacional:** Oferecer suporte à tomada de decisão na originação de matéria-prima e planejamento semanal.

---

## 🛠️ Arquitetura da Solução

O pipeline da aplicação foi estruturado de forma modular dentro do ecossistema Spark:

1. **Processamento Preditivo no Spark (Batch Pipeline):**
   * Leitura do histórico em `/datasets/processamento_soja.csv`.
   * Decomposição multiplicativa da série temporal (Tendência, Sazonalidade Semanal e Resíduos).
   * Ajuste automático de modelo **ARIMA** via `pmdarima` com geração de previsões para até 30 dias.
   * Salvamento dos artefatos estruturados em formato CSV para consumo da aplicação.

2. **Dashboard Executivo (Streamlit & Plotly):**
   * Interface Dark Mode responsiva com KPIs operacionais dinâmicos.
   * Filtro de horizonte de previsão (slider de 1 a 30 dias) com regras e alertas de governança.
   * Gráficos interativos conectando o histórico real à curva de projeção.
   * Exportação dos dados preditivos formatados.

---

## 📊 Principais Resultados Estatísticos

* **Melhor Modelo Identificado:** `ARIMA(2, 1, 4)` com intercepto.
* **Estacionaridade dos Resíduos:** Teste Dickey-Fuller Aumentado (ADF) com $p\text{-value} \approx 1.93 \times 10^{-12}$, confirmando que os resíduos se comportam como **ruído branco** (o modelo capturou os padrões estruturais da série).

---

## 📂 Estrutura do Módulo no Repositório

```text
projetos-cluster-spark/
│
├── docker-compose.yml
├── datasets/
│   └── processamento_soja.csv
│
└── projetos/
    └── projeto-volume-processamento-soja/
        ├── app.py                             # Dashboard Streamlit
        ├── projeto-volume-processamento-soja.py  # Script PySpark + ARIMA
        ├── 01-trend.csv                       # Artefato: Tendência
        ├── 02-seasonal.csv                    # Artefato: Sazonalidade
        ├── 03-residual.csv                    # Artefato: Resíduos
        ├── 04-forecast.csv                    # Artefato: Previsões ARIMA
        └── README.md                          # Documentação do projeto
```

---

## 🚀 Como Executar este Projeto

### 1. Subir o Cluster Spark (Docker)
A partir da raiz do repositório principal:
```bash
docker-compose up -d
```

### 2. Executar o Pipeline PySpark + ARIMA
Submeta o job para execução dentro do container `spark-master`:
```bash
docker exec spark-master spark-submit --deploy-mode client /opt/spark/dados/projeto-volume-processamento-soja/projeto-volume-processamento-soja.py
```

### 3. Iniciar o Dashboard Streamlit
Navegue até a pasta do projeto e inicie a aplicação web:
```bash
cd projetos/projeto-volume-processamento-soja
streamlit run app.py
```

---

## 👨‍💻 Autor

Projeto desenvolvido como parte do portfólio profissional em Engenharia de Dados, Ciência de Dados e Big Data.