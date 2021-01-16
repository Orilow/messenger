import time
import configparser
import tkinter as tk
from tkinter.ttk import *
from client import Client
from server import Server
from threading import Thread
from tkinter.scrolledtext import ScrolledText


class ChatWindow(Frame):
    def __init__(self, parent, mode, address):
        Frame.__init__(self, parent)
        self.parent = parent
        self.config = configparser.ConfigParser()
        self.config.read("cnf.ini")
        self.server = None
        self.chat = None
        self.input = None
        self.panel = None

        self.set_widgets_before_connection()

        if mode == "con":
            self.client = Client(address, self.chat.display_message, self.start_new_server)
        elif mode == "host":
            self.server = Server(address)
            self.client = Client(("127.0.0.1", 50322), self.chat.display_message, self.start_new_server)

        self.set_widgets_after_connection()

    def set_widgets_before_connection(self):
        self.columnconfigure(0, weight=1)
        self.chat = MessagesWindow(self)
        self.chat.grid(sticky='NSEW')
        self.grid_columnconfigure(1, minsize=100, weight=1)
        self.input = tk.Text(self, height=2, font=("Helvetica", 10))
        self.input.grid(row=1, column=0, sticky='NSEW')
        btn = Button(self, text="Send", command=self.send_action)
        btn.grid(row=1, column=1)
        self.input.bind('<Return>', self.send_action)

    def set_widgets_after_connection(self):
        self.panel = Panel(self.client, self)
        self.panel.grid(row=0, column=1, sticky='NSEW')

    def send_action(self, _=None):
        message_text = self.input.get("1.0", 'end-1c')
        self.input.delete("1.0", tk.END)
        if message_text == "":
            return 'break'
        self.config.read("cnf.ini")
        self.client.send_message(self.config["USER INFO"]["nickname"], message_text)
        return 'break'

    def close(self):
        self.panel.stop()
        self.client.stop()
        time.sleep(0.2)
        if self.server:
            self.server.stop()

    def start_new_server(self, address):
        self.server = Server(address)


class MessagesWindow(ScrolledText):
    def __init__(self, *args, **kwargs):
        ScrolledText.__init__(self, *args, **kwargs)
        self.config(bg="#a7bbe2")
        self.pack(fill="both")
        self.configure(state="disabled")
        self.configure(font=("Helvetica", 13))

    def display_message(self, nickname, message_text):
        self.configure(state="normal")
        self.insert(tk.END, nickname + ": ")
        self.insert(tk.END, message_text + "\n")
        self.configure(state="disabled")


class Panel(Frame):
    def __init__(self, client, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.is_running = True
        self.client = client
        self.label = None
        self.labels = []
        thread = Thread(target=self.show_chat_members)
        thread.daemon = True
        thread.start()

    def show_chat_members(self):
        while self.is_running:
            time.sleep(1)
            if not self.client.has_new_connections_info:
                continue
            self.client.has_new_connections_info = False
            for widget in self.winfo_children():
                widget.destroy()
            self.label = Label(self, text="Chat members:")
            self.label.pack(pady=5)
            for user in self.client.connections_info:
                label = Label(self, text=(user["nickname"]), font='Arial 10')
                label.pack()
                self.labels.append(label)

    def stop(self):
        self.is_running = False
