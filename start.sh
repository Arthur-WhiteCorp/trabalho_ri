#!/bin/bash

# Script de inicialização do projeto de indexação
# Uso: ./start.sh [comando]
# Comandos disponíveis:
#   up          - Inicia todos os serviços (Elasticsearch + Indexador + Flask)
#   index       - Roda apenas o indexador
#   flask       - Roda apenas o Flask
#   elastic     - Roda apenas o Elasticsearch
#   down        - Para todos os serviços
#   clean       - Limpa tudo (containers, volumes, redes)
#   status      - Mostra status dos serviços
#   logs        - Mostra logs de todos os serviços

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para verificar se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker não está rodando. Por favor, inicie o Docker e tente novamente."
        exit 1
    fi
}

# Função para verificar se o docker-compose está disponível
check_docker_compose() {
    if ! docker compose version &> /dev/null; then
        print_error "docker compose não está disponível. Por favor, instale o Docker Compose e tente novamente."
        exit 1
    fi
}

# Função para verificar se a pasta colecao existe
check_colecao() {
    if [ ! -d "colecao" ]; then
        print_error "Pasta 'colecao' não encontrada. Certifique-se de que os dados estão na pasta correta."
        exit 1
    fi
}

# Função para iniciar todos os serviços
start_all() {
    print_info "Iniciando todos os serviços..."
    docker compose up -d
    print_success "Serviços iniciados! Aguarde alguns segundos para o Elasticsearch inicializar."
    print_info "Para ver os logs: ./start.sh logs"
    print_info "Para ver o status: ./start.sh status"
}

# Função para rodar apenas o indexador
run_indexer() {
    print_info "Iniciando Elasticsearch..."
    docker compose up -d elasticsearch
    
    print_info "Aguardando Elasticsearch inicializar..."
    sleep 10
    
    print_info "Executando indexador..."
    docker compose up indexador
}

# Função para rodar apenas o Flask
run_flask() {
    print_info "Iniciando Elasticsearch..."
    docker compose up -d elasticsearch
    
    print_info "Aguardando Elasticsearch inicializar..."
    sleep 10
    
    print_info "Executando Flask..."
    docker compose up flask-app
}

# Função para mostrar logs
show_logs() {
    print_info "Mostrando logs de todos os serviços..."
    docker compose logs -f
}

# Função para mostrar status
show_status() {
    print_info "Status dos serviços:"
    docker compose ps
}

# Função para parar todos os serviços
stop_all() {
    print_info "Parando todos os serviços..."
    docker compose down
    print_success "Serviços parados!"
}

# Função para limpar tudo
clean_all() {
    print_warning "Isso irá remover todos os containers, volumes e redes. Tem certeza? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Limpando tudo..."
        docker compose down -v --remove-orphans
        docker system prune -f
        print_success "Limpeza concluída!"
    else
        print_info "Operação cancelada."
    fi
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: ./start.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  up          - Inicia todos os serviços (Elasticsearch + Indexador + Flask)"
    echo "  index       - Roda apenas o indexador"
    echo "  flask       - Roda apenas o Flask"
    echo "  elastic     - Roda apenas o Elasticsearch"
    echo "  down        - Para todos os serviços"
    echo "  clean       - Limpa tudo (containers, volumes, redes)"
    echo "  status      - Mostra status dos serviços"
    echo "  logs        - Mostra logs de todos os serviços"
    echo "  help        - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  ./start.sh up      # Inicia tudo"
    echo "  ./start.sh index   # Roda apenas o indexador"
    echo "  ./start.sh logs    # Vê os logs"
}

# Verificações iniciais
check_docker
check_docker_compose
check_colecao

# Processamento do comando
case "${1:-help}" in
    "up")
        start_all
        ;;
    "index")
        run_indexer
        ;;
    "flask")
        run_flask
        ;;
    "elastic")
        print_info "Iniciando apenas o Elasticsearch..."
        docker compose up -d elasticsearch
        print_success "Elasticsearch iniciado!"
        ;;
    "down")
        stop_all
        ;;
    "clean")
        clean_all
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Comando desconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 