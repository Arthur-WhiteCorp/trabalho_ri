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

# Roda o cálculo do MAP (dentro do Docker, conecta com Flask via rede)
map:
	docker run --rm -it -v $(PWD)/colecao:/app/colecao -v $(PWD)/analysers:/app/analysers --network container:flask-app indexador-parquet python analysers/calculate_map_json.py

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