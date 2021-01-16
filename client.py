import os
import time
import json
import socket
import configparser
from threading import Thread


class Client:
    def __init__(self, address, display_message, start_new_server):
        self.server_address = address
        self.display_message = display_message
        self.start_new_server = start_new_server
        self.is_running = True
        self.socket = socket.socket()
        self.connections = []
        self.connections_info = []
        self.has_new_connections_info = True
        thread = Thread(target=self.get_raw_data)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.is_running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_raw_data(self):
        try:
            self.socket.connect(self.server_address)
            self.display_message("Server", "Connected to Chat")
            thread = Thread(target=self.send_actual_user_info)
            thread.daemon = True
            thread.start()
        except socket.error as e:
            self.display_message("Server", "No connection")
            print("Error: " + str(e))
            return
        while self.is_running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    raise socket.error
                else:
                    self.filter_raw_data(data)
            except socket.error as e:
                if not self.is_running:
                    return
                self.display_message("Server", "Server has disconnected")
                self.restart_server()
                break

    def send_actual_user_info(self):
        current = 0
        while self.is_running:
            modified = os.path.getmtime("cnf.ini")
            if current < modified:
                config = configparser.ConfigParser()
                config.read("cnf.ini")
                name = config.get("USER INFO", "nickname")
                self.socket.sendall(
                    json.dumps({"User": {"nickname": name}}).encode())
                current = modified
            time.sleep(1)

    def filter_raw_data(self, data):
        messages = data.decode().split("}{")
        if len(messages) > 1:
            messages = [messages[0] + "}"] + ["{" + i + "}" for i in messages[1:-1]] + ["{" + messages[-1]]
        for message in messages:
            self.filter_message(message)

    def send_message(self, name, text):
        config = configparser.ConfigParser()
        config.read("cnf.ini")
        self.socket.sendall(json.dumps({"nickname":  name,
                                      "text": text}).encode())

    def filter_message(self, message):
        json_data = json.loads(message)
        if "connections_list" in json_data:
            if len(json_data["connections_list"]) == 0:
                self.connections = []
            else:
                self.connections = [tuple(l) for l in json_data["connections_list"]]
        elif "users_data" in json_data:
            self.connections_info = list(json_data["users_data"])
            self.has_new_connections_info = True
        else:
            self.display_message(json_data["nickname"], json_data["text"])

    def restart_server(self):
        self.connections.sort(key=lambda tup: str(tup))
        if self.connections[0] == self.socket.getsockname():
            self.start_new_server(('', self.server_address[1]))
            self.server_address = ('127.0.0.1', self.server_address[1])
            self.display_message("Server", "You are host now")
        else:
            self.server_address = (self.connections[0][0], self.server_address[1])
            time.sleep(1)

        self.socket.close()
        self.socket = socket.socket()
        thread = Thread(target=self.get_raw_data)
        thread.daemon = True
        thread.start()
