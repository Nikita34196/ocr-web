import os
import requests
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '')

HTML = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'index.html'), encoding='utf-8').read()

@app.route('/')
def index():
    return HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/test')
def test():
    return {'status': 'ok', 'key_set': bool(ANTHROPIC_KEY)}

@app.route('/api', methods=['POST'])
def proxy():
    try:
        body = request.get_json(force=True)
        if body is None:
            return {'error': {'message': 'Невалидный JSON'}}, 400

        api_key = body.pop('api_key', ANTHROPIC_KEY)
        if not api_key:
            return {'error': {'message': 'API ключ не задан'}}, 400

        # Потоковая передача — обходит буферизацию и фильтрацию
        r = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            },
            json=body,
            stream=True,
            timeout=600
        )

        def generate():
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk

        return Response(
            stream_with_context(generate()),
            status=r.status_code,
            content_type='application/json'
        )

    except Exception as e:
        return {'error': {'message': str(e)}}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
