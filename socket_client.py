import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

try:
    sio.connect('http://localhost:8000', socketio_path='/socket.io')
    sio.wait()
except Exception as e:
    print(f"An error occurred: {e}")
