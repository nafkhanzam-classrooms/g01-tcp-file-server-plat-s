import socket
import select
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 12345
STORAGE_DIR = 'server_storage'

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    try:
        poller = select.poll()
    except AttributeError:
        print("[!] Error: Sistem operasi ini (kemungkinan Windows) tidak mendukung select.poll(). Gunakan Linux/macOS.")
        return

    poller.register(server, select.POLLIN)

    fd_to_socket = {server.fileno(): server}
    clients = {} 

    print(f"[*] Server Poll berjalan di {HOST}:{PORT}")

    try:
        while True:
            events = poller.poll()

            for fd, flag in events:
                sock = fd_to_socket[fd]

                if sock is server:
                    conn, addr = server.accept()
                    poller.register(conn, select.POLLIN)
                    fd_to_socket[conn.fileno()] = conn
                    clients[conn] = addr
                    print(f"[{get_time()}] {addr[0]}:{addr[1]} > CONNECTED")
                
                elif flag & select.POLLIN:
                    try:
                        data = sock.recv(4096).decode()
                        addr = clients[sock]

                        if not data:
                            print(f"[{get_time()}] {addr[0]}:{addr[1]} > DISCONNECTED")
                            poller.unregister(sock)
                            del fd_to_socket[fd]
                            del clients[sock]
                            sock.close()
                            continue

                        parts = data.split(':', 2)
                        command = parts[0]

                        if command == "LIST":
                            files = os.listdir(STORAGE_DIR)
                            response = "FILE_LIST:" + (",".join(files) if files else "Kosong")
                            sock.send(response.encode())

                        elif command == "UPLOAD":
                            filename, content = parts[1], parts[2]
                            with open(os.path.join(STORAGE_DIR, filename), 'w') as f:
                                f.write(content)
                            sock.send(f"SUCCESS:File {filename} berhasil diunggah".encode())

                        elif command == "CHAT":
                            pesan = parts[1]
                            for c_sock in clients:
                                if c_sock != sock:
                                    c_sock.send(f"Chat dari {addr[1]}: {pesan}".encode())
                            sock.send(f"ACK: Pesan terkirim".encode())

                        elif command == "DOWNLOAD":
                            filename = parts[1]
                            filepath = os.path.join(STORAGE_DIR, filename)
                            if os.path.exists(filepath):
                                with open(filepath, 'r') as f:
                                    sock.send(f"FILE_DATA:{filename}:{f.read()}".encode())
                            else:
                                sock.send(f"ERROR:File {filename} tidak ditemukan".encode())

                    except Exception as e:
                        poller.unregister(sock)
                        del fd_to_socket[fd]
                        if sock in clients:
                            del clients[sock]
                        sock.close()

    except KeyboardInterrupt:
        print("\n[*] Server dimatikan.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()