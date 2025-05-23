from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from collections import defaultdict
from datetime import datetime
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

rooms_users = defaultdict(set)       # Track usernames per room
chat_history = defaultdict(list)     # Track message history per room


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    room = data.get('room')
    sid = request.sid

    if not username or not room:
        return

    join_room(room)
    rooms_users[room].add(username)

    # Send chat history to new user
    for message in chat_history[room]:
        emit('message', message, room=sid)

    # Broadcast join event
    join_message = {
        "username": "System",
        "text": f"{username} has joined the room.",
        "timestamp": datetime.utcnow().isoformat()
    }
    chat_history[room].append(join_message)
    emit('message', join_message, room=room)
    emit('user_list', list(rooms_users[room]), room=room)


@socketio.on('message')
def handle_message(data):
    username = data.get('username')
    room = data.get('room')
    text = data.get('text')

    if not all([username, room, text]):
        return

    message = {
        "username": username,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }

    chat_history[room].append(message)
    emit('message', message, room=room)


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"User disconnected: {sid}")
    # Optional: Clean up user tracking here
    # You can emit a 'user_left' message if you store sid->username mapping


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8887)
