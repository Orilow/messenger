import unittest
import time
from server import Server
from client import Client


class Tests(unittest.TestCase):
    def after_each_test(self, *args):
        for arg in args:
            arg.stop()

    def get_messages(self, name, text):
        self.nickname = name
        self.message = text

    def test_successful_connection(self):
        server = Server(('127.0.0.1', 51111))
        try:
            client = Client(('127.0.0.1', 51111), self.get_messages, None)
        except:
            raise ConnectionError("Can't connect")

    def test_simple_connection(self):
        server = Server(('127.0.0.1', 25000))
        client = Client(('127.0.0.1', 25000), self.get_messages, None)
        time.sleep(1)
        client.send_message("bot", "Test")
        time.sleep(1)
        self.assertEqual("Test", self.message)
        self.assertEqual("bot", self.nickname)
        self.after_each_test(client, server)

    def test_double_connection(self):
        server = Server(('127.0.0.1', 51111))
        client1 = Client(('127.0.0.1', 51111), lambda x, y: None, None)
        client2 = Client(('127.0.0.1', 51111), self.get_messages, None)
        time.sleep(0.2)
        client1.send_message("bot", "Test")
        time.sleep(1)
        self.assertEqual("Test", self.message)
        self.assertEqual("bot", self.nickname)
        self.after_each_test(client1, client2, server)

    def test_server_down_and_restart(self):
        server = Server(('127.0.0.1', 51111))
        def new_server(address):
            Server(address)
        client1 = Client(('127.0.0.1', 51111), lambda x, y: None, new_server)
        client2 = Client(('127.0.0.1', 51111), self.get_messages, new_server)
        time.sleep(1)
        server.stop()
        time.sleep(2)
        client1.send_message("bot", "Test")
        time.sleep(0.2)
        self.assertEqual("Test", self.message)
        self.assertEqual("bot", self.nickname)
        self.after_each_test(client1, client2, server)
