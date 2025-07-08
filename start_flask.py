#!/usr/bin/env python3
"""
Script para aguardar a indexação estar completa e então iniciar o Flask.
"""

from wait_for_indexing import wait_for_indexing
from app import app
import sys

def main():
    print("🌐 Iniciando processo de start do Flask...")
    
    # Aguardar indexação estar completa
    if not wait_for_indexing():
        print("❌ Falha ao aguardar indexação. Abortando Flask...")
        sys.exit(1)
    
    print("🚀 Iniciando aplicação Flask...")
    
    # Iniciar Flask
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 