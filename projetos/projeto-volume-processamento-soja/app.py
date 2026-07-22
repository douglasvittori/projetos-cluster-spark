import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. Configuração da Página
st.set_page_config(
    page_title="AgroGrain - Forecasting de Processamento de Soja",
    page_icon="🌾",
    layout="wide",
)

# Estilo personalizado para os cards e alertas
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #0056b3;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,  # Parâmetro correto
)

st.title("🌾 AgroGrain Global | Pipeline Preditivo de Originação de Soja")
st.caption(
    "Dashboard executivo integrado ao ecossistema Apache Spark e modelos de Séries Temporais (ARIMA)."
)
st.markdown("---")


# Função de Carregamento dos Dados com Busca Dinâmica
@st.cache_data
def carregar_dados():
    # 1. Mapeia o diretório onde o próprio app.py está localizado
    DIR_ATUAL = Path(__file__).resolve().parent

    # 2. Lista de possíveis caminhos para os arquivos (ordem de prioridade)
    caminhos_possiveis = [
        # Opção 1: Pasta 'datasets' subindo duas pastas (projetos-cluster-spark/datasets)
        DIR_ATUAL.parents[1] / "datasets" / "projeto-volume-processamento-soja",
        DIR_ATUAL.parents[1] / "datasets",
        # Opção 2: Dentro do Container Docker / Spark
        Path("/opt/spark/dados/projeto-volume-processamento-soja"),
        Path("/opt/spark/dados"),
        # Opção 3: Na própria pasta onde está o app.py
        DIR_ATUAL,
    ]

    base_path = None
    # Procura o primeiro caminho da lista que realmente exista e contenha os CSVs
    for caminho in caminhos_possiveis:
        if (
            caminho.exists()
            and (caminho / "04-forecast.csv").exists()
            and (caminho / "processamento_soja.csv").exists()
        ):
            base_path = caminho
            break

    if not base_path:
        return (
            None,
            None,
            None,
            None,
            None,
            "Nenhum diretório válido com os arquivos CSV foi encontrado.",
        )

    try:
        df_historico = pd.read_csv(
            base_path / "processamento_soja.csv", parse_dates=["data"]
        )
        df_trend = pd.read_csv(base_path / "01-trend.csv", parse_dates=["data"])
        df_seasonal = pd.read_csv(
            base_path / "02-seasonal.csv", parse_dates=["data"]
        )
        df_resid = pd.read_csv(
            base_path / "03-residual.csv", parse_dates=["data"]
        )
        df_forecast = pd.read_csv(
            base_path / "04-forecast.csv", index_col=0, parse_dates=True
        )
        df_forecast.columns = ["volume_previsto"]

        return (
            df_historico,
            df_trend,
            df_seasonal,
            df_resid,
            df_forecast,
            "Sucesso",
        )
    except Exception as e:
        return None, None, None, None, None, str(e)


df_hist, df_trend, df_seasonal, df_resid, df_forecast, status = carregar_dados()

if status != "Sucesso":
    st.error(
        f"⚠️ Erro ao carregar os dados gerados pelo Spark. Certifique-se de ter executado o script do PySpark no container.\n\nDetalhes: {status}"
    )
    st.stop()

# 3. Sidebar / Filtro do Horizonte Preditivo
with st.sidebar:
    # Um título curto e profissional
    st.title("🌾 Sobre o Projeto")

    # Uma breve descrição do objetivo do app
    st.markdown(
        """
        Este sistema utiliza **Apache Spark** e modelos estatísticos preditivos (**ARIMA**) 
        para projetar a demanda de processamento de soja, otimizando o planejamento 
        logístico de originação e mitigando gargalos operacionais no recebimento de grãos.
        """
    )

    st.header("⚙️ Parâmetros de Simulação")
    dias_selecionados = st.sidebar.slider(
        label="📅 Selecione o Horizonte de Previsão (Dias):",
        min_value=1,
        max_value=30,  # Limite de 30 dias gerados no Spark
        value=7,  # Padrão recomendado de 7 dias
        help="O modelo foi pré-calculado no cluster Spark para até 30 dias.",
    )

    st.markdown("---")
    st.info(
        "💡 **Arquitetura Batch Pipeline:**\n\nO modelo ARIMA foi treinado e processado no **Apache Spark**. Esta aplicação lê os artefatos pré-calculados para uma renderização ultrarrápida."
    )

    # Seção do Desenvolvedor 
    st.subheader("🛠️ Desenvolvedor")
    st.markdown("**Douglas Vittori**")
    st.caption("Cientista de Dados em Formação")
        
    # Botão e link destacado para o portfólio
    st.markdown("🔗 **Acesse meus projetos:**")
    st.markdown("[🚀 Meu Portfólio de Dados](https://douglasvittori-portfolio.lovable.app/)")

# Filtra a previsão com base na escolha do usuário
df_forecast_exibicao = df_forecast.head(dias_selecionados)

# Mensagens de governança baseadas na escolha
if dias_selecionados > 14:
    st.warning(
        f"⚠️ **Atenção:** Projeções estendidas ({dias_selecionados} dias) possuem maior margem de incerteza devido à volatilidade do mercado agrícola."
    )
elif dias_selecionados == 7:
    st.success(
        "✅ **Horizonte Operacional Recomendado:** 7 dias (Ciclo ideal de planejamento semanal de recebimento e moagem)."
    )

# 4. Métricas Principais (KPIs superiores dinâmicos)
col1, col2, col3, col4 = st.columns(4)

ultimo_historico = df_hist["volume_processado_ton"].iloc[-1]
media_prevista = df_forecast_exibicao["volume_previsto"].mean()
total_previsto_periodo = df_forecast_exibicao["volume_previsto"].sum()
variacao_pct = (
    (media_prevista - ultimo_historico) / ultimo_historico
) * 100

with col1:
    st.metric(
        label="Último Volume Realizado",
        value=f"{ultimo_historico:,.2f} Ton",
    )

with col2:
    st.metric(
        label=f"Média Prevista ({dias_selecionados}d)",
        value=f"{media_prevista:,.2f} Ton",
        delta=f"{variacao_pct:+.2f}% vs último dia",
    )

with col3:
    st.metric(
        label=f"Volume Total Previsto ({dias_selecionados}d)",
        value=f"{total_previsto_periodo:,.2f} Ton",
    )

with col4:
    st.metric(
        label="Janela Selecionada",
        value=f"{dias_selecionados} Dias",
        delta="Buffer Spark: 30d",
    )

st.markdown("---")

# 5. Abas Principais de Visualização
aba1, aba2, aba3 = st.tabs(
    [
        "🚀 Projeção Preditiva (ARIMA)",
        "🔍 Decomposição de Série Temporal",
        "📋 Tabela de Dados & Exportação",
    ]
)

# --- ABA 1: PREVISÃO ---
with aba1:
    st.subheader(
        f"Projeção Operacional de Processamento para os Próximos {dias_selecionados} Dias"
    )

    # Gráfico Combinado Histórico Recente + Previsão Filtrada
    fig_pred = go.Figure()

    # Histórico dos últimos 60 dias para dar contexto
    df_rec = df_hist.tail(60)
    fig_pred.add_trace(
        go.Scatter(
            x=df_rec["data"],
            y=df_rec["volume_processado_ton"],
            mode="lines",
            name="Histórico Real",
            line=dict(color="#1f77b4", width=2),
        )
    )

    # Previsão selecionada pelo slider
    fig_pred.add_trace(
        go.Scatter(
            x=df_forecast_exibicao.index,
            y=df_forecast_exibicao["volume_previsto"],
            mode="lines+markers",
            name=f"Previsão {dias_selecionados} Dias",
            line=dict(color="#2ca02c", width=3, dash="dash"),
            marker=dict(size=8),
        )
    )

    fig_pred.update_layout(
        title="Histórico Recente vs Projeção Preditiva",
        xaxis_title="Data",
        yaxis_title="Volume Processado (Toneladas)",
        hovermode="x unified",
        template="plotly_white",
        height=480,
    )

    st.plotly_chart(fig_pred, use_container_width=True)

# --- ABA 2: DECOMPOSIÇÃO ---
with aba2:
    st.subheader("Componentes da Série Temporal (Decomposição Multiplicativa)")

    col_decomp1, col_decomp2 = st.columns(2)

    with col_decomp1:
        # Tendência
        fig_trend = px.line(
            df_trend,
            x="data",
            y="trend",
            title="1. Tendência de Longo Prazo",
            color_discrete_sequence=["#ff7f0e"],
        )
        fig_trend.update_layout(template="plotly_white", height=300)
        st.plotly_chart(fig_trend, use_container_width=True)

        # Resíduos
        fig_resid = px.line(
            df_resid,
            x="data",
            y="resid",
            title="3. Resíduos / Ruído Aleatório",
            color_discrete_sequence=["#d62728"],
        )
        fig_resid.update_layout(template="plotly_white", height=300)
        st.plotly_chart(fig_resid, use_container_width=True)

    with col_decomp2:
    # Sazonalidade (plotando os últimos 90 dias para ver o ciclo semanal com clareza)
        df_seas_rec = df_seasonal.tail(90)

        fig_seas = px.line(
            df_seas_rec,
            x="data",
            y="seasonal",
            title="2. Sazonalidade (Ciclos Semanais - Últimos 90 Dias)",
            color_discrete_sequence=["#00cc96"],
        )
        fig_seas.update_traces(
            mode="lines+markers"
        )  # Desenha a linha com pontos claros nos dias
        fig_seas.update_layout(
            template="plotly_dark",
            height=300,
            yaxis=dict(tickformat=".2f"),  # Força formatação dos eixos
        )
        st.plotly_chart(fig_seas, use_container_width=True)

# --- ABA 3: TABELA ---
with aba3:
    st.subheader(f"Tabela de Previsões ({dias_selecionados} Dias)")

    # Prepara cópia tratada para exibição
    df_tabela = df_forecast_exibicao.copy()
    df_tabela.index = df_tabela.index.strftime("%d/%m/%Y")
    df_tabela.columns = ["Volume Previsto (Toneladas)"]

    st.dataframe(df_tabela.style.format("{:,.2f}"), use_container_width=True)

    # Botão de Download mantém o DataFrame original com índice Datetime
    csv_data = df_forecast_exibicao.to_csv().encode("utf-8")
    st.download_button(
        label=f"📥 Baixar Previsão ({dias_selecionados} Dias) em CSV",
        data=csv_data,
        file_name=f"agrograin_previsao_processamento_{dias_selecionados}dias.csv",
        mime="text/csv",
    )