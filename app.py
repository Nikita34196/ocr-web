import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static')

ANTHROPIC_KEY = os.environ.get('ANTHROPIC_KEY', '')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api', methods=['POST'])
def proxy():
    try:
        body = request.get_json()
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
            timeout=120
        )

        return jsonify(r.json()), r.status_code

    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
