import os
import requests

from dotenv import load_dotenv, find_dotenv

from flask import Flask, request, jsonify


load_dotenv(find_dotenv())

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL_SEND_MESSAGE = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'


app = Flask(__name__)


@app.route('/response', methods=['POST'])
def response_webhook():
    try:
        data = request.get_json()
        
        response = requests.post(TELEGRAM_API_URL_SEND_MESSAGE, json=data)

        if response.status_code == 200:
            return jsonify({'message': 'Response sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send response'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

@app.route('/chat', methods=['POST'])
def handle_bid_response():
    try:
        data = request.get_json()
        
        response = requests.post(TELEGRAM_API_URL_SEND_MESSAGE, json=data)

        if response.status_code == 200:
            return jsonify({'message': 'Chat message sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send chat message'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)