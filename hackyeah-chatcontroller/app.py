from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/v1/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field'}), 400

    message = data['message']

    # Process the message here
    response = {
        'received': message,
        'status': 'success'
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
