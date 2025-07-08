# Builda a imagem Docker
build:
	docker build -t indexador-parquet .

# Roda o container Docker com o volume da pasta colecao
run:
	docker run --rm -it -v $(PWD)/colecao:/app/colecao indexador-parquet

# Builda e roda em sequência
all: build run

# Roda o app.py expondo a porta 5000
app:
	docker run --rm -it -p 5000:5000 -v $(PWD)/colecao:/app/colecao --name flask-app indexador-parquet python app.py

start: build app

# Roda o cálculo do MAP (dentro do Docker, conecta com Flask via rede)
map:
	docker run --rm -it -v $(PWD)/colecao:/app/colecao -v $(PWD)/analysers:/app/analysers --network container:flask-app indexador-parquet python analysers/calculate_map_json.py

ndcg:
	docker run --rm -it -v $(PWD)/colecao:/app/colecao -v $(PWD)/analysers:/app/analysers --network container:flask-app indexador-parquet python analysers/calculate_ndcg_json.py

# Roda tudo: Flask + MAP em sequência
map-full: build
	@echo "🚀 Iniciando aplicação Flask..."
	@docker run --rm -d -p 5000:5000 -v $(PWD)/colecao:/app/colecao --name flask-app indexador-parquet python app.py
	@sleep 10
	@echo "📊 Iniciando cálculo do MAP..."
	@docker run --rm -it -v $(PWD)/colecao:/app/colecao -v $(PWD)/analysers:/app/analysers --network container:flask-app indexador-parquet python analysers/calculate_map_json.py
	@echo "🧹 Limpando containers..."
	@docker stop flask-app || true
	@docker rm flask-app || true

# Para o container Flask se estiver rodando
stop:
	docker stop flask-app || true
	docker rm flask-app || true

# ===== COMANDOS COM DOCKER COMPOSE - SEQUÊNCIA CORRETA =====

# Inicia todo o processo: Elasticsearch → Indexador → Flask (SEQUENCIAL)
up-sequencial:
	@echo "🚀 Iniciando processo sequencial..."
	@echo "1️⃣ Iniciando Elasticsearch..."
	@docker compose up -d elasticsearch
	@echo "⏳ Aguardando Elasticsearch estar pronto..."
	@sleep 30
	@echo "2️⃣ Executando indexação..."
	@docker compose up indexador
	@echo "3️⃣ Iniciando Flask..."
	@docker compose up -d flask-app
	@echo "✅ Processo completo! Flask disponível em http://localhost:5000"

# Inicia todos os serviços (dependências automáticas do Docker Compose)
up:
	@echo "🚀 Iniciando todos os serviços com dependências automáticas..."
	@echo "📋 Sequência: Elasticsearch → Indexador → Flask"
	docker compose up -d

# Para todos os serviços
down:
	docker compose down

# Roda apenas o Elasticsearch
elasticsearch:
	docker compose up -d elasticsearch

# Roda apenas o indexador (depende do Elasticsearch estar saudável)
index:
	docker compose up indexador

# Roda apenas o Flask (depende do indexador ter terminado)
flask:
	docker compose up flask-app

# Roda tudo em modo interativo (para ver logs)
up-interactive:
	@echo "🚀 Iniciando em modo interativo para ver logs..."
	docker compose up

# Reinicia todo o processo (limpa e inicia novamente)
restart:
	@echo "🔄 Reiniciando todo o processo..."
	@make down
	@sleep 5
	@make up

# Limpa tudo (containers, volumes, redes)
clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Verifica status dos serviços
status:
	docker compose ps

# Ver logs do Elasticsearch
logs-es:
	docker compose logs elasticsearch

# Ver logs do indexador
logs-indexador:
	docker compose logs indexador

# Ver logs do Flask
logs-flask:
	docker compose logs flask-app

# Ver logs de todos os serviços
logs:
	docker compose logs

# Seguir logs em tempo real
logs-follow:
	docker compose logs -f

# Comando para debugging - mostra informações dos volumes
debug-volumes:
	@echo "📊 Informações dos volumes:"
	@docker volume ls | grep trabalho_ri || echo "Nenhum volume encontrado"
	@echo ""
	@echo "📁 Conteúdo do volume compartilhado:"
	@docker run --rm -v trabalho_ri_shared_signals:/shared alpine ls -la /shared || echo "Volume não acessível"

# Remove apenas o arquivo de sinal para reindexar
reset-signal:
	@echo "🧹 Removendo arquivo de sinal para permitir reindexação..."
	@docker run --rm -v trabalho_ri_shared_signals:/shared alpine rm -f /shared/indexacao_completa.flag || echo "Arquivo não encontrado"
	@echo "✅ Sinal removido. Próxima execução fará reindexação completa." 