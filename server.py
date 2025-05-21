from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Track users and messages per room
rooms_users = defaultdict(set)
chat_history = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']

    join_room(room)
    rooms_users[room].add(username)

    # Send existing chat history to the new user
    for message in chat_history[room]:
        emit('message', message, room=request.sid)

    send(f"{username} has joined the room.", room=room)
    emit("user_list", list(rooms_users[room]), room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']

    leave_room(room)
    rooms_users[room].discard(username)

    send(f"{username} has left the room.", room=room)
    emit("user_list", list(rooms_users[room]), room=room)

@socketio.on('message')
def handle_message(data):
    room = data.get('room')
    message = data.get('msg')
    if room and message:
        chat_history[room].append(message)
        send(message, room=room)

@socketio.on('disconnect')
def on_disconnect():
    print("A user disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=4887)
