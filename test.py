import socketio
import time

# Create a Socket.IO client
sio = socketio.Client()

# Define the server URL (adjust the port if necessary)
SERVER_URL = 'http://localhost:3000'

@sio.event
def connect():
    print("Connected to the server.")

@sio.event
def disconnect():
    print("Disconnected from the server.")

@sio.event
def question(data):
    print("Received question response:", data)

def send_question():
    question_data = {
        "id": "12345",  # Example question ID
        "text": "What is the capital of France1?"  # Example question text
    }
    # Emit the question to the server
    sio.emit('receive_external_question', question_data)

if __name__ == '__main__':
    # Connect to the server
    sio.connect(SERVER_URL)

    # Give some time for the connection to establish
    time.sleep(1)

    # Send a question
    send_question()

    # Wait for a while to receive responses
    time.sleep(5)

    # Disconnect from the server
    sio.disconnect()