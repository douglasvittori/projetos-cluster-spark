# Análise e Modelagem de Séries Temporais de Consumo de Dados em Larga Escala com PySpark
# Script de Treino do Modelo

# Imports
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, month, to_date, year

# Inicializar a Spark Session
spark = SparkSession.builder.appName("Treino").getOrCreate()

# Carregar os dados
data_path = (
    "/opt/spark/dados/projeto_trafego_internet/dados_trafego_internet_2010_2025.csv"
)
df = spark.read.csv(data_path, header=True, inferSchema=True)

# Tratar a data no formato 'YYYY-MM' para evitar valores nulos (NULL)
df = df.withColumn("Date", to_date(col("Date"), "yyyy-MM"))

# Extrair ano e mês da coluna 'Date'
df = df.withColumn("Year", year(col("Date"))).withColumn("Month", month(col("Date")))

# Assembler para transformar as colunas em vetor de features dentro do pipeline
feature_assembler = VectorAssembler(
    inputCols=["Year", "Month"], outputCol="Features"
)

# Modelo de regressão linear
modelo_lr = LinearRegression(featuresCol="Features", labelCol="Data_Traffic_TB")

# Configurar o pipeline com assembler e modelo
pipeline = Pipeline(stages=[feature_assembler, modelo_lr])

# Separar dados para treino e teste
dados_treino, dados_teste = df.randomSplit([0.7, 0.3], seed=42)

# Treinar o modelo
modelo = pipeline.fit(dados_treino)

# Fazer previsões
previsoes = modelo.transform(dados_teste)

# CORREÇÃO 2: Removida a vírgula incorreta antes de Data_Traffic_TB
previsoes.select("Date", "Data_Traffic_TB", "prediction").show()

# Avaliar o modelo
evaluator = RegressionEvaluator(
    labelCol="Data_Traffic_TB", predictionCol="prediction", metricName="rmse"
)
rmse = evaluator.evaluate(previsoes)
print("\nRoot Mean Squared Error (RMSE) nos Dados de Teste = %g" % rmse)
print("\n")

evaluator = RegressionEvaluator(
    labelCol="Data_Traffic_TB", predictionCol="prediction", metricName="r2"
)
r2 = evaluator.evaluate(previsoes)
print("\nCoeficiente de Determinação (R2) nos Dados de Teste = %g" % r2)
print("\n")

# Salvar o modelo treinado
model_path = "/opt/spark/dados/projeto_trafego_internet/modelo"
modelo.write().overwrite().save(model_path)

# Salvar as previsões em um arquivo CSV
previsoes.select("Date", "Data_Traffic_TB", "prediction").write.csv(
    "/opt/spark/dados/projeto_trafego_internet/previsoesteste",
    header=True,
    mode="overwrite",
)

# Fechar a Spark session
spark.stop()