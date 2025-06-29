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
	docker run --rm -it -p 5000:5000 -v $(PWD)/colecao:/app/colecao indexador-parquet python app.py 