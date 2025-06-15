from elasticsearch import Elasticsearch, helpers
import os
from elasticsearch.helpers import BulkIndexError
import pandas as pd
from helpers.validateField import validateField

class Indexer:
    def __init__(self):
        self.index = {}
        self.index_name = "documents"
        self.es = self.initialize_elasticsearch()

    def initialize_elasticsearch(self):
        try:
            print("Tentando conectar ao Elasticsearch...")
            es = Elasticsearch(
                "http://localhost:9200",
                verify_certs=False,
                ssl_show_warn=False
            )
            print("Cliente Elasticsearch inicializado")
            return es
        except Exception as e:
            print(f"Erro ao inicializar Elasticsearch: {str(e)}")
            raise
    
    def test_connection(self):
        try:
            print("Testando conexão com Elasticsearch...")
            if self.es.ping():
                info = self.es.info()
                print("Conexão com Elasticsearch estabelecida com sucesso!")
                print(f"Versão do Elasticsearch: {info['version']['number']}")
                return True
            else:
                print("Não foi possível conectar ao Elasticsearch")
                return False
        except Exception as e:
            print(f"Erro ao conectar com Elasticsearch: {str(e)}")
            return False
    
    def create_index(self):
        if not self.test_connection():
            raise ConnectionError("Não foi possível conectar ao Elasticsearch")
            
        mapping = {
        "mappings": {
            "properties": {
                "court":                    {"type": "keyword"},
                "degree":                   {"type": "keyword"},
                "is_mandatory_precedent":   {"type": "boolean"},
                "title":                    {"type": "text"},
                "body":                     {"type": "text"},
                "highlight":                {"type": "text"},
                "date":                     {"type": "date"}
                }
            }
        }
        # tenta criar, se ja existir, apaga e cria novamente
        try:
            if self.es.indices.exists(index=self.index_name):
                self.delete_index()
                
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Índice '{self.index_name}' criado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao criar índice: {str(e)}")
            raise

    
    def delete_index(self):
        try:
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                print("Index deleted successfully.")
            else:
                print("Index does not exist.")
        except Exception as e:
            print(f"Error deleting index '{self.index_name}': {e}")
            
    def index_documents(self, df):
        for idx, row in df.iterrows():
            try:
                metadata = row.get('metadata', {})
                document = row.get('document', {})
                if (not metadata or not document):
                    print(f"Documento {idx} não possui metadata ou document")
                    continue
                source = {
                    # do metadata
                    "court":                  validateField(metadata, "court"),
                    "degree":                 validateField(metadata, "degree"),
                    "is_mandatory_precedent": validateField(metadata, "is_mandatory_precedent"),
                    # do document
                    "title":     validateField(document, "title"),
                    "body":      validateField(document, "body"),
                    "highlight": validateField(document, "highlight"),
                    "date":      validateField(document, "date"),
                }
                
                yield {
                    "_index":  self.index_name,
                    "_id":     idx,    
                    "_source": source
                }
            except Exception as e:
                print(f"Erro ao processar documento {idx}: {str(e)}")
                continue

    def execute_index(self, df):
        try:
            helpers.bulk(self.es, self.index_documents(df))
        except BulkIndexError as e:
            print("Erros na indexação:", e.errors)
            return

