from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)  

DB_PATH = '/app/db/carteira.db'

def init_db():
    """Inicializa o banco de dados criando a tabela se não existir"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carteira (
            id INTEGER PRIMARY KEY,
            ticker TEXT NOT NULL,
            data_compra TEXT NOT NULL,
            valor_compra REAL NOT NULL,
            quantidade INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/carteira', methods=['GET'])
def get_carteira():
    """Obtém todas as ações da carteira"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carteira ORDER BY data_compra DESC')
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carteira', methods=['POST'])
def add_acao():
    """Adiciona uma nova ação à carteira"""
    data = request.json
    try:
        required_fields = ['ticker', 'data_compra', 'valor_compra', 'quantidade']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório faltando: {field}'}), 400
        
        ticker = data['ticker'].upper().strip()
        data_compra = datetime.strptime(data['data_compra'], '%Y-%m-%d').date()
        valor_compra = float(data['valor_compra'])
        quantidade = int(data['quantidade'])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO carteira (ticker, data_compra, valor_compra, quantidade)
            VALUES (?, ?, ?, ?)
        ''', (ticker, data_compra, valor_compra, quantidade))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'id': new_id, 'message': 'Ação adicionada com sucesso'}), 201

    except ValueError as e:
        return jsonify({'error': f'Formato de dados inválido: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carteira/<int:id>', methods=['PUT'])
def update_acao(id):
    """Atualiza uma ação existente"""
    data = request.json
    try:
        required_fields = ['ticker', 'data_compra', 'valor_compra', 'quantidade']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório faltando: {field}'}), 400

        ticker = data['ticker'].upper().strip()
        data_compra = datetime.strptime(data['data_compra'], '%Y-%m-%d').date()
        valor_compra = float(data['valor_compra'])
        quantidade = int(data['quantidade'])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE carteira
            SET ticker = ?, data_compra = ?, valor_compra = ?, quantidade = ?
            WHERE id = ?
        ''', (ticker, data_compra, valor_compra, quantidade, id))
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows == 0:
            return jsonify({'error': 'Ação não encontrada'}), 404
            
        return jsonify({'message': 'Ação atualizada com sucesso'}), 200

    except ValueError as e:
        return jsonify({'error': f'Formato de dados inválido: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/carteira/<int:id>', methods=['DELETE'])
def delete_acao(id):
    """Remove uma ação da carteira"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carteira WHERE id = ?', (id,))
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows == 0:
            return jsonify({'error': 'Ação não encontrada'}), 404
            
        return jsonify({'message': 'Ação removida com sucesso'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quote/<ticker>', methods=['GET'])
def get_quote(ticker):
    """Obtém cotação atual do ticker"""
    try:
        response = requests.get(f'https://brapi.dev/api/quote/{ticker}?token=7ENBXpDBTfhsgwDBW5Dzhq')
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results') or len(data['results']) == 0:
            return jsonify({
                'error': 'Ticker não encontrado',
                'ticker': ticker,
                'details': 'Nenhum resultado retornado pela API externa'
            }), 404

        return jsonify(data), 200

    except requests.exceptions.HTTPError as e:
        return jsonify({
            'error': 'Erro na requisição à API externa',
            'ticker': ticker,
            'details': str(e)
        }), 502
    except Exception as e:
        return jsonify({
            'error': 'Erro interno ao processar cotação',
            'ticker': ticker,
            'details': str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3003, debug=True)