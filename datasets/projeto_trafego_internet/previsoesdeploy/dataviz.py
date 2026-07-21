# Análise e Modelagem de Séries Temporais de Consumo de Dados em Larga Escala com PySpark
# Script de Visualização de Dados

# Imports
import os
import pandas as pd
import matplotlib.pyplot as plt

# Define o diretório onde os arquivos CSV estão localizados (altere esta pasta com o caminho no seu computador)
diretorio = "/opt/spark/dados/projeto_trafego_internet/previsoesdeploy"

# Encontra o primeiro arquivo CSV no diretório
arquivo_csv = next((f for f in os.listdir(diretorio) if f.endswith('.csv')), None)
if arquivo_csv is None:
    raise FileNotFoundError("Nenhum arquivo CSV encontrado no diretório especificado.")

# Carrega os dados do CSV para um DataFrame
caminho_completo = os.path.join(diretorio, arquivo_csv)
dados = pd.read_csv(caminho_completo)

# Converte a coluna 'Date' para datetime para melhor manipulação
dados['Date'] = pd.to_datetime(dados['Date'])

# Cria um gráfico de linhas mais completo
plt.figure(figsize=(10, 5))
plt.plot(dados['Date'], dados['prediction'], marker='o', linestyle='-', color='r', linewidth=2)

# Títulos e Labels mais descritivos
plt.title('Previsões de Consumo de Tráfego de Dados (Primeiro Semestre de 2026)', fontsize=14, fontweight='bold')
plt.xlabel('Data (Ano-Mês)', fontsize=12)
plt.ylabel('Previsão de Consumo (em Terabytes - TB)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Rotacionar as datas levemente para o caso de séries maiores
plt.xticks(rotation=15)

# Ajusta o layout para não cortar as legendas ao salvar
plt.tight_layout()

# Salva o gráfico como uma imagem PNG
plt.savefig('projeto-consumo-dados.png', dpi=300) # dpi=300 deixa a imagem em alta definição para o GitHub
