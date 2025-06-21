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
        
        if not query_text.strip():
            return jsonify({'error': 'Query não pode estar vazia'}), 400
        
        # Construir query baseada no campo selecionado
        if search_field == 'all':
            query = {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title", "body", "highlight"],
                    "type": "best_fields"
                }
            }
        else:
            query = {
                "match": {
                    search_field: query_text
                }
            }
        
        # Executar busca
        results = indexer.search_documents(query=query, size=size)
        
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
        
        return jsonify({
            'total': results['hits']['total']['value'],
            'results': formatted_results
        })
        
    except Exception as e:
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