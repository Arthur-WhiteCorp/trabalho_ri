#!/usr/bin/env python3
"""
Script para calcular MAP completo com todas as consultas
"""

import requests
import json
import time
from collections import defaultdict
import os

class MAPCalculatorFull:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.queries_data = None
        
    def load_queries_json(self, file_path="colecao/queries.json"):
        """Carrega consultas do arquivo JSON"""
        print("📖 Carregando consultas do arquivo JSON...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.queries_data = json.load(f)
            
            print(f"✅ Carregadas {self.queries_data['metadata']['total_queries']} consultas")
            return True
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {file_path}")
            print("💡 Certifique-se de que o arquivo queries.json está na pasta colecao/")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar arquivo: {str(e)}")
            return False
    
    def search_query(self, query, size=100, use_expansion=True):
        """Executa busca para uma query específica"""
        try:
            response = requests.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "field": "all",
                    "size": size,
                    "use_local_expansion": use_expansion
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if use_expansion and 'expansion_info' in data:
                    print(f"   🔍 Expansão aplicada: {data['expansion_info'].get('local_expansion_terms', [])}")
                elif use_expansion:
                    print(f"   ⚠️  Expansão solicitada mas não aplicada")
                return data
            else:
                print(f"❌ Erro na busca: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro: Não foi possível conectar ao servidor em {self.base_url}")
            return None
        except requests.exceptions.Timeout:
            print("❌ Timeout na requisição")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
            return None
    
    def calculate_average_precision(self, query_data, search_results):
        """Calcula Average Precision para uma query"""
        if not search_results or 'results' not in search_results:
            return 0.0
        
        # Obter documentos relevantes para esta query
        relevant_docs = set()
        for doc in query_data['relevant_documents']:
            if doc['relevance'] > 0:  # Considerar apenas documentos relevantes
                # Converter para string para comparação
                relevant_docs.add(str(doc['doc_id']))
        
        if not relevant_docs:
            return 0.0
        
        retrieved_docs = search_results['results']
        precision_sum = 0.0
        relevant_found = 0
        
        for i, doc in enumerate(retrieved_docs):
            # Converter ID retornado para string se necessário
            doc_id = str(doc['id'])
            if doc_id in relevant_docs:
                relevant_found += 1
                precision_at_k = relevant_found / (i + 1)
                precision_sum += precision_at_k
        
        if relevant_found == 0:
            return 0.0
        
        return precision_sum / len(relevant_docs)
    
    def calculate_precision_at_k(self, query_data, search_results, k=10):
        """Calcula precisão@k"""
        if not search_results or 'results' not in search_results:
            return 0.0
        
        # Obter documentos relevantes
        relevant_docs = set()
        for doc in query_data['relevant_documents']:
            if doc['relevance'] > 0:
                relevant_docs.add(str(doc['doc_id']))
        
        if k == 0:
            return 0.0
            
        relevant_retrieved = 0
        for i, doc in enumerate(search_results['results'][:k]):
            doc_id = str(doc['id'])
            if doc_id in relevant_docs:
                relevant_retrieved += 1
        
        return relevant_retrieved / k
    
    def calculate_map(self, use_expansion=True, progress_interval=10):
        """Calcula o MAP geral com todas as consultas"""
        if not self.queries_data:
            print("❌ Dados de consultas não carregados")
            return 0.0
        
        queries = self.queries_data['queries']
        
        expansion_text = "COM expansão local" if use_expansion else "SEM expansão"
        print(f"🔍 Executando buscas para calcular MAP ({expansion_text})...")
        print(f"📊 Processando TODAS as {len(queries)} consultas")
        print(f"⏱️  Estimativa: ~{len(queries) * 0.2:.0f} segundos")
        
        total_queries = len(queries)
        ap_sum = 0.0
        successful_queries = 0
        precision_at_10_sum = 0.0
        
        results_by_query = []
        start_time = time.time()
        
        for i, query_data in enumerate(queries, 1):
            query_text = query_data['query']
            
            # Mostrar progresso a cada N consultas
            if i % progress_interval == 0 or i == 1:
                elapsed = time.time() - start_time
                eta = (elapsed / i) * (total_queries - i) if i > 0 else 0
                print(f"📊 Progresso: {i}/{total_queries} ({i/total_queries*100:.1f}%) - ETA: {eta:.0f}s")
            
            # Executar busca
            search_results = self.search_query(query_text, use_expansion=use_expansion)
            
            if search_results:
                # Calcular Average Precision
                ap = self.calculate_average_precision(query_data, search_results)
                precision_at_10 = self.calculate_precision_at_k(query_data, search_results, k=10)
                
                ap_sum += ap
                precision_at_10_sum += precision_at_10
                successful_queries += 1
                
                # Debug: mostrar resultados para as primeiras queries
                if i <= 3:
                    print(f"   📋 Query {i} ({expansion_text}):")
                    print(f"      Query: '{query_text[:50]}...'")
                    print(f"      Resultados: {len(search_results.get('results', []))}")
                    print(f"      AP: {ap:.4f}, P@10: {precision_at_10:.4f}")
                    if use_expansion and 'expansion_info' in search_results:
                        terms = search_results['expansion_info'].get('local_expansion_terms', [])
                        print(f"      Termos expandidos: {terms}")
                
                # Guardar resultados (apenas para queries com AP > 0 para economizar espaço)
                if ap > 0:
                    results_by_query.append({
                        'query': query_text,
                        'ap': ap,
                        'precision_at_10': precision_at_10,
                        'total_relevant': query_data['total_relevant'],
                        'total_documents': query_data['total_documents']
                    })
                
                # Mostrar AP apenas se > 0
                if ap > 0:
                    print(f"   ✅ Query {i}: AP={ap:.4f}, P@10={precision_at_10:.4f}")
                
                # Pequena pausa para não sobrecarregar o servidor
                time.sleep(0.1)
            else:
                print(f"   ❌ Falha na busca (query {i})")
        
        if successful_queries == 0:
            print("❌ Nenhuma query foi processada com sucesso")
            return 0.0
        
        map_score = ap_sum / successful_queries
        mean_precision_at_10 = precision_at_10_sum / successful_queries
        total_time = time.time() - start_time
        
        expansion_suffix = "_with_local_expansion" if use_expansion else "_without_expansion"
        
        print(f"\n📈 RESULTADOS FINAIS ({expansion_text}):")
        print(f"   Queries processadas: {successful_queries}/{total_queries}")
        print(f"   Tempo total: {total_time:.1f} segundos")
        print(f"   MAP: {map_score:.4f}")
        print(f"   Mean Precision@10: {mean_precision_at_10:.4f}")
        
        # Criar diretório se não existir
        os.makedirs("analysers/results", exist_ok=True)
        
        # Salvar resultados detalhados
        detailed_results = {
            "metadata": {
                "map_score": map_score,
                "mean_precision_at_10": mean_precision_at_10,
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "total_time_seconds": total_time,
                "use_expansion": use_expansion,
                "expansion_type": "local_only",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results_by_query": results_by_query
        }
        
        filename = f"analysers/results/map_full_results{expansion_suffix}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            print(f"💾 Resultados salvos em {filename}")
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível salvar resultados: {str(e)}")
        
        return map_score

def main():
    print("🚀 Iniciando cálculo de MAP...")
    
    # Verificar se estamos em ambiente Docker
    if os.path.exists('/.dockerenv'):
        print("🐳 Executando em ambiente Docker")
        # Para Docker na mesma rede, usar localhost
        base_url = "http://localhost:5000"
    else:
        print("💻 Executando em ambiente local")
        base_url = "http://localhost:5000"
    
    print(f"🔗 Conectando com aplicação em: {base_url}")
    
    # Criar instância do analisador
    analyser = MAPCalculatorFull(base_url=base_url)
    
    # Carregar dados das consultas
    if not analyser.load_queries_json():
        print("❌ Falha ao carregar dados das consultas")
        exit(1)
    
    print("\n" + "="*60)
    print("📊 CALCULANDO MAP SEM EXPANSÃO")
    print("="*60)
    
    # Calcular MAP sem expansão
    map_without_expansion = analyser.calculate_map(use_expansion=False)
    
    print("\n" + "="*60)
    print("📊 CALCULANDO MAP COM EXPANSÃO LOCAL")
    print("="*60)
    
    # Calcular MAP com expansão local
    map_with_expansion = analyser.calculate_map(use_expansion=True)
    
    print("\n" + "="*60)
    print("📈 COMPARAÇÃO FINAL")
    print("="*60)
    print(f"MAP sem expansão:     {map_without_expansion:.4f}")
    print(f"MAP com expansão:     {map_with_expansion:.4f}")
    print(f"Diferença:            {map_with_expansion - map_without_expansion:+.4f}")
    print(f"Melhoria relativa:    {((map_with_expansion - map_without_expansion) / map_without_expansion * 100):+.2f}%" if map_without_expansion > 0 else "N/A")
    
    print("\n✅ Análise concluída!")

if __name__ == "__main__":
    main() 