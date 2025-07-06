from elasticsearch import Elasticsearch, helpers
import pandas as pd
import os
from indexer import Indexer   # supondo que sua classe está em indexer.py
from wait_for_elasticsearch import wait_for_elasticsearch

def main():
    # 0. Aguardar Elasticsearch estar pronto
    print("🚀 Iniciando processo de indexação...")
    if not wait_for_elasticsearch():
        print("❌ Falha ao conectar com Elasticsearch. Abortando...")
        return
    
    # 1. Leia o parquet
    folder = os.getcwd()
    print(f"📚 Lendo arquivo parquet de {folder}/colecao/baseDocumentos...")
    df = pd.read_parquet(f"{folder}/colecao/baseDocumentos")
    print(f"✅ Carregados {len(df)} documentos")

    # 2. Instancie o Indexer
    print("🔧 Inicializando indexador...")
    indexer = Indexer()

    # 3. (Opcional, mas recomendado) Crie o índice com mapping
    print("📋 Criando índice no Elasticsearch...")
    indexer.create_index()

    # 4. Dispare o bulk indexing
    print("📤 Iniciando indexação dos documentos...")
    indexer.execute_index(df)

    print("✅ Indexação finalizada com sucesso!")

if __name__ == "__main__":
    main()
