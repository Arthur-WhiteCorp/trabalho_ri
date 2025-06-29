from flask import Flask, render_template, request, jsonify
from indexer import Indexer
import json

app = Flask(__name__)
indexer = Indexer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/document/<doc_id>')
def document_details(doc_id):
    return render_template('document.html', doc_id=doc_id)

@app.route('/api/document/<doc_id>')
def get_document(doc_id):
    try:
        # Buscar documento específico por ID
        query = {
            "term": {
                "_id": doc_id
            }
        }
        
        results = indexer.search_documents(query=query, size=1)
        
        if not results or len(results['hits']['hits']) == 0:
            return jsonify({'error': 'Documento não encontrado'}), 404
        
        document = results['hits']['hits'][0]['_source']
        document['id'] = doc_id
        document['score'] = results['hits']['hits'][0]['_score']
        
        return jsonify(document)
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        search_field = data.get('field', 'all')
        size = data.get('size', 10)
        page = data.get('page', 1)  # Página atual (começa em 1)
        use_local_expansion = data.get('use_local_expansion', True)  # Novo parâmetro
        
        # Calcular offset para paginação
        from_ = (page - 1) * size
        
        if not query_text.strip():
            return jsonify({'error': 'Query não pode estar vazia'}), 400
        
        # Usar expansão local se habilitada
        if use_local_expansion:
            results = indexer.search_with_local_expansion(
                query_text=query_text,
                field=search_field,
                size=size,
                from_=from_,
                use_expansion=True
            )
        else:
            # Busca tradicional sem expansão
            if search_field == 'all':
                query = {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": ["body", "highlight"],
                                    "type": "best_fields"
                                }
                            }
                        ],
                        # "should": [
                        #     {
                        #         "script_score": {
                        #             "query": {"match_all": {}},
                        #             # "script": {
                        #             #     "source": """
                        #             #     def degree = doc['degree'].value;
                        #             #     def date = doc['date'].value;
                                        
                        #             #     // Score baseado no grau do tribunal
                        #             #     def degreeScore = 0.0;
                        #             #     if (degree == 'DEGREE_TERCEIRO') degreeScore = 3.0;
                        #             #     else if (degree == 'DEGREE_SEGUNDO') degreeScore = 2.0;
                        #             #     else if (degree == 'DEGREE_PRIMEIRO') degreeScore = 1.0;
                        #             #     else degreeScore = 0.5;
                                        
                        #             #     // Score baseado na data (documentos mais recentes têm maior peso)
                        #             #     def dateScore = 0.0;
                        #             #     if (date != null) {
                        #             #         def currentTime = System.currentTimeMillis();
                        #             #         def docTime = date.toInstant().toEpochMilli();
                        #             #         def diffDays = (currentTime - docTime) / (1000 * 60 * 60 * 24);
                                            
                        #             #         // Score decresce com o tempo: 1.0 para documentos de hoje, 0.1 para documentos muito antigos
                        #             #         if (diffDays <= 30) dateScore = 1.0;  // Último mês
                        #             #         else if (diffDays <= 365) dateScore = 0.8;  // Último ano
                        #             #         else if (diffDays <= 1825) dateScore = 0.6;  // Últimos 5 anos
                        #             #         else if (diffDays <= 3650) dateScore = 0.4;  // Últimos 10 anos
                        #             #         else dateScore = 0.1;  // Mais antigo
                        #             #     }
                                        
                        #             #     // Combinar scores (70% grau do tribunal, 30% data)
                        #             #     return (degreeScore * 0.7) + (dateScore * 0.3);
                        #             #     """,
                        #             #     "lang": "painless"
                        #             # }
                        #         }
                        #     }
                        # ]
                    }
                }
            else:
                query = {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    search_field: query_text
                                }
                            }
                        ],
                        # "should": [
                        #     {
                        #         "script_score": {
                        #             "query": {"match_all": {}},
                        #             # "script": {
                        #             #     "source": """
                        #             #     def degree = doc['degree'].value;
                        #             #     def date = doc['date'].value;
                                        
                        #             #     // Score baseado no grau do tribunal
                        #             #     def degreeScore = 0.0;
                        #             #     if (degree == 'TERCEIRA_INSTANCIA') degreeScore = 3.0;
                        #             #     else if (degree == 'SEGUNDA_INSTANCIA') degreeScore = 2.0;
                        #             #     else if (degree == 'PRIMEIRA_INSTANCIA') degreeScore = 1.0;
                        #             #     else degreeScore = 0.5;
                                        
                        #             #     // Score baseado na data (documentos mais recentes têm maior peso)
                        #             #     def dateScore = 0.0;
                        #             #     if (date != null) {
                        #             #         def currentTime = System.currentTimeMillis();
                        #             #         def docTime = date.toInstant().toEpochMilli();
                        #             #         def diffDays = (currentTime - docTime) / (1000 * 60 * 60 * 24);
                                            
                        #             #         // Score decresce com o tempo: 1.0 para documentos de hoje, 0.1 para documentos muito antigos
                        #             #         if (diffDays <= 30) dateScore = 1.0;  // Último mês
                        #             #         else if (diffDays <= 365) dateScore = 0.8;  // Último ano
                        #             #         else if (diffDays <= 1825) dateScore = 0.6;  // Últimos 5 anos
                        #             #         else if (diffDays <= 3650) dateScore = 0.4;  // Últimos 10 anos
                        #             #         else dateScore = 0.1;  // Mais antigo
                        #             #     }
                                        
                        #             #     // Combinar scores (70% grau do tribunal, 30% data)
                        #             #     return (degreeScore * 0.7) + (dateScore * 0.3);
                        #             #     """,
                        #             #     "lang": "painless"
                        #             # }
                        #         }
                        #     }
                        # ]
                    }
                }
            
            results = indexer.search_documents(query=query, size=size, from_=from_)
        
        if not results:
            return jsonify({'error': 'Erro ao executar busca'}), 500
        
        # Formatar resultados
        formatted_results = []
        for hit in results['hits']['hits']:
            formatted_results.append({
                'id': hit['_id'],
                'score': hit['_score'],
                'title': hit['_source'].get('title', 'Sem título'),
                'body': hit['_source'].get('body', '')[:200] + '...' if hit['_source'].get('body') else '',
                'highlight': hit['_source'].get('highlight', ''),
                'court': hit['_source'].get('court', ''),
                'degree': hit['_source'].get('degree', ''),
                'date': hit['_source'].get('date', ''),
                'is_mandatory_precedent': hit['_source'].get('is_mandatory_precedent', False)
            })
        
        # Calcular informações de paginação
        total = results['hits']['total']['value']
        total_pages = (total + size - 1) // size  # Arredondar para cima
        
        response_data = {
            'total': total,
            'results': formatted_results,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'size': size,
                'from': from_,
                'to': min(from_ + size, total)
            }
        }
        
        # Adicionar informações sobre expansão local se aplicada
        if use_local_expansion and 'expansion_info' in results:
            response_data['expansion_info'] = results['expansion_info']
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"Erro detalhado na busca: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/stats')
def stats():
    try:
        stats = indexer.get_index_stats()
        if stats:
            return jsonify(stats)
        else:
            return jsonify({'error': 'Não foi possível obter estatísticas'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao obter estatísticas: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 