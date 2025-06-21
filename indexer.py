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
            # print("Tentando conectar ao Elasticsearch...")
            es = Elasticsearch(
                "http://localhost:9200",
                verify_certs=False,
                ssl_show_warn=False
            )
            # print("Cliente Elasticsearch inicializado")
            return es
        except Exception as e:
            # print(f"Erro ao inicializar Elasticsearch: {str(e)}")
            raise
    
    def test_connection(self):
        try:
            # print("Testando conexão com Elasticsearch...")
            if self.es.ping():
                info = self.es.info()
                # print("Conexão com Elasticsearch estabelecida com sucesso!")
                # print(f"Versão do Elasticsearch: {info['version']['number']}")
                return True
            else:
                # print("Não foi possível conectar ao Elasticsearch")
                return False
        except Exception as e:
            # print(f"Erro ao conectar com Elasticsearch: {str(e)}")
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
            # print(f"Índice '{self.index_name}' criado com sucesso!")
            
        except Exception as e:
            # print(f"Erro ao criar índice: {str(e)}")
            raise

    
    def delete_index(self):
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            # print("Index deleted successfully.")
                
                # print("Index does not exist.")
            # print(f"Error deleting index '{self.index_name}': {e}")
            
    def index_documents(self, df):
        total_docs = len(df)
        print(f"Iniciando indexação de {total_docs} documentos...")
        
        processed = 0
        skipped = 0
        
        for idx, row in df.iterrows():
            try:
                metadata = row.get('metadata', {})
                document = row.get('document', {})
                
                # Se document estiver vazio, pular o documento
                if not document:
                    skipped += 1
                    continue
                
                # Se metadata estiver vazio, usar valores padrão
                if not metadata:
                    metadata = {}
                
                # Verificar se os campos existem
                court_val = validateField(metadata, "court")
                degree_val = validateField(metadata, "degree")
                precedent_val = validateField(metadata, "is_mandatory_precedent")
                title_val = validateField(document, "title")
                body_val = validateField(document, "body")
                highlight_val = validateField(document, "highlight")
                date_val = validateField(document, "date")
                
                # Verificar se todos os campos do document são NOT_FOUND
                document_fields_not_found = all(val == 'NOT_FOUND' for val in [title_val, body_val, highlight_val, date_val])
                
                if document_fields_not_found:
                    skipped += 1
                    continue
                
                source = {
                    "court":                  court_val,
                    "degree":                 degree_val,
                    "is_mandatory_precedent": precedent_val,
                    "title":     title_val,
                    "body":      body_val,
                    "highlight": highlight_val,
                    "date":      date_val,
                }
                
                processed += 1
                
                yield {
                    "_index":  self.index_name,
                    "_id":     idx,    
                    "_source": source
                }
                
            except Exception as e:
                skipped += 1
                continue
        
        print(f"Processados: {processed}, Pulados: {skipped}")

    def execute_index(self, df):
        try:
            success, failed = helpers.bulk(
                self.es, 
                self.index_documents(df),
                stats_only=True,
                raise_on_error=False
            )
            
            print(f"Indexação finalizada - Sucesso: {success}, Falhas: {failed}")
                
        except BulkIndexError as e:
            print(f"Erro na indexação: {str(e)}")
            return
        except Exception as e:
            print(f"Erro geral: {str(e)}")
            return

    def search_documents(self, query=None, size=10):
        """
        Busca documentos no índice.
        
        Args:
            query (dict): Query de busca no formato Elasticsearch
            size (int): Número máximo de documentos a retornar
            
        Returns:
            dict: Resultados da busca
        """
        try:
            if query is None:
                # Busca todos os documentos
                query = {
                    "match_all": {}
                }
            
            body = {
                "size": size,
                "query": query
            }
            
            results = self.es.search(
                index=self.index_name,
                body=body
            )
            
            return results
            
        except Exception as e:
            print(f"Erro ao buscar documentos: {str(e)}")
            return None

    def get_index_stats(self):
        """
        Obtém estatísticas do índice indexado.
        """
        try:
            stats = self.es.indices.stats(index=self.index_name)
            index_stats = stats['indices'][self.index_name]
            
            print(f"\n=== ESTATÍSTICAS DO ÍNDICE ===")
            print(f"Nome do índice: {self.index_name}")
            print(f"Total de documentos: {index_stats['total']['docs']['count']}")
            print(f"Tamanho do índice: {index_stats['total']['store']['size_in_bytes']} bytes")
            print(f"Tamanho da lista invertida: {index_stats['total']['indexing']['index_size_in_bytes']} bytes")
            
            return stats
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {str(e)}")
            return None

