import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class Client:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        self.root = tk.Tk()
        self.root.title("Chat Client")

        self.setup_ui()

        # Thread untuk menerima pesan dari server
        threading.Thread(target=self.receive_messages).start()

        # Thread untuk GUI
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.close_client())
        self.root.mainloop()

    def setup_ui(self):
        # Gaya warna dan font
        self.root.configure(bg='#132043')
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', bg='#FFFFFF', font=('Arial', 12))
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.entry = tk.Entry(self.root, width=50, bg='#FFFFFF', font=('Arial', 12))
        self.entry.bind("<Return>", lambda event: self.send_message())
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(self.root, text="Kirim", command=self.send_message, bg='#4CAF50', fg='white', font=('Arial', 12))
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.update_chat(f"Server: {message}", 'server_message')
            except:
                break

    def send_message(self):
        message = self.entry.get()
        self.update_chat(f"You: {message}", 'user_message')
        self.entry.delete(0, tk.END)
        self.client_socket.send(message.encode('utf-8'))

    def update_chat(self, message, tag=None):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, message + '\n', tag)
        self.chat_area.tag_configure('user_message', foreground='#000000')  # Warna teks pesan dari client
        self.chat_area.tag_configure('server_message', foreground='#008B8B')  # Warna teks pesan dari server
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def close_client(self):
        self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    Client('localhost', 12345)
