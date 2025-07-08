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
