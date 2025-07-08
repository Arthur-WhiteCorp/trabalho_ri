# Trabalho de Recuperação de Informação - 2025/1

### Integrantes

- Arthur Matias
- Bianka Vasconcelos

## Objetivo

Este trabalho consiste no desenvolvimento de um buscador Jurídico que nomeamos `JusLocal`, que utiliza expansão local como principal contribuinte de aumento do MAP e NDCG.

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
