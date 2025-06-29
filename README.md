# Sistema de Busca de Documentos Jurídicos

Sistema de busca em documentos jurídicos usando Elasticsearch e Flask.

## Funcionalidades

- ✅ Indexação automática de documentos
- ✅ Busca full-text com BM25
- ✅ **Novo sistema de ranking**: Boost por grau do tribunal (3ª instância tem maior peso)
- ✅ Interface web moderna e responsiva
- ✅ Busca por campos específicos
- ✅ Estatísticas do índice
- ✅ Score de relevância
- ✅ IDs únicos dos documentos preservados

## Sistema de Ranking

O sistema agora utiliza um **ranking híbrido** que combina:

1. **Relevância textual**: Busca nos campos `body` e `highlight` (título removido)
2. **Boost por grau do tribunal**:
   - **3ª Instância**: Boost de 3.0 (maior peso)
   - **2ª Instância**: Boost de 2.0 (peso médio)
   - **1ª Instância**: Boost de 1.0 (peso menor)
   - **Outros**: Boost de 0.5 (peso mínimo)

### Por que essa mudança?

- **Título removido**: Evita que documentos com títulos similares tenham vantagem injusta
- **Grau do tribunal**: Documentos de instâncias superiores têm maior autoridade jurídica
- **3ª instância**: Representa a instância máxima, com maior peso no ranking

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

- **Todos os campos**: Busca em corpo e destaque + boost por grau do tribunal
- **Corpo do texto**: Busca no conteúdo principal
- **Destaque**: Busca no campo de destaque
- **Tribunal**: Busca por tribunal específico
- **Grau**: Busca por grau do processo

> **Nota**: O título foi removido da busca para evitar viés no ranking. O sistema agora prioriza documentos de instâncias superiores.

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
# Busca simples (sem boost)
query = {"match": {"body": "processo"}}

# Busca em múltiplos campos (sem título) + boost por grau
query = {
    "bool": {
        "must": [
            {
                "multi_match": {
                    "query": "processo",
                    "fields": ["body", "highlight"]
                }
            }
        ],
        "should": [
            {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": """
                        def degree = doc['degree'].value;
                        if (degree == '3ª INSTÂNCIA') return 3.0;
                        else if (degree == '2ª INSTÂNCIA') return 2.0;
                        else if (degree == '1ª INSTÂNCIA') return 1.0;
                        else return 0.5;
                        """,
                        "lang": "painless"
                    }
                }
            }
        ]
    }
}

# Busca com filtros
query = {
    "bool": {
        "must": [
            {"match": {"body": "processo"}},
            {"term": {"court": "TRF5"}}
        ],
        "should": [
            {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": """
                        def degree = doc['degree'].value;
                        if (degree == '3ª INSTÂNCIA') return 3.0;
                        else if (degree == '2ª INSTÂNCIA') return 2.0;
                        else if (degree == '1ª INSTÂNCIA') return 1.0;
                        else return 0.5;
                        """,
                        "lang": "painless"
                    }
                }
            }
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

## Testando o Sistema

### Teste do Ranking

Para verificar se o novo sistema de ranking está funcionando:

```bash
python test_ranking.py
```

Este script irá:

- Executar uma busca de teste
- Mostrar os top 5 resultados
- Analisar os scores por grau do tribunal
- Verificar se 3ª instância tem scores maiores

### Verificação Manual

1. Acesse `http://localhost:5000`
2. Digite uma busca (ex: "processo")
3. Verifique se documentos de 3ª instância aparecem primeiro
4. Compare os scores entre diferentes graus

## Avaliação de Performance

### Cálculo de MAP (Mean Average Precision)

Para avaliar a qualidade do sistema de busca usando o arquivo de consultas:

```bash
python calculate_map.py
```

Este script:

- Lê o arquivo `colecao/query_eval` com consultas e relevância
- Executa cada consulta no sistema atual
- Calcula o MAP considerando o novo sistema de ranking
- Salva resultados em `map_results.json`

### Análise Detalhada do Ranking

Para analisar como o ranking por grau do tribunal está funcionando:

```bash
python analyze_ranking.py
```

Este script:

- Analisa distribuição de resultados por grau
- Verifica se 3ª instância tem scores maiores
- Compara diferentes consultas
- Mostra top resultados com detalhes

### Execução Completa de Avaliação

Para executar todos os testes de uma vez:

```bash
python run_evaluation.py
```

Este script:

- Verifica se o servidor está rodando
- Executa todos os testes de forma sequencial
- Mostra resultados organizados
- Salva métricas finais

### Scripts de Teste

- **`test_ranking.py`**: Teste básico do sistema de ranking
- **`calculate_map.py`**: Cálculo de MAP (versão original com problema de tipos)
- **`calculate_map_json.py`**: Cálculo de MAP otimizado (usa JSON, mas com problema de tipos)
- **`calculate_map_json_fixed.py`**: Cálculo de MAP corrigido (resolve problema de tipos, limitado a 20 queries)
- **`calculate_map_full.py`**: Cálculo de MAP completo (todas as 253 consultas)
- **`analyze_ranking.py`**: Análise detalhada do ranking
- **`convert_query_eval.py`**: Conversor para JSON
- **`debug_map.py`**: Script de debug para identificar problemas
- **`run_evaluation.py`**: Execução completa de todos os testes

### Scripts Recomendados

Para avaliação completa:

```bash
# 1. Converter dados
python convert_query_eval.py

# 2. Calcular MAP completo (recomendado)
python calculate_map_full.py

# 3. Análise detalhada
python analyze_ranking.py
```

### Versões dos Scripts de MAP

| Script                        | Consultas | Problema          | Uso          |
| ----------------------------- | --------- | ----------------- | ------------ |
| `calculate_map.py`            | Todas     | ❌ Tipos de dados | Não usar     |
| `calculate_map_json.py`       | Todas     | ❌ Tipos de dados | Não usar     |
| `calculate_map_json_fixed.py` | 20        | ✅ Corrigido      | Teste rápido |
| `calculate_map_full.py`       | 253       | ✅ Corrigido      | **Produção** |

### Interpretação dos Resultados

- **MAP > 0.5**: Excelente performance
- **MAP 0.3-0.5**: Boa performance
- **MAP 0.1-0.3**: Performance moderada
- **MAP < 0.1**: Performance baixa

> **Nota**: O MAP considera tanto a relevância quanto a posição dos documentos no ranking.

## Conversão de Dados

### Converter query_eval para JSON

Para converter o arquivo de consultas para formato JSON (mais fácil de trabalhar):

```bash
python convert_query_eval.py
```

Este script cria:

- **`colecao/queries.json`**: Formato padrão JSON
- **`colecao/elasticsearch_queries.json`**: Formato para Elasticsearch Rank Evaluation API

### Estrutura do JSON

```json
{
  "metadata": {
    "total_queries": 253,
    "format": "query_evaluation"
  },
  "queries": [
    {
      "query": "texto da consulta",
      "relevant_documents": [
        {
          "doc_id": 123456,
          "relevance": 2
        }
      ],
      "total_relevant": 12,
      "total_documents": 16
    }
  ]
}
```

# Aplicação de Indexação com Docker

## Como rodar

1. **Build da imagem Docker:**

```bash
docker build -t indexador-parquet .
```

2. **Execute o container:**

```bash
docker run --rm -it -v $(pwd)/colecao:/app/colecao indexador-parquet
```

> O volume `-v $(pwd)/colecao:/app/colecao` garante que a pasta com o arquivo Parquet seja acessível dentro do container.

3. **Configuração do Elasticsearch:**

Certifique-se de que o Elasticsearch está rodando e acessível a partir do container (localhost ou IP da máquina).

---

- O script padrão executado é o `indexador.py`.
- Para rodar outros scripts, altere o comando no Dockerfile ou use `docker run ... python outro_script.py`.
