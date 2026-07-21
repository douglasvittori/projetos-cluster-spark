# Análise e Modelagem de Séries Temporais de Consumo de Dados em Larga Escala com PySpark
# Script de Deploy do Modelo

# Imports
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month
from pyspark.ml import PipelineModel
from pyspark.sql.types import StringType

# Inicializar a Spark Session
spark = SparkSession.builder \
    .appName("Deploy") \
    .getOrCreate()


# Carregar o modelo treinado (como um PipelineModel)
model_path = '/opt/spark/dados/projeto_trafego_internet/modelo' 
model = PipelineModel.load(model_path)

# Criar um DataFrame com os novos dados para previsão
# Estes são os meses para os quais queremos prever o consumo de dados em terabytes
dates = ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06']
novas_datas = spark.createDataFrame([(date,) for date in dates], ['Date'])
novas_datas = novas_datas.withColumn('Date', col('Date').cast('date'))
novas_datas = novas_datas.withColumn('Year', year(col('Date'))).withColumn('Month', month(col('Date')))

# Aplica o pipeline e faz as previsões
predictions = model.transform(novas_datas)

# Mostra as previsões
predictions.select('Date', 'prediction').show()

# Salva as previsões em um único arquivo CSV
predictions.select('Date', 'prediction').coalesce(1).write.csv('/opt/spark/dados/projeto_trafego_internet/previsoesdeploy', header=True, mode="overwrite")

# Fechar a Spark session
spark.stop()