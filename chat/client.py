import socket
import threading

channel_selected = False
channel = None
running = True

def receive(client):
    global channel_selected, channel, running
    while running: 
        try:
            message = client.recv(1024).decode()
            if message == 'nickname':
                client.send(nickname.encode())
            elif message == 'channel' and not channel_selected:
                channel_selected = True
            else:
                print(message)
        except:
            if running:
                print("Something went wrong.")
                client.close()
            break

def write(client):
    global channel_selected, channel, running
    while running: 
        if channel_selected and channel is None:
            channel = input("Join the channel: ")
            client.send(channel.encode())
            channel_selected = False
        else:
            message_input = input('')
            if message_input.lower() == "disconnect":
                print("Disconnecting from the server.")
                running = False 
                client.send("Disconnect".encode())
                client.close()
                break
            client.send(message_input.encode())

if __name__ == "__main__":
    nickname = input("Set the nickname: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 4399))

    receive_thread = threading.Thread(target=receive, args=(client,))
    receive_thread.start()

    write_thread = threading.Thread(target=write, args=(client,))
    write_thread.start()