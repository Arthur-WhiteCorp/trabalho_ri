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

# ===== NOVOS COMANDOS COM DOCKER COMPOSE =====

# Inicia todos os serviços (Elasticsearch + Indexador + Flask)
up:
	docker compose up -d

# Para todos os serviços
down:
	docker compose down

# Roda apenas o Elasticsearch
elasticsearch:
	docker compose up -d elasticsearch

# Roda apenas o indexador (depende do Elasticsearch)
index:
	docker compose up indexador

# Roda apenas o Flask (depende do Elasticsearch)
flask:
	docker compose up flask-app

# Roda tudo em modo interativo (para ver logs)
up-interactive:
	docker compose up

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

# Roda o indexador e depois o Flask (sequencial)
index-and-flask: elasticsearch
	@echo "⏳ Aguardando Elasticsearch inicializar..."
	@sleep 30
	@echo "📚 Executando indexador..."
	@docker compose up indexador
	@echo "🌐 Iniciando aplicação Flask..."
	@docker compose up -d flask-app 