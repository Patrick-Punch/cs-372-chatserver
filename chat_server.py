import socket
import select
import json
import sys

clients = {}

def broadcast(message):
    global clients
    for client_socket in clients.keys():
        length = len(message)
        client_socket.send(length.to_bytes(2) + message)

def handle_client_msg(client_socket):
    global clients
    header = client_socket.recv(2)
    if len(header) < 2:
        print("Error processing header")

    length = int.from_bytes(header)
    data = client_socket.recv(length).decode()
    message = json.loads(data)
    nickname, _ = clients.get(client_socket)
    if message['type'] == "chat":
        chat_message = {
            "type": "chat",
            "nick": nickname,
            "message": message["message"]
        }
        broadcast(json.dumps(chat_message).encode())


def run_server(port):
    global clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen()
    print(f"Server is listening on port {port}")

    sockets = [server_socket]

    try:
        while True:
            read_sockets, _, _ = select.select(sockets, [], [])
            for s in read_sockets:
                if s == server_socket:
                    client_socket, client_address = server_socket.accept()
                    print(f"Connection from {client_address}")

                    length_bytes = client_socket.recv(2)
                    length = int.from_bytes(length_bytes)
                    data = client_socket.recv(length).decode()
                    hello_msg = json.loads(data)
                    nickname = hello_msg['nick']
                    clients[client_socket] = (nickname, client_address)

                    # Broadcast the join message
                    join_msg = {
                        "type": "join",
                        "nick": nickname
                    }
                    broadcast(json.dumps(join_msg).encode())
                    sockets.append(client_socket)

                else:
                    try:
                        handle_client_msg(s)
                    except json.JSONDecodeError:
                        nickname, client_address = clients.get(s)
                        # Broadcast the leave message
                        print(f"Connection ended from {client_address}")
                        leave_msg = {
                            "type": "leave",
                            "nick": nickname
                        }
                        broadcast(json.dumps(leave_msg).encode())
                        sockets.remove(s)
                        del clients[s]
                        s.close()
    except KeyboardInterrupt:
        print(" Closing the chat server.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chat_server.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    run_server(port)