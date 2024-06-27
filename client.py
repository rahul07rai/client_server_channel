import socket
import json

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_commands(self, commands):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))
            client_socket.sendall(json.dumps(commands).encode())
            
            response = client_socket.recv(4096)
            return json.loads(response.decode())

class CommandSender:
    def __init__(self, client):
        self.client = client

    def send(self, commands):
        responses = self.client.send_commands(commands)
        for response in responses:
            self.print_response(response)

    def print_response(self, response):
        print('Response from server:', response)

if __name__ == '__main__':
    host = 'localhost'
    port = 8000
    commands = [
        {'method': 'date', 'id': 1},
        {'method': 'hostname', 'id': 2},
        {'method': 'uptime', 'id': 3}
    ]
    
    client = Client(host, port)
    sender = CommandSender(client)
    sender.send(commands)

