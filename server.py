import socket
import json
import threading
import subprocess

class ShellCommandExecutor:
    def execute(self, command):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        except Exception as e:
            return 4, '', str(e)

class RequestHandler:
    def __init__(self):
        self.executor = ShellCommandExecutor()

    def handle_request(self, request):
        command = request.get('method')
        request_id = request.get('id')
        
        if not command or request_id is None:
            return {'result': None, 'stdout': '', 'stderr': 'Invalid request', 'id': request_id, 'error_code': 2}
        
        returncode, stdout, stderr = self.executor.execute(command)
        error_code = 0 if returncode == 0 else 3 if returncode != 0 else 4
        
        return {
            'result': returncode,
            'stdout': stdout,
            'stderr': stderr,
            'id': request_id,
            'error_code': error_code
        }

    def handle_requests(self, requests):
        responses = []
        threads = []
        results = [None] * len(requests)

        def thread_func(i, req):
            results[i] = self.handle_request(req)
        
        for i, request in enumerate(requests):
            thread = threading.Thread(target=thread_func, args=(i, request))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        return results

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.request_handler = RequestHandler()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f'Server listening on {self.host}:{self.port}')
            
            while True:
                client_socket, client_address = server_socket.accept()
                with client_socket:
                    print(f'Connected by {client_address}')
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    try:
                        requests = json.loads(data.decode())
                    except json.JSONDecodeError:
                        response = [{'result': None, 'stdout': '', 'stderr': 'JSON parse error', 'id': None, 'error_code': 1}]
                        client_socket.sendall(json.dumps(response).encode())
                        continue
                    
                    if not isinstance(requests, list):
                        requests = [requests]

                    responses = self.request_handler.handle_requests(requests)
                    client_socket.sendall(json.dumps(responses).encode())

if __name__ == '__main__':
    server = Server('localhost', 8000)
    server.start()

