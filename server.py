from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Stores users and chat history for each room
rooms_users = defaultdict(set)
chat_history = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']

    join_room(room)
    rooms_users[room].add(username)

    # Send previous messages only to the joining user
    for msg in chat_history[room]:
        emit('message', msg, room=request.sid)

    join_msg = f"{username} has joined the room."
    chat_history[room].append(join_msg)
    send(join_msg, room=room)

    emit('user_list', list(rooms_users[room]), room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    msg = data['msg']

    chat_history[room].append(msg)
    send(msg, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    # Optional: You can handle user cleanup here with extra tracking
    print(f"User with session ID {request.sid} disconnected.")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8887)
