# Trabalho de Recuperação de Informação - 2025/1

### Integrantes

- Arthur Matias
- Bianka Vasconcelos

## Objetivo

Este trabalho consiste no desenvolvimento de um buscador Jurídico que nomeamos `JusLocal`, que utiliza expansão local como principal contribuinte de aumento do MAP e NDCG.

## Dependências

- Docker: seu docker deve estar executando. Caso não esteja, execute com `sudo systemctl start docker`

- docker compose

## Como Executar

Baixe a base de documentos [nesse link](https://drive.google.com/file/d/1ekgXfYu23pBG-Wu4X1a8GsiLlN0TLIzI/view?usp=sharing).

Coloque o arquivo `baseDocumentos.parquet` na pasta `colecao`.

Rode o script:

```
start.sh up
```

E depois, rode

```
start.sh logs
```

Para acompanhar os logs da aplicação. O sistema ficará disponível em `localhost:5000`.

## Organização do Código

O projeto está estruturado da seguinte forma:

### **Arquivos Principais**

- **`app.py`**: Aplicação web Flask com rotas para busca e visualização de documentos
- **`indexer.py`**: **Classe principal** com toda a lógica de indexação, busca e expansão local
- **`main.py`**: Script para indexar os documentos parquet no Elasticsearch
- **`wait_for_elasticsearch.py`**: Utilitário para aguardar o Elasticsearch estar pronto

### **Interface do Usuário (`templates/`)**

- **`index.html`**: Página principal com interface de busca e expansão local
- **`document.html`**: Página de detalhes de um documento específico

### **Análise de Performance (`analysers/`)**

- **`calculate_map_json.py`**: Calcula MAP com e sem expansão local
- **`calculate_ndcg_json.py`**: Calcula NDCG com e sem expansão local
- **`script.py`**: Script auxiliar para análise dos dados
- **`results/`**: Resultados das análises de MAP e NDCG em formato JSON

### **Dados (`colecao/`)**

- **`baseDocumentos`**: Arquivo parquet com a base de documentos jurídicos
- **`queries.json`**: Consultas de teste para avaliação
- **`query_eval`**: Arquivo de avaliação das consultas

### **Utilitários (`helpers/`)**

- **`validateField.py`**: Função auxiliar para validação de campos

## Expansão Local

A **expansão local** é a técnica principal utilizada pelo JusLocal que usamos para melhorar o resultado da busca. Ela funciona da seguinte forma:

### Como Funciona

1. **Busca Inicial**: O sistema executa a consulta original do usuário
2. **Análise dos Top Resultados**: Analisa os primeiros 10 documentos retornados
3. **Extração de Termos Relevantes**: Identifica palavras-chave frequentes e relevantes nesses documentos
4. **Expansão da Consulta**: Adiciona esses termos à consulta original
5. **Nova Busca**: Executa uma busca expandida com melhor precisão

### Implementação no Código

A expansão local está implementada principalmente em:

- **`indexer.py`**: Núcleo da implementação

  - `extract_relevant_terms()`: Extrai termos relevantes dos documentos
  - `expand_query_local()`: Cria a consulta expandida
  - `search_with_local_expansion()`: Orquestra todo o processo

- **`app.py`**: Integração na API web

  - Rota `/search`: Permite ativar/desativar expansão local

- **`templates/index.html`**: Interface do usuário
  - Checkbox para ativar expansão local
  - Exibição dos termos expandidos

### Benefícios

- **Melhoria no MAP**: Aumenta a precisão média dos resultados
- **Melhoria no NDCG**: Melhora o ranking de documentos relevantes
- **Feedback Implícito**: Não requer interação adicional do usuário
