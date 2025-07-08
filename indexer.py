from elasticsearch import Elasticsearch, helpers
import os
from elasticsearch.helpers import BulkIndexError
import pandas as pd
from helpers.validateField import validateField
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download recursos necessários do NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class Indexer:
    def __init__(self):
        self.index = {}
        self.index_name = "documents"
        self.es = self.initialize_elasticsearch()
        self.stop_words = set(stopwords.words('portuguese'))
        # Adicionar stop words específicas do domínio jurídico
        self.stop_words.update([
            'artigo', 'art', 'lei', 'decreto', 'portaria', 'resolução', 'processo',
            'autos', 'apelação', 'recurso', 'sentença', 'acórdão', 'voto', 'relator',
            'ministro', 'desembargador', 'juiz', 'tribunal', 'instância', 'grau',
            'requerente', 'requerido', 'autor', 'réu', 'parte', 'partes'
        ])

    def initialize_elasticsearch(self):
        try:
            # Usar variável de ambiente se disponível, senão usar fallback
            es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
            
            es = Elasticsearch(
                es_url,
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
                
                # Obter o ID do parquet
                doc_id = row.get('id', idx)  # Usa o ID do parquet, ou idx como fallback
                
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
                    "_id":     str(doc_id),  # Converte para string para garantir compatibilidade
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

    def search_documents(self, query=None, size=10, from_=0):
        """
        Busca documentos no índice.
        
        Args:
            query (dict): Query de busca no formato Elasticsearch
            size (int): Número máximo de documentos a retornar
            from_ (int): Offset para paginação (número de documentos a pular)
            
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
                "from": from_,
                "query": query
            }
            
            results = self.es.search(
                index=self.index_name,
                body=body
            )
            
            # Sempre retorna dict puro
            if hasattr(results, 'to_dict'):
                return results.to_dict()
            return dict(results)
            
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

    def extract_relevant_terms(self, documents, top_k=5, min_freq=2):
        """
        Extrai termos relevantes dos documentos do topo do ranking.
        
        Args:
            documents (list): Lista de documentos do topo do ranking
            top_k (int): Número de termos mais relevantes a retornar
            min_freq (int): Frequência mínima para considerar um termo relevante
            
        Returns:
            list: Lista de termos relevantes ordenados por relevância
        """
        term_frequencies = Counter()
        
        for doc in documents:
            # Extrair texto dos campos relevantes
            text_fields = []
            if doc.get('title'):
                text_fields.append(doc['title'])
            if doc.get('body'):
                text_fields.append(doc['body'])
            if doc.get('highlight'):
                text_fields.append(doc['highlight'])
            
            # Tokenizar e processar texto
            for text in text_fields:
                if text and isinstance(text, str):
                    # Tokenizar
                    tokens = word_tokenize(text.lower())
                    
                    # Filtrar tokens
                    filtered_tokens = []
                    for token in tokens:
                        # Remover pontuação e números
                        if re.match(r'^[a-zA-ZÀ-ÿ]+$', token):
                            # Remover stop words
                            if token not in self.stop_words:
                                # Filtrar palavras muito curtas ou muito longas
                                if 3 <= len(token) <= 20:
                                    filtered_tokens.append(token)
                    
                    # Contar frequência
                    term_frequencies.update(filtered_tokens)
        
        # Filtrar por frequência mínima e ordenar
        relevant_terms = [
            (term, freq) for term, freq in term_frequencies.items() 
            if freq >= min_freq
        ]
        
        # Ordenar por frequência (decrescente)
        relevant_terms.sort(key=lambda x: x[1], reverse=True)
        
        # Retornar apenas os termos (sem frequência)
        return [term for term, freq in relevant_terms[:top_k]]

    def expand_query_local(self, original_query, original_results, expansion_terms=3):
        """
        Expande a consulta usando apenas expansão local (feedback implícito).
        
        Args:
            original_query (str): Consulta original do usuário
            original_results (dict): Resultados da busca original
            expansion_terms (int): Número de termos de expansão local a adicionar
            
        Returns:
            dict: Query expandida no formato Elasticsearch
        """
        if not original_results or 'hits' not in original_results:
            return None
        
        # Obter documentos do topo (primeiros 10 resultados)
        top_documents = []
        for hit in original_results['hits']['hits'][:10]: # 10 documentos do topo do rank
            top_documents.append(hit['_source'])
        
        # Extrair termos relevantes (expansão local)
        relevant_terms = self.extract_relevant_terms(top_documents, top_k=expansion_terms)
        
        # Criar query expandida usando bool query
        expanded_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": original_query,
                            "fields": ["body", "highlight"],
                            "type": "best_fields",
                            "boost": 2.0  # Query original tem peso maior
                        }
                    }
                ],
                "should": []
            }
        }
        
        # Adicionar termos locais expandidos
        if relevant_terms:
            expanded_query["bool"]["should"].append({
                "multi_match": {
                    "query": " ".join(relevant_terms),
                    "fields": ["body", "highlight"],
                    "type": "best_fields",
                    "boost": 1.0  # Termos expandidos têm peso menor
                }
            })
        
        return expanded_query

    def search_with_local_expansion(self, query_text, field="all", size=10, from_=0, use_expansion=True):
        """
        Executa busca com expansão local opcional.
        
        Args:
            query_text (str): Texto da consulta
            field (str): Campo para busca
            size (int): Número de resultados
            from_ (int): Offset para paginação
            use_expansion (bool): Se deve usar expansão local
            
        Returns:
            dict: Resultados da busca
        """
        # Primeira busca (sem expansão)
        if field == 'all':
            initial_query = {
                "multi_match": {
                    "query": query_text,
                    "fields": ["body", "highlight"],
                    "type": "best_fields"
                }
            }
        else:
            initial_query = {
                "match": {
                    field: query_text
                }
            }
        
        initial_results = self.search_documents(query=initial_query, size=size, from_=from_)
        
        if not use_expansion or not initial_results:
            # Garantir que retorna dict
            if hasattr(initial_results, 'to_dict'):
                return initial_results.to_dict()
            return initial_results
        
        # Aplicar expansão local
        expanded_query = self.expand_query_local(query_text, initial_results)
        
        if expanded_query:
            # Executar busca expandida
            expanded_results = self.search_documents(query=expanded_query, size=size, from_=from_)
            
            # Converter para dict se necessário
            if hasattr(expanded_results, 'to_dict'):
                expanded_results = expanded_results.to_dict()
            
            # Adicionar informações sobre a expansão
            if expanded_results:
                # Obter termos locais para informação
                top_documents = []
                for hit in initial_results['hits']['hits'][:10]:
                    top_documents.append(hit['_source'])
                
                local_terms = self.extract_relevant_terms(top_documents, top_k=3)
                
                expanded_results['expansion_info'] = {
                    'original_query': query_text,
                    'expansion_applied': True,
                    'local_expansion_terms': local_terms,
                    'expansion_type': 'local_only'
                }
            
            return expanded_results
        
        # Garantir que retorna dict
        if hasattr(initial_results, 'to_dict'):
            return initial_results.to_dict()
        return initial_results

