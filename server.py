import json
import socket
from threading import Thread
import time


class Server:
    def __init__(self, server_address):
        self.address = server_address
        self.socket = socket.socket()
        try:
            self.socket.bind(self.address)
        except socket.error:
            pass
        self.connections = {}
        self.main_client = None
        self.messages = []
        self.is_running = True
        self.socket.listen(16)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.start_threads()

    def start_threads(self):
        thread = Thread(target=self.waiting_for_connections)
        thread.daemon = True
        thread.start()
        thread2 = Thread(target=self.send_to_all)
        thread2.daemon = True
        thread2.start()

    def waiting_for_connections(self):
        while self.is_running:
            try:
                connection, address = self.socket.accept()
                if not self.main_client:
                    self.main_client = address
                self.connections.update({connection: json.loads(connection.recv(1024).decode())['User']})
                self.send_all_connections()
                self.send_server_message("New connection detected: " + str(address))
                thread = Thread(target=self.get_raw_data, args=[connection, address])
                thread.daemon = True
                thread.start()
            except socket.error as e:
                if not self.is_running:
                    return
                print("Error: Disconnected to Internet")
                print(e)

    def get_raw_data(self, connection, address):
        while self.is_running:
            try:
                data = connection.recv(1024)
            except socket.error:
                self.send_server_message("Client " + self.connections[connection]['nickname'] + str(address) +
                                         " has disconnected")
                self.connections.pop(connection)
                self.send_all_connections()
                break
            if data:
                messages = data.decode().split("}{")
                if len(messages) > 1:
                    messages = [messages[0] + "}"] +\
                               ["{" + i + "}" for i in messages[1:-1]] +\
                               ["{" + messages[-1]]
                for message in messages:
                    self.handle_raw_message(message, connection)

    def send_to_all(self):
        while self.is_running:
            time.sleep(0.1)
            for message in self.messages:
                for connection in self.connections.keys():
                    connection.sendall(message.encode())
                self.messages.remove(message)

    def handle_raw_message(self, message, connection):
        json_data = json.loads(message)
        if "User" in json_data:
            self.connections[connection] = json_data['User']
            self.send_all_connections()
        else:
            self.messages.append(message)

    def send_server_message(self, text):
        self.messages.append(json.dumps(
            {"nickname": "Server", "text": text}))

    def send_all_connections(self):
        connections = [connection.getpeername() for connection in self.connections.keys()
                       if connection.getpeername() != self.main_client]
        self.messages.append(json.dumps({"connections_list": connections}))
        self.messages.append(json.dumps({"users_data": list(self.connections.values())}))

    def stop(self):
        self.is_running = False
        for connection in list(self.connections.keys()):
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
        self.socket.close()
