import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class Server:
    def __init__(self, host, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []

        self.root = tk.Tk()
        self.root.title("Chat Server")

        self.setup_ui()

        # Thread untuk menerima koneksi dari klien
        threading.Thread(target=self.accept_clients).start()

        # Thread untuk GUI
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.close_server())
        self.root.mainloop()

    def setup_ui(self):
        # Gaya warna dan font
        self.root.configure(bg='#132043')
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', bg='#FFFFFF', fg='#333333', font=('Arial', 12))
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.entry = tk.Entry(self.root, width=50, bg='#FFFFFF', fg='#333333', font=('Arial', 12))
        self.entry.bind("<Return>", lambda event: self.send_message())
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(self.root, text="Kirim", command=self.send_message, bg='#4CAF50', fg='white', font=('Arial', 12))
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Tag untuk konfigurasi pesan pengguna dan pesan sistem
        self.chat_area.tag_configure('user_message', font=('Arial', 12))
        self.chat_area.tag_configure('server_message', font=('Arial', 12, 'italic'), foreground='#008B8B')

    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            self.update_chat(f"[{addr[0]}:{addr[1]}] connected")

            # Thread untuk menangani pesan dari klien
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    self.update_chat(f"[{addr[0]}:{addr[1]}] disconnected")
                    self.remove_client(client_socket)
                    break

                self.update_chat(f"[{addr[0]}:{addr[1]}] {message}")

            except ConnectionResetError:
                self.update_chat(f"[{addr[0]}:{addr[1]}] disconnected forcibly")
                self.remove_client(client_socket)
                break

    def send_message(self):
        message = self.entry.get()
        self.update_chat(f"You (Server): {message}")
        self.entry.delete(0, tk.END)

        # Kirim pesan ke semua klien yang terhubung
        for client_socket in self.clients:
            try:
                client_socket.send(message.encode('utf-8'))
            except:
                self.remove_client(client_socket)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)

    def update_chat(self, message):
        self.chat_area.configure(state='normal')
        if "You (Server)" in message:
            self.chat_area.insert(tk.END, message + '\n', 'server_message')
        else:
            self.chat_area.insert(tk.END, message + '\n', 'user_message')
        self.chat_area.configure(state='disabled')
        self.chat_area.yview(tk.END)

    def close_server(self):
        # Tutup semua klien sebelum menutup server
        for client in self.clients:
            client.close()
        self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    Server('localhost', 12345)
