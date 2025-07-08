# Projeto de Indexação com Docker

Este projeto agora está configurado para rodar completamente dentro do Docker, incluindo o Elasticsearch. Isso garante que funcione em qualquer máquina, independentemente de ter o Elasticsearch instalado localmente.

## 🚀 Início Rápido

### Pré-requisitos

- Docker instalado e rodando
- Docker Compose instalado
- Dados na pasta `colecao/`

### Comandos Principais

```bash
# Iniciar tudo (Elasticsearch + Indexador + Flask)
./start.sh up

# Rodar apenas o indexador
./start.sh index

# Rodar apenas o Flask
./start.sh flask

# Ver logs
./start.sh logs

# Parar tudo
./start.sh down

# Ver status dos serviços
./start.sh status
```

## 📋 Estrutura do Projeto

```
trabalho_ri/
├── docker-compose.yml          # Configuração dos serviços
├── Dockerfile                  # Imagem do indexador/Flask
├── start.sh                    # Script de inicialização
├── wait_for_elasticsearch.py   # Script para aguardar ES
├── main.py                     # Script principal do indexador
├── app.py                      # Aplicação Flask
├── indexer.py                  # Classe do indexador
├── colecao/                    # Dados para indexação
├── analysers/                  # Scripts de análise
└── requirements.txt            # Dependências Python
```

## 🔧 Serviços Docker

### 1. Elasticsearch

- **Imagem**: `docker.elastic.co/elasticsearch/elasticsearch:8.11.0`
- **Porta**: 9200 (HTTP), 9300 (Transport)
- **Configuração**: Single-node, sem segurança habilitada
- **Volume**: Dados persistentes em `elasticsearch_data`

### 2. Indexador

- **Imagem**: Build local baseada em Python 3.10
- **Função**: Indexa documentos do parquet no Elasticsearch
- **Dependência**: Elasticsearch

### 3. Flask App

- **Imagem**: Build local baseada em Python 3.10
- **Porta**: 5000
- **Função**: Interface web para busca
- **Dependência**: Elasticsearch

## 🛠️ Comandos Detalhados

### Usando o script `start.sh`

```bash
# Ver todos os comandos disponíveis
./start.sh help

# Iniciar todos os serviços em background
./start.sh up

# Rodar indexador (inicia ES automaticamente)
./start.sh index

# Rodar Flask (inicia ES automaticamente)
./start.sh flask

# Ver logs em tempo real
./start.sh logs

# Ver status dos containers
./start.sh status

# Parar todos os serviços
./start.sh down

# Limpar tudo (containers, volumes, redes)
./start.sh clean
```

### Usando Docker Compose diretamente

```bash
# Iniciar todos os serviços
docker compose up -d

# Rodar apenas o Elasticsearch
docker compose up -d elasticsearch

# Rodar apenas o indexador
docker compose up indexador

# Rodar apenas o Flask
docker compose up flask-app

# Ver logs
docker compose logs -f

# Parar tudo
docker compose down

# Limpar volumes
docker compose down -v
```

### Usando o Makefile

```bash
# Comandos antigos (ainda funcionam)
make build
make run
make app

# Novos comandos com Docker Compose
make up
make index
make flask
make down
make clean
```

## 🔍 Monitoramento

### Verificar se o Elasticsearch está funcionando

```bash
# Via curl
curl http://localhost:9200

# Via navegador
http://localhost:9200
```

### Verificar logs específicos

```bash
# Logs do Elasticsearch
docker compose logs elasticsearch

# Logs do indexador
docker compose logs indexador

# Logs do Flask
docker compose logs flask-app
```

## 🐛 Solução de Problemas

### Elasticsearch não inicia

```bash
# Verificar se há containers conflitantes
docker ps -a | grep elasticsearch

# Limpar e tentar novamente
./start.sh clean
./start.sh up
```

### Indexador falha ao conectar

```bash
# Verificar se o Elasticsearch está pronto
curl http://localhost:9200

# Aguardar mais tempo para inicialização
# O script wait_for_elasticsearch.py aguarda até 60 segundos
```

### Porta 9200 já está em uso

```bash
# Parar serviços locais do Elasticsearch
sudo systemctl stop elasticsearch

# Ou usar uma porta diferente no docker-compose.yml
```

## 📊 Fluxo de Trabalho Típico

1. **Preparação**:

   ```bash
   # Certifique-se de que os dados estão na pasta colecao/
   ls colecao/
   ```

2. **Indexação**:

   ```bash
   # Iniciar Elasticsearch e rodar indexador
   ./start.sh index
   ```

3. **Aplicação Web**:

   ```bash
   # Iniciar Flask (se não estiver rodando)
   ./start.sh flask
   ```

4. **Acesso**:

   - Abrir http://localhost:5000 no navegador

5. **Limpeza**:
   ```bash
   # Parar tudo quando terminar
   ./start.sh down
   ```

## 🔄 Variáveis de Ambiente

O projeto usa as seguintes variáveis de ambiente:

- `ELASTICSEARCH_URL`: URL do Elasticsearch (padrão: http://localhost:9200)
- `ES_JAVA_OPTS`: Opções JVM do Elasticsearch (padrão: -Xms512m -Xmx512m)

## 📝 Notas Importantes

1. **Primeira execução**: O Elasticsearch pode demorar alguns minutos para inicializar na primeira vez
2. **Dados persistentes**: Os dados do Elasticsearch são mantidos em volume Docker
3. **Rede**: Todos os serviços se comunicam via rede Docker interna
4. **Portas**: Certifique-se de que as portas 9200 e 5000 estão livres
5. **Memória**: O Elasticsearch usa 512MB de RAM por padrão

## 🆘 Suporte

Se encontrar problemas:

1. Verifique se o Docker está rodando
2. Verifique se o docker-compose está instalado
3. Execute `./start.sh clean` e tente novamente
4. Verifique os logs com `./start.sh logs`
5. Certifique-se de que os dados estão na pasta `colecao/`
