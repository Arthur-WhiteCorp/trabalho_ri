#!/bin/bash

# Script de inicialização do projeto de indexação
# Uso: ./start.sh [comando]
# Comandos disponíveis:
#   up          - Inicia todos os serviços com dependências automáticas (Elasticsearch → Indexador → Flask)
#   up-seq      - Inicia processo sequencial manual (com pausas)
#   index       - Roda apenas o indexador
#   flask       - Roda apenas o Flask
#   elastic     - Roda apenas o Elasticsearch
#   down        - Para todos os serviços
#   restart     - Reinicia todo o processo
#   clean       - Limpa tudo (containers, volumes, redes)
#   status      - Mostra status dos serviços
#   logs        - Mostra logs de todos os serviços
#   reset       - Remove arquivo de sinal para reindexar

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

# Função para iniciar todos os serviços com dependências automáticas
start_all() {
    print_info "Iniciando todos os serviços com dependências automáticas..."
    print_info "📋 Sequência: Elasticsearch → Indexador → Flask"
    docker compose up -d
    print_success "Serviços iniciados!"
    print_info "⏳ Aguarde alguns minutos para a indexação terminar e o Flask iniciar"
    print_info "🌐 O Flask estará disponível em http://localhost:5000 após a indexação"
    print_info "📊 Para ver os logs: ./start.sh logs"
    print_info "📈 Para ver o status: ./start.sh status"
}

# Função para iniciar processo sequencial manual
start_sequential() {
    print_info "Iniciando processo sequencial manual..."
    print_info "1️⃣ Iniciando Elasticsearch..."
    docker compose up -d elasticsearch
    
    print_info "⏳ Aguardando Elasticsearch inicializar (30 segundos)..."
    sleep 30
    
    print_info "2️⃣ Executando indexação..."
    docker compose up indexador
    
    print_info "3️⃣ Iniciando Flask..."
    docker compose up -d flask-app
    
    print_success "Processo sequencial completo!"
    print_info "🌐 Flask disponível em http://localhost:5000"
}

# Função para rodar apenas o indexador
run_indexer() {
    print_info "Iniciando apenas o indexador..."
    print_warning "Certifique-se de que o Elasticsearch esteja rodando"
    docker compose up indexador
}

# Função para rodar apenas o Flask
run_flask() {
    print_info "Iniciando apenas o Flask..."
    print_warning "Certifique-se de que a indexação já foi concluída"
    docker compose up flask-app
}

# Função para rodar apenas o Elasticsearch
run_elasticsearch() {
    print_info "Iniciando apenas o Elasticsearch..."
    docker compose up -d elasticsearch
    print_success "Elasticsearch iniciado!"
    print_info "⏳ Aguarde alguns segundos para estar completamente pronto"
}

# Função para reiniciar todo o processo
restart_all() {
    print_info "Reiniciando todo o processo..."
    docker compose down
    sleep 5
    start_all
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
    
    echo ""
    print_info "Verificando arquivo de sinal de indexação..."
    if docker run --rm -v trabalho_ri_shared_signals:/shared alpine test -f /shared/indexacao_completa.flag 2>/dev/null; then
        print_success "Indexação completa!"
    else
        print_warning "Indexação ainda em andamento ou não iniciada"
    fi
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

# Função para resetar o arquivo de sinal
reset_signal() {
    print_info "Removendo arquivo de sinal para permitir reindexação..."
    docker run --rm -v trabalho_ri_shared_signals:/shared alpine rm -f /shared/indexacao_completa.flag 2>/dev/null || print_warning "Arquivo não encontrado"
    print_success "Sinal removido. Próxima execução fará reindexação completa."
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: ./start.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  up          - Inicia todos os serviços com dependências automáticas (Recomendado)"
    echo "  up-seq      - Inicia processo sequencial manual (com pausas)"
    echo "  index       - Roda apenas o indexador"
    echo "  flask       - Roda apenas o Flask"
    echo "  elastic     - Roda apenas o Elasticsearch"
    echo "  down        - Para todos os serviços"
    echo "  restart     - Reinicia todo o processo"
    echo "  clean       - Limpa tudo (containers, volumes, redes)"
    echo "  status      - Mostra status dos serviços"
    echo "  logs        - Mostra logs de todos os serviços"
    echo "  reset       - Remove arquivo de sinal para reindexar"
    echo "  help        - Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  ./start.sh up        # Inicia tudo (RECOMENDADO)"
    echo "  ./start.sh up-seq    # Inicia manualmente passo a passo"
    echo "  ./start.sh logs      # Vê os logs"
    echo "  ./start.sh status    # Verifica status"
    echo ""
    echo "📋 Sequência automática: Elasticsearch → Indexador → Flask"
    echo "🌐 Flask estará disponível em http://localhost:5000"
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
    "up-seq")
        start_sequential
        ;;
    "index")
        run_indexer
        ;;
    "flask")
        run_flask
        ;;
    "elastic")
        run_elasticsearch
        ;;
    "down")
        stop_all
        ;;
    "restart")
        restart_all
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
    "reset")
        reset_signal
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