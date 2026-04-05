import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '')

@app.route('/')
def index():
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'index.html')
        html = open(path, encoding='utf-8').read()
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return f'Ошибка: {e}', 500

@app.route('/test')
def test():
    files = []
    base = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, fs in os.walk(base):
        for f in fs:
            files.append(os.path.join(root, f).replace(base, ''))
    return jsonify({'status': 'ok', 'files': files, 'key_set': bool(ANTHROPIC_KEY)})

@app.route('/api', methods=['POST'])
def proxy():
    try:
        body = request.get_json(force=True)
        if body is None:
            return jsonify({'error': {'message': 'Невалидный JSON'}}), 400

        api_key = body.pop('api_key', ANTHROPIC_KEY)
        if not api_key:
            return jsonify({'error': {'message': 'API ключ не задан'}}), 400

        r = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            },
            json=body,
            timeout=600
        )

        return jsonify(r.json()), r.status_code

    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
