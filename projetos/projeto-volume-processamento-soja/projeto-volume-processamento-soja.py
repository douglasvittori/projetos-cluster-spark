# Análise e Previsão do Volume de Processamento de Soja usando Decomposição de Séries Temporais

import warnings
import pandas as pd
from pmdarima import auto_arima
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, adfuller, pacf

warnings.filterwarnings("ignore")

# 1. Inicializa a sessão Spark de forma robusta no container
spark = (
    SparkSession.builder.appName("Previsão do Volume de Processamento de Soja")
    .master("local[*]")
    .getOrCreate()
)

# 2. Carrega os dados de séries temporais (nome do arquivo ajustado para underline)
df = spark.read.csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/processamento_soja.csv",
    header=True,
    inferSchema=True,
)

print("\nSessão Spark Criada e Dados Carregados.")

# 3. Seleciona colunas e converte para o formato Pandas / Datetime Index
time_series_data = (
    df.select("data", col("volume_processado_ton").alias("value"))
    .orderBy("data")
    .toPandas()
)
time_series_data["data"] = pd.to_datetime(time_series_data["data"])
time_series_data.set_index("data", inplace=True)

# 4. Decomposição da série temporal (Multiplicativa, janela de 7 dias)
resultado_decomp = seasonal_decompose(
    time_series_data, model="multiplicative", period=7
)

# Salva o resultado da decomposição em disco
resultado_decomp.trend.to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/01-trend.csv"
)
resultado_decomp.seasonal.to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/02-seasonal.csv"
)
resultado_decomp.resid.to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/03-residual.csv"
)

print("\nDecomposição da Série Temporal Realizada com Sucesso.\n")

# 5. Determina os melhores hiperparâmetros (p, d, q) do modelo ARIMA
modelo_auto_arima = auto_arima(time_series_data, seasonal=False, trace=True)
best_order = modelo_auto_arima.order

print(f"\nEstes São os Melhores Valores de order: {best_order}")

# 6. Treina o modelo ARIMA com a melhor ordem encontrada
modelo_arima = ARIMA(time_series_data, order=best_order)
modelo_arima_fit = modelo_arima.fit()

# 7. Previsões para horizonte de 30 dias (para dar margem ao slider do Streamlit)
HORIZONTE_DIAS = 30
forecast = modelo_arima_fit.forecast(steps=HORIZONTE_DIAS)

# Converte forecast para Series com índice de datas futuras
forecast_series = pd.Series(
    forecast,
    name="forecast",
    index=pd.date_range(
        start=time_series_data.index[-1] + pd.Timedelta(days=1),
        periods=HORIZONTE_DIAS,
        freq="D",
    ),
)

# Cria DataFrame de previsões e salva em disco
forecast_df = forecast_series.to_frame()
forecast_df.to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/04-forecast.csv"
)

print(
    f"\nModelo ARIMA Treinado e Previsões ({HORIZONTE_DIAS} dias) Salvas em Disco."
)
print("\nPrimeiros 7 dias previstos:\n")
print(forecast_df.head(7))

# 8. Salva os resíduos do modelo (corrigido para modelo_arima_fit)
residuals = pd.DataFrame(modelo_arima_fit.resid)
residuals.to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/05-residuos.csv"
)

# 9. Teste de Dickey-Fuller Aumentado
adf_test = adfuller(residuals.dropna())
print("\nEstatísticas dos Resíduos do Modelo:\n")
print("ADF Statistic:", adf_test[0])
print("p-value:", adf_test[1])

# 10. Função de Autocorrelação (ACF) e Autocorrelação Parcial (PACF)
acf_values = acf(residuals.dropna())
pacf_values = pacf(residuals.dropna())

# Salva ACF e PACF em disco
pd.DataFrame(acf_values, columns=["ACF"]).to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/06-acf_values.csv"
)
pd.DataFrame(pacf_values, columns=["PACF"]).to_csv(
    "/opt/spark/dados/projeto-volume-processamento-soja/07-pacf_values.csv"
)

print("\nProcessamento Concluído com Sucesso.\n")

# Encerra sessão do Spark
spark.stop()