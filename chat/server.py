import socket
import threading

class ChatServer:
    def __init__(self, host='127.0.0.1', port=4399):
        self.clients = {}
        self.nicknames = {}
        self.channels = {"general": set()}
        self.client_channels = {}
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        print(f"Server is starting on {host}:{port}...")
        self.server.listen()
        print("Server is listening")

    def show_information(self, message, sender=None):
        channel = self.client_channels[sender]
        for client in self.channels[channel]:
            if client != sender:
                client.send(message)

    def private_message(self, message, sender):
        try:
            _, nickname, msg = message.split(' ', 2)
            if nickname in self.nicknames:
                target_client = self.nicknames[nickname]
                sender_nickname = self.clients[sender]
                target_client.send(f"[Private] {sender_nickname}: {msg}".encode())
                print(f"Private message from {sender_nickname} to {nickname}")
            else:
                sender.send(f"Nickname {nickname} not found.".encode())
        except ValueError:
            sender.send("The private message format is invalid. Use [Private] <nickname> <message>".encode())

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode()
                if message == "Disconnect":
                    raise Exception("Client requested disconnection.")
                elif message.startswith('[Private]'):
                    self.private_message(message, client)
                else:
                    channel = self.client_channels[client]
                    message_to_broadcast = f"[Channel: {channel}] {self.clients[client]}: {message}"
                    self.show_information(message_to_broadcast.encode(), client)
            except:
                nickname = self.clients.get(client)
                if nickname:
                    print(f"{nickname} has disconnected.")
                    disconnection_message = f"{nickname} has left the chat system."
                    self.show_information(disconnection_message.encode(), client)
                    self.clients.pop(client)
                    self.nicknames.pop(nickname, None)
                    channel = self.client_channels.pop(client, None)
                    if channel:
                        self.channels[channel].remove(client)
                try:
                    client.close()
                except OSError:
                    pass
                break

    def connections(self):
        while True:
            client, address = self.server.accept()
            print(f"Already connected with {str(address)}")

            client.send('nickname'.encode())
            nickname = client.recv(1024).decode()
            self.clients[client] = nickname
            self.nicknames[nickname] = client

            client.send('channel'.encode())
            channel = client.recv(1024).decode()
            if channel not in self.channels:
                self.channels[channel] = set()
            self.channels[channel].add(client)
            self.client_channels[client] = channel

            print(f"{nickname} joined channel {channel}")
            client.send(f'Connected to the server and joined {channel} channel successfully. You can chat now.'.encode())
            self.show_information(f"{nickname} joined the chat in {channel} channel.".encode(), client)

            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.connections()
