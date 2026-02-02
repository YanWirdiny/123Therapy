from flask import Blueprint, render_template_string


test_bp = Blueprint('test', __name__)
TEST_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>123Therapy - Test</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 40px auto; padding: 20px; }
        #messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
        .msg { margin: 5px 0; padding: 5px; border-radius: 4px; }
        .partner_a { background: #e3f2fd; }
        .partner_b { background: #f3e5f5; }
        .ai { background: #e8f5e9; font-style: italic; }
        .system { background: #fff3e0; color: #666; }
        input, button { padding: 8px; margin: 5px; }
        #status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .connected { background: #c8e6c9; }
        .disconnected { background: #ffcdd2; }
    </style>
</head>
<body>
    <h1>123Therapy Test</h1>
    
    <div id="status" class="disconnected">Disconnected</div>
    
    <div id="room-controls">
        <button onclick="createRoom()">Create Room</button>
        <input type="text" id="room-code" placeholder="Room Code" maxlength="6">
        <button onclick="joinRoom()">Join Room</button>
    </div>
    
    <div id="messages"></div>
    
    <div id="chat-controls" style="display:none;">
        <input type="text" id="message" placeholder="Type a message..." style="width:70%">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <script>
        let socket = null;
        let myRole = null;
        let currentRoom = null;
        
        function connect() {
            socket = io();
            
            socket.on('connect', () => {
                document.getElementById('status').className = 'connected';
                document.getElementById('status').textContent = 'Connected';
            });
            
            socket.on('disconnect', () => {
                document.getElementById('status').className = 'disconnected';
                document.getElementById('status').textContent = 'Disconnected';
            });
            
            socket.on('room_created', (data) => {
                addMessage('system', 'Room created: ' + data.room_code);
                document.getElementById('room-code').value = data.room_code;
            });
            
            socket.on('joined', (data) => {
                myRole = data.role;
                currentRoom = data.room_code;
                addMessage('system', 'Joined as ' + data.role + ': ' + data.message);
                document.getElementById('chat-controls').style.display = 'block';
            });
            
            socket.on('partner_joined', (data) => {
                addMessage('system', data.message);
            });
            
            socket.on('partner_disconnected', (data) => {
                addMessage('system', 'Partner disconnected');
            });
            
            socket.on('new_message', (data) => {
                addMessage(data.sender_role, data.content);
            });
            
            socket.on('error', (data) => {
                addMessage('system', 'Error: ' + data.message);
            });
        }
        
        function addMessage(role, text) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            div.textContent = '[' + role + '] ' + text;
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = 999999;
        }
        
        function createRoom() {
            socket.emit('create_room');
        }
        
        function joinRoom() {
            const code = document.getElementById('room-code').value.trim();
            if (code) {
                socket.emit('join_room', { room_code: code });
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('message');
            if (input.value.trim()) {
                socket.emit('send_message', { content: input.value });
                input.value = '';
            }
        }
        
        document.getElementById('message').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        
        connect();
    </script>
</body>
</html>
'''

@test_bp.route('/test')
def test_page():
    """Serve the test page for WebSocket testing."""
    return render_template_string(TEST_HTML)

