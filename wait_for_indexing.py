#!/usr/bin/env python3
"""
Script para aguardar a indexação estar completa antes de iniciar o Flask.
"""

import time
import os

def wait_for_indexing(max_retries=60, retry_interval=5):
    """
    Aguarda a indexação estar completa verificando o arquivo de sinal.
    
    Args:
        max_retries (int): Número máximo de tentativas
        retry_interval (int): Intervalo entre tentativas em segundos
    
    Returns:
        bool: True se a indexação estiver completa, False caso contrário
    """
    signal_file = "/app/indexacao_completa.flag"
    
    print(f"⏳ Aguardando indexação estar completa...")
    print(f"🔍 Verificando arquivo: {signal_file}")
    print(f"⏰ Máximo de {max_retries * retry_interval} segundos ({max_retries} tentativas)")
    
    for attempt in range(max_retries):
        try:
            if os.path.exists(signal_file):
                with open(signal_file, 'r') as f:
                    content = f.read().strip()
                    if content == "INDEXACAO_COMPLETA":
                        print(f"✅ Indexação completa! Flask pode iniciar.")
                        return True
                    else:
                        print(f"❌ Tentativa {attempt + 1}/{max_retries}: Arquivo de sinal existe mas conteúdo inválido: {content}")
            else:
                print(f"⏳ Tentativa {attempt + 1}/{max_retries}: Arquivo de sinal não encontrado, indexação ainda em andamento...")
                
        except Exception as e:
            print(f"❌ Tentativa {attempt + 1}/{max_retries}: Erro ao verificar arquivo - {str(e)}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Aguardando {retry_interval} segundos antes da próxima verificação...")
            time.sleep(retry_interval)
    
    print("❌ Timeout: Indexação não foi concluída no tempo esperado")
    return False

if __name__ == "__main__":
    success = wait_for_indexing()
    if not success:
        exit(1) 