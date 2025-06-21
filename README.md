# Sistema de Busca de Documentos Jurídicos

Sistema de busca em documentos jurídicos usando Elasticsearch e Flask.

## Funcionalidades

- ✅ Indexação automática de documentos
- ✅ Busca full-text com BM25
- ✅ Interface web moderna e responsiva
- ✅ Busca por campos específicos
- ✅ Estatísticas do índice
- ✅ Score de relevância
- ✅ IDs únicos dos documentos preservados

## Pré-requisitos

- Python 3.8+
- Elasticsearch 8.x
- Kibana (opcional, para visualização)

## Instalação

1. **Instalar dependências:**

```bash
pip install -r requirements.txt
```

2. **Configurar Elasticsearch:**

```bash
# Iniciar Elasticsearch
sudo systemctl start elasticsearch

# Verificar se está rodando
sudo systemctl status elasticsearch
```

3. **Indexar documentos:**

```bash
python main.py
```

4. **Executar a aplicação web:**

```bash
python app.py
```

5. **Acessar a interface:**

```
http://localhost:5000
```

## IDs dos Documentos

O sistema preserva os **IDs originais** dos documentos do parquet:

- **Antes:** IDs sequenciais (1, 2, 3, ..., 4268)
- **Agora:** IDs originais do parquet (716144885, 2661736329, etc.)

### Reindexar com IDs corretos:

Se você já indexou com IDs sequenciais e quer usar os IDs originais:

```bash
python reindex_with_correct_ids.py
```

## Como usar

### Interface Web

1. **Acesse** `http://localhost:5000`
2. **Digite** sua busca no campo de texto
3. **Selecione** o campo para buscar (ou "Todos os campos")
4. **Clique** em "Buscar"
5. **Clique no título** para ver detalhes completos

### Campos de Busca

- **Todos os campos**: Busca em título, corpo e destaque
- **Título**: Busca apenas no título
- **Corpo do texto**: Busca no conteúdo principal
- **Destaque**: Busca no campo de destaque
- **Tribunal**: Busca por tribunal específico
- **Grau**: Busca por grau do processo

### Resultados

Cada resultado mostra:

- **Título** do documento (clicável)
- **Score** de relevância (BM25)
- **Preview** do conteúdo
- **Metadados**: ID, Tribunal, Grau, Data
- **Precedente Obrigatório** (se aplicável)

## Estrutura do Projeto

```
├── app.py                      # Aplicação Flask
├── main.py                     # Script de indexação
├── reindex_with_correct_ids.py # Reindexação com IDs corretos
├── indexer.py                  # Classe para indexação
├── helpers/
│   └── validateField.py        # Validação de campos
├── templates/
│   ├── index.html              # Interface de busca
│   └── document.html           # Página de detalhes
├── requirements.txt            # Dependências
└── README.md                   # Este arquivo
```

## Tecnologias

- **Backend**: Flask, Elasticsearch
- **Frontend**: HTML5, CSS3, JavaScript
- **Indexação**: Elasticsearch (BM25, TF-IDF)
- **Interface**: Design responsivo e moderno

## API Endpoints

- `GET /` - Interface principal
- `POST /search` - Executar busca
- `GET /stats` - Estatísticas do índice
- `GET /document/<id>` - Página de detalhes
- `GET /api/document/<id>` - API de detalhes

## Exemplo de Busca

```python
# Busca simples
query = {"match": {"title": "processo"}}

# Busca em múltiplos campos
query = {
    "multi_match": {
        "query": "processo",
        "fields": ["title", "body", "highlight"]
    }
}

# Busca com filtros
query = {
    "bool": {
        "must": [
            {"match": {"title": "processo"}},
            {"term": {"court": "TRF5"}}
        ]
    }
}
```

## Suporte

Para dúvidas ou problemas, verifique:

1. Se o Elasticsearch está rodando
2. Se os documentos foram indexados corretamente
3. Se todas as dependências estão instaladas
4. Se os IDs dos documentos estão corretos
