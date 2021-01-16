import chatWindow
import configparser
import tkinter as tk
from tkinter import ttk


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("1000x630")
        self.title("Small Messanger")
        menu = tk.Menu(self)
        menu.add_command(label="+", command=self.create_new_chat)
        menu.add_command(label="Settings", command=SettingsWindow)
        self.config(menu=menu)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both")
        self.chats = dict()
        self.images = tk.PhotoImage(data='''
                                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                                5kEJADs=
                                ''')

        self.create_new_chat()
        self.stylling()

    def create_new_chat(self):
        frame = SettingWindow(self)
        self.notebook.add(frame, text="Let's Connect to Chat...")
        self.notebook.select(len(self.notebook.tabs()) - 1)

    def close_current_tab(self, event):
        element = self.notebook.identify(event.x, event.y)
        if "close" in element:
            chat_index = self.notebook.index(self.notebook.select())
            if chat_index in self.chats:
                self.chats[chat_index].close()
                self.chats.pop(chat_index)
            self.notebook.forget(chat_index)
            if len(self.notebook.tabs()) == 0:
                self.create_new_chat()

    def update_chat_window(self, frame, new_text):
        chat_index = self.notebook.index(self.notebook.select())
        if isinstance(frame, chatWindow.ChatWindow):
            self.chats[chat_index] = frame
        self.notebook.forget(self.notebook.select())
        if chat_index != len(self.notebook.tabs()):
            self.notebook.insert(chat_index, frame, text=new_text)
        else:
            self.notebook.add(frame, text=new_text)
            self.notebook.select(chat_index)

    def stylling(self):
        style = ttk.Style()
        style.element_create("close", "image", self.images,
                             border=8, sticky='')
        style.layout("TNotebook", [("TNotebook.client", {"sticky": "nswe"})])
        style.layout("TNotebook.Tab", [
            ("TNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("TNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("TNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("TNotebook.label", {"side": "left", "sticky": ''}),
                                    ("TNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        self.notebook.bind("<ButtonRelease-1>", self.close_current_tab)


class SettingWindow(tk.Frame):
    def __init__(self, main_window):
        tk.Frame.__init__(self, main_window.notebook)
        self.notebook = main_window.notebook
        self.main_window = main_window
        self.input = None
        self.input_port1 = None
        self.input_port2 = None
        self.set_widgets()

    def set_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        tk.Label(self, text="Connect To Chat", font=16).grid(pady=20, sticky="NSEW")
        tk.Label(self, text="Enter IP:").grid(row=1, column=0, sticky="NSEW")
        self.input = tk.Entry(self)
        self.input_port1 = tk.Entry(self)
        self.input.insert(tk.END, '127.0.0.1')
        self.input_port1.insert(tk.END, "50322")
        self.input.grid()
        self.input_port1.grid()
        self.input_port2 = tk.Entry(self)
        self.input_port2.insert(tk.END, "50322")
        tk.Button(self, text="Connect", command=self.connect).grid(pady=10)

        tk.Label(self, text="or", font=12).grid(pady=20, sticky="NSEW")
        tk.Label(self, text="Create New Chat", font=16).grid(pady=20, sticky="NSEW")
        self.input_port2.grid()
        tk.Button(self, text="Create", command=self.host_chat).grid()

    def connect(self):
        address = (self.input.get(), int(self.input_port1.get()))
        self.main_window.update_chat_window(chatWindow.ChatWindow(self.notebook,
                                                                  "con",
                                                                  address),
                                            "Welcome to Chat")

    def host_chat(self):
        address = ("", int(self.input_port2.get()))
        self.main_window.update_chat_window(chatWindow.ChatWindow(self.notebook,
                                                                  "host",
                                                                  address),
                                            "Welcome to Chat")


class SettingsWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.nickname = None
        self.set_widgets()

    def set_widgets(self):
        self.title("Settings")
        self.geometry("200x120")
        self.config = configparser.ConfigParser()
        self.config.read("cnf.ini")
        tk.Label(self, text="NickName: ").grid(column=0, pady=20)
        self.nickname = tk.Entry(self)
        self.nickname.grid(row=0, column=1, pady=20)
        self.nickname.insert(0, self.config["USER INFO"]["nickname"])
        tk.Button(self, text="Apply", width=20, command=self.save_configurations).grid(row=1, columnspan=2, pady=30)

    def save_configurations(self):
        self.config.set("USER INFO",  "nickname", self.nickname.get())
        with open('cnf.ini', 'w') as config_file:
            self.config.write(config_file)
        self.destroy()
