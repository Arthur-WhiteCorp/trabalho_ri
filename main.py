from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os
from indexer import Indexer   # supondo que sua classe está em indexer.py

def main():
    # 1. Leia o parquet
    folder = os.getcwd()
    df = pd.read_parquet(f"{folder}/colecao/baseDocumentos")

    # 2. Instancie o Indexer
    indexer = Indexer()

    # 3. (Opcional, mas recomendado) Crie o índice com mapping
    indexer.create_index()

    # 4. Dispare o bulk indexing
    indexer.execute_index(df)

    

    # print("Indexação finalizada com sucesso!")

if __name__ == "__main__":
    main()
