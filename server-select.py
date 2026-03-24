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
    
    sockets_list = [server]
    clients = {}

    print(f"[*] Server Select berjalan di {HOST}:{PORT}")

    try:
        while True:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

            for notified_socket in read_sockets:
                if notified_socket == server:
                    conn, addr = server.accept()
                    sockets_list.append(conn)
                    clients[conn] = addr
                    print(f"[{get_time()}] {addr[0]}:{addr[1]} > CONNECTED")
                
                else:
                    try:
                        data = notified_socket.recv(4096).decode()
                        addr = clients[notified_socket]
                        
                        if not data:
                            print(f"[{get_time()}] {addr[0]}:{addr[1]} > DISCONNECTED")
                            sockets_list.remove(notified_socket)
                            del clients[notified_socket]
                            continue

                        parts = data.split(':', 2)
                        command = parts[0]

                        if command == "LIST":
                            files = os.listdir(STORAGE_DIR)
                            response = "FILE_LIST:" + (",".join(files) if files else "Kosong")
                            notified_socket.send(response.encode())
                            print(f"[{get_time()}] {addr[0]}:{addr[1]} > LIST REQUESTED")

                        elif command == "UPLOAD":
                            filename, content = parts[1], parts[2]
                            with open(os.path.join(STORAGE_DIR, filename), 'w') as f:
                                f.write(content)
                            notified_socket.send(f"SUCCESS:File {filename} berhasil diunggah".encode())
                            print(f"[{get_time()}] {addr[0]}:{addr[1]} > UPLOADED: {filename}")

                        elif command == "CHAT":
                            pesan = parts[1]
                            for client_socket in clients:
                                if client_socket != notified_socket:
                                    client_socket.send(f"Chat dari {addr[1]}: {pesan}".encode())
                            notified_socket.send(f"ACK: Pesan terkirim".encode())
                            print(f"[{get_time()}] {addr[0]}:{addr[1]} > CHAT BROADCASTED")

                        elif command == "DOWNLOAD":
                            filename = parts[1]
                            filepath = os.path.join(STORAGE_DIR, filename)
                            if os.path.exists(filepath):
                                with open(filepath, 'r') as f:
                                    notified_socket.send(f"FILE_DATA:{filename}:{f.read()}".encode())
                            else:
                                notified_socket.send(f"ERROR:File {filename} tidak ditemukan".encode())

                    except Exception as e:
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]

            for notified_socket in exception_sockets:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]

    except KeyboardInterrupt:
        print("\n[*] Server dimatikan.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()