
import pandas as pd # type: ignore

# Caminho do arquivo
c_arquivo = r"C:\Users\Richard\OneDrive\Área de Trabalho\ESTUDOS\financas.xlsm"

# Ler a planilha
df = pd.read_excel(c_arquivo, sheet_name="Planilha1")

# Ler a planilha pulando as 2 primeiras linhas para buscando as colunas
df = pd.read_excel(c_arquivo, sheet_name="Planilha1", skiprows=2)

# Ajustar os nomes das colunas para evitar problemas
df.columns = df.columns.str.strip()  # Remove espaços extras

# Verificar se as colunas foram carregadas corretamente
print(df.head())

# Ajustar o nome das colunas para evitar problemas
df.columns = df.columns.str.strip()
# Remove espaços extras nos nomes das colunas

# Converter a coluna Data para formato datetime, se existir
if 'Data' in df.columns:
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)

# Exibir o dataframe processado
print(df.info())
print(df.head())
