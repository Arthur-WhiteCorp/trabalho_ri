import pandas as pd
import os

folder = os.getcwd()
# Lê o arquivo parquet
df = pd.read_parquet(f"{folder}/colecao/baseDocumentos")

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
    count += 1
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
     