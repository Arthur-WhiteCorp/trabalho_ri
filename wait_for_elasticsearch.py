#!/usr/bin/env python3
"""
Script para aguardar o Elasticsearch estar pronto antes de executar o indexador.
"""

import time
import os
import requests
from elasticsearch import Elasticsearch

def wait_for_elasticsearch(max_retries=30, retry_interval=2):
    """
    Aguarda o Elasticsearch estar pronto para receber conexões.
    
    Args:
        max_retries (int): Número máximo de tentativas
        retry_interval (int): Intervalo entre tentativas em segundos
    
    Returns:
        bool: True se o Elasticsearch estiver pronto, False caso contrário
    """
    es_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    
    print(f"⏳ Aguardando Elasticsearch em {es_url}...")
    
    for attempt in range(max_retries):
        try:
            # Tentar conectar com o Elasticsearch
            es = Elasticsearch(es_url, verify_certs=False, ssl_show_warn=False)
            
            if es.ping():
                info = es.info()
                print(f"✅ Elasticsearch está pronto! Versão: {info['version']['number']}")
                return True
            else:
                print(f"❌ Tentativa {attempt + 1}/{max_retries}: Elasticsearch não respondeu ao ping")
                
        except Exception as e:
            print(f"❌ Tentativa {attempt + 1}/{max_retries}: Erro ao conectar - {str(e)}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Aguardando {retry_interval} segundos antes da próxima tentativa...")
            time.sleep(retry_interval)
    
    print("❌ Timeout: Elasticsearch não ficou pronto no tempo esperado")
    return False

if __name__ == "__main__":
    success = wait_for_elasticsearch()
    if not success:
        exit(1) 