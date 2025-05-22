from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Track users per room and chat history
rooms_users = defaultdict(set)
chat_history = defaultdict(list)

@app.route('/')
def index():
    return render_template('index.html')  # Make sure index.html is in a /templates folder

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    room = data.get('room')

    if not username or not room:
        return  # Ignore invalid join attempts

    join_room(room)
    rooms_users[room].add(username)

    # Send chat history to the user who joined
    for message in chat_history[room]:
        emit('message', message, room=request.sid)

    # Notify others in the room
    join_msg = f"{username} has joined the room."
    chat_history[room].append(join_msg)
    send(join_msg, room=room)

    # Update the user list in the room
    emit('user_list', list(rooms_users[room]), room=room)

@socketio.on('message')
def handle_message(data):
    room = data.get('room')
    msg = data.get('msg')

    if not room or not msg:
        return  # Ignore invalid messages

    chat_history[room].append(msg)
    send(msg, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    # Optional: remove user from room if you track user sessions
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8887)
