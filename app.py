from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send
import json
import os
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

MESSAGES_FILE = 'messages.json'
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f)


messages = load_messages()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    messages.append(msg)
    save_messages(messages)
    send(msg, broadcast=True)

@app.route('/get_messages')
def get_messages():
    return jsonify(messages)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    data = request.get_json()
    image_data = data.get('image_data')

    if image_data:
        image_data = image_data.split(',')[1]  
        img_data = base64.b64decode(image_data)

        image_filename = f'{len(os.listdir(UPLOAD_FOLDER)) + 1}.png'
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)

        with open(image_path, 'wb') as img_file:
            img_file.write(img_data)

        image_url = f'/static/uploads/{image_filename}'
        
        messages.append({"image_url": image_url})
        save_messages(messages)

        return jsonify({'image_url': image_url}), 200
    return jsonify({'error': 'No image data found'}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True)
