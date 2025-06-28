import pandas as pd
import os

# Obter o diretório atual do script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construir o caminho para o arquivo parquet
parquet_path = os.path.join(script_dir, "..", "colecao", "baseDocumentos")

print(f"Tentando ler arquivo: {parquet_path}")
print(f"Arquivo existe: {os.path.exists(parquet_path)}")

# Lê o arquivo parquet
df = pd.read_parquet(parquet_path)

# # Exibe as primeiras linhas do DataFrame
# print("\nPrimeiras linhas do arquivo:")
# print(df.head())

# # Exibe informações sobre o DataFrame
# print("\nInformações sobre o DataFrame:")
# print(df.info())

# print("\nEstatísticas descritivas:")
# print(df.describe()) 
count = 0
for index, row in df.iterrows():
    metadata = row['metadata']
    features = row['features']
    # print(metadata['degree'])
    print(features)
    break
    # contar quantidade de documentos no parquet 

print(count)

    # if (not court):
    #         print('esse documento nao tem court', index)
    #         break
    # metaData = row['metadata'].keys()
    # print("metadata\n",metaData)
    # keys = row['document'].keys()
    # print("document\n",keys)
    # print(row['document']['body'])
     