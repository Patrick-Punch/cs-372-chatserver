import sys
import socket
import threading
import json
from chatui import init_windows, read_command, print_message, end_windows

client_socket = None
nickname = ""

def receive_msg():
    global client_socket
    while True:
        header = client_socket.recv(2)
        if len(header) < 2:
            break
        length = int.from_bytes(header)
        data = client_socket.recv(length).decode()
        message = json.loads(data)

        if message['type'] == 'chat':
            print_message(f"{message['nick']}: {message['message']}")
        elif message['type'] == 'join':
            print_message(f"*** {message['nick']} has joined the chat")
        elif message['type'] == 'leave':
            print_message(f"*** {message['nick']} has left the chat")

def send_msg():
    global client_socket, nickname
    while True:
        command = read_command(f"{nickname}> ")
        
        if command == "/q":
            client_socket.send(json.dumps({"type": "leave", "nick": nickname}).encode())
            break
        elif command:
            msg_packet = {
                "type": "chat",
                "message": command
            }
            json_data = json.dumps(msg_packet).encode()
            length = len(json_data)
            client_socket.send(length.to_bytes(2) + json_data)

def main(argv):
    global client_socket, nickname

    if len(argv) != 4:
        print("Usage: python chat_client.py nickname host port")
        return

    nickname = argv[1]
    host = argv[2]
    port = int(argv[3])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    init_windows()

    hello_packet = {
        "type": "hello",
        "nick": nickname
    }
    json_data = json.dumps(hello_packet).encode()
    length = len(json_data)
    client_socket.send(length.to_bytes(2) + json_data)

    receive_thread = threading.Thread(target=receive_msg, daemon=True)
    receive_thread.start()

    send_msg()
    end_windows()

if __name__ == "__main__":
    main(sys.argv)