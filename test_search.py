#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de busca e detalhes do documento.
"""

import requests
import json

def test_search():
    """Testa a funcionalidade de busca."""
    print("🔍 Testando funcionalidade de busca...")
    
    # URL da aplicação
    base_url = "http://localhost:5000"
    
    try:
        # Teste 1: Busca simples
        print("\n1. Testando busca por 'justa causa'...")
        search_data = {
            "query": "justa causa",
            "field": "all",
            "size": 5
        }
        
        response = requests.post(f"{base_url}/search", json=search_data)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Busca bem-sucedida! Encontrados {results['total']} documentos")
            
            if results['results']:
                first_doc = results['results'][0]
                print(f"   Primeiro resultado: ID {first_doc['id']}, Score {first_doc['score']}")
                
                # Teste 2: Acessar detalhes do primeiro documento
                print(f"\n2. Testando acesso aos detalhes do documento {first_doc['id']}...")
                doc_response = requests.get(f"{base_url}/api/document/{first_doc['id']}")
                
                if doc_response.status_code == 200:
                    doc_data = doc_response.json()
                    print(f"✅ Detalhes carregados com sucesso!")
                    print(f"   Título: {doc_data.get('title', 'N/A')[:50]}...")
                    print(f"   Tribunal: {doc_data.get('court', 'N/A')}")
                    print(f"   Score: {doc_data.get('score', 'N/A')}")
                else:
                    print(f"❌ Erro ao carregar detalhes: {doc_response.status_code}")
            else:
                print("⚠️  Nenhum resultado encontrado para 'justa causa'")
        
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Certifique-se de que a aplicação Flask está rodando em http://localhost:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

def test_stats():
    """Testa a funcionalidade de estatísticas."""
    print("\n📊 Testando estatísticas do índice...")
    
    try:
        response = requests.get("http://localhost:5000/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Estatísticas carregadas com sucesso!")
            
            if 'indices' in stats and 'documents' in stats['indices']:
                docs_count = stats['indices']['documents']['total']['docs']['count']
                print(f"   Total de documentos: {docs_count}")
            else:
                print("⚠️  Estrutura de estatísticas inesperada")
        else:
            print(f"❌ Erro ao carregar estatísticas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar estatísticas: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da aplicação de busca...")
    print("=" * 50)
    
    test_search()
    test_stats()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("\nPara usar a interface web:")
    print("1. Acesse: http://localhost:5000")
    print("2. Digite sua busca")
    print("3. Clique no título de um resultado para ver os detalhes") 