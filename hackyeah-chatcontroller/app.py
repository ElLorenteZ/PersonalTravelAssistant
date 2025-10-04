import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chat_service import ChatService

app = Flask(__name__)
CORS(app)
chat_service = ChatService(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/api/v1/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field'}), 400

    message = data['message']

    try:
        chat_response = chat_service.send_prompt(message)
        return jsonify({'response': chat_response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
