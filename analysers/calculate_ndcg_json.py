#!/usr/bin/env python3
"""
Script para calcular NDCG completo com todas as consultas
"""

import requests
import json
import time
import math
from collections import defaultdict
import os

class NDCGCalculatorFull:
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
    
    def calculate_dcg(self, query_data, search_results, k=10):
        """Calcula DCG (Discounted Cumulative Gain) para uma query"""
        if not search_results or 'results' not in search_results:
            return 0.0
        
        # Criar dicionário de relevância para busca rápida
        relevance_dict = {}
        for doc in query_data['relevant_documents']:
            relevance_dict[str(doc['doc_id'])] = doc['relevance']
        
        dcg = 0.0
        retrieved_docs = search_results['results'][:k]
        
        for i, doc in enumerate(retrieved_docs):
            doc_id = str(doc['id'])
            relevance = relevance_dict.get(doc_id, 0)
            
            # Fórmula DCG: DCG@k = Σ(relevance_i / log2(i+1))
            if relevance > 0:
                dcg += relevance / math.log2(i + 2)  # i+2 porque log2(1) = 0
        
        return dcg
    
    def calculate_idcg(self, query_data, k=10):
        """Calcula IDCG (Ideal DCG) para uma query"""
        # Obter todos os documentos relevantes ordenados por relevância (decrescente)
        relevant_docs = []
        for doc in query_data['relevant_documents']:
            if doc['relevance'] > 0:
                relevant_docs.append(doc['relevance'])
        
        # Ordenar por relevância (decrescente)
        relevant_docs.sort(reverse=True)
        
        # Calcular IDCG com os k primeiros documentos
        idcg = 0.0
        for i, relevance in enumerate(relevant_docs[:k]):
            idcg += relevance / math.log2(i + 2)
        
        return idcg
    
    def calculate_ndcg(self, query_data, search_results, k=10):
        """Calcula NDCG (Normalized Discounted Cumulative Gain) para uma query"""
        dcg = self.calculate_dcg(query_data, search_results, k)
        idcg = self.calculate_idcg(query_data, k)
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def calculate_ndcg_at_k(self, query_data, search_results, k_values=[1, 3, 5, 10]):
        """Calcula NDCG para múltiplos valores de k"""
        results = {}
        for k in k_values:
            results[f'ndcg_at_{k}'] = self.calculate_ndcg(query_data, search_results, k)
        return results
    
    def calculate_ndcg_full(self, use_expansion=True, progress_interval=10, k_values=[1, 3, 5, 10]):
        """Calcula o NDCG geral com todas as consultas"""
        if not self.queries_data:
            print("❌ Dados de consultas não carregados")
            return {}
        
        queries = self.queries_data['queries']
        
        expansion_text = "COM expansão local" if use_expansion else "SEM expansão"
        print(f"🔍 Executando buscas para calcular NDCG ({expansion_text})...")
        print(f"📊 Processando TODAS as {len(queries)} consultas")
        print(f"⏱️  Estimativa: ~{len(queries) * 0.2:.0f} segundos")
        
        total_queries = len(queries)
        ndcg_sums = {f'ndcg_at_{k}': 0.0 for k in k_values}
        successful_queries = 0
        
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
                # Calcular NDCG para diferentes valores de k
                ndcg_results = self.calculate_ndcg_at_k(query_data, search_results, k_values)
                
                # Somar para calcular média
                for k in k_values:
                    key = f'ndcg_at_{k}'
                    ndcg_sums[key] += ndcg_results[key]
                
                successful_queries += 1
                
                # Debug: mostrar resultados para as primeiras queries
                if i <= 3:
                    print(f"   📋 Query {i} ({expansion_text}):")
                    print(f"      Query: '{query_text[:50]}...'")
                    print(f"      Resultados: {len(search_results.get('results', []))}")
                    for k in k_values:
                        print(f"      NDCG@{k}: {ndcg_results[f'ndcg_at_{k}']:.4f}")
                    if use_expansion and 'expansion_info' in search_results:
                        terms = search_results['expansion_info'].get('local_expansion_terms', [])
                        print(f"      Termos expandidos: {terms}")
                
                # Guardar resultados (apenas para queries com NDCG > 0 para economizar espaço)
                max_ndcg = max(ndcg_results.values())
                if max_ndcg > 0:
                    results_by_query.append({
                        'query': query_text,
                        'ndcg_results': ndcg_results,
                        'total_relevant': query_data['total_relevant'],
                        'total_documents': query_data['total_documents']
                    })
                
                # Mostrar NDCG apenas se > 0
                if max_ndcg > 0:
                    ndcg_str = ", ".join([f"NDCG@{k}={ndcg_results[f'ndcg_at_{k}']:.4f}" for k in k_values])
                    print(f"   ✅ Query {i}: {ndcg_str}")
                
                # Pequena pausa para não sobrecarregar o servidor
                time.sleep(0.1)
            else:
                print(f"   ❌ Falha na busca (query {i})")
        
        if successful_queries == 0:
            print("❌ Nenhuma query foi processada com sucesso")
            return {}
        
        # Calcular médias
        mean_ndcg = {}
        for k in k_values:
            key = f'ndcg_at_{k}'
            mean_ndcg[key] = ndcg_sums[key] / successful_queries
        
        total_time = time.time() - start_time
        
        expansion_suffix = "_with_local_expansion" if use_expansion else "_without_expansion"
        
        print(f"\n📈 RESULTADOS FINAIS ({expansion_text}):")
        print(f"   Queries processadas: {successful_queries}/{total_queries}")
        print(f"   Tempo total: {total_time:.1f} segundos")
        for k in k_values:
            print(f"   NDCG@{k}: {mean_ndcg[f'ndcg_at_{k}']:.4f}")
        
        # Criar diretório se não existir
        os.makedirs("analysers/results", exist_ok=True)
        
        # Salvar resultados detalhados
        detailed_results = {
            "metadata": {
                "mean_ndcg": mean_ndcg,
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "total_time_seconds": total_time,
                "use_expansion": use_expansion,
                "expansion_type": "local_only",
                "k_values": k_values,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results_by_query": results_by_query
        }
        
        filename = f"analysers/results/ndcg_full_results{expansion_suffix}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            print(f"💾 Resultados salvos em {filename}")
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível salvar resultados: {str(e)}")
        
        return mean_ndcg

def main():
    print("🚀 Iniciando cálculo de NDCG...")
    
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
    analyser = NDCGCalculatorFull(base_url=base_url)
    
    # Carregar dados das consultas
    if not analyser.load_queries_json():
        print("❌ Falha ao carregar dados das consultas")
        exit(1)
    
    # Valores de k para calcular NDCG
    k_values = [1, 3, 5, 10]
    
    print("\n" + "="*60)
    print("📊 CALCULANDO NDCG SEM EXPANSÃO")
    print("="*60)
    
    # Calcular NDCG sem expansão
    ndcg_without_expansion = analyser.calculate_ndcg_full(use_expansion=False, k_values=k_values)
    
    print("\n" + "="*60)
    print("📊 CALCULANDO NDCG COM EXPANSÃO LOCAL")
    print("="*60)
    
    # Calcular NDCG com expansão local
    ndcg_with_expansion = analyser.calculate_ndcg_full(use_expansion=True, k_values=k_values)
    
    print("\n" + "="*60)
    print("📈 COMPARAÇÃO FINAL")
    print("="*60)
    
    for k in k_values:
        key = f'ndcg_at_{k}'
        without_val = ndcg_without_expansion.get(key, 0.0)
        with_val = ndcg_with_expansion.get(key, 0.0)
        diff = with_val - without_val
        improvement = (diff / without_val * 100) if without_val > 0 else 0
        
        print(f"NDCG@{k} sem expansão:     {without_val:.4f}")
        print(f"NDCG@{k} com expansão:     {with_val:.4f}")
        print(f"Diferença:                 {diff:+.4f}")
        print(f"Melhoria relativa:         {improvement:+.2f}%" if without_val > 0 else "N/A")
        print()
    
    print("✅ Análise concluída!")

if __name__ == "__main__":
    main() 