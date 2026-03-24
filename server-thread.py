import socket
import threading
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 12345
STORAGE_DIR = 'server_storage'

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

clients = [] 

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def broadcast(message, sender_conn):
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message.encode())
            except:
                clients.remove(client)

def handle_client(conn, addr):
    print(f"[{get_time()}] {addr[0]}:{addr[1]} > CONNECTED")
    try:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            
            parts = data.split(':', 2)
            command = parts[0]

            if command == "LIST":
                files = os.listdir(STORAGE_DIR)
                response = "FILE_LIST:" + (",".join(files) if files else "Kosong")
                conn.send(response.encode())
                print(f"[{get_time()}] {addr[0]}:{addr[1]} > LIST REQUESTED")

            elif command == "UPLOAD":
                filename, content = parts[1], parts[2]
                with open(os.path.join(STORAGE_DIR, filename), 'w') as f:
                    f.write(content)
                conn.send(f"SUCCESS:File {filename} berhasil diunggah".encode())
                print(f"[{get_time()}] {addr[0]}:{addr[1]} > UPLOADED: {filename}")

            elif command == "CHAT":
                pesan = parts[1]
                broadcast(f"Chat dari {addr[1]}: {pesan}", conn)
                conn.send(f"ACK: Pesan '{pesan}' terkirim ke semua".encode())
                print(f"[{get_time()}] {addr[0]}:{addr[1]} > CHAT BROADCASTED: {pesan}")
            
            elif command == "DOWNLOAD":
                filename = parts[1]
                filepath = os.path.join(STORAGE_DIR, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        conn.send(f"FILE_DATA:{filename}:{f.read()}".encode())
                    print(f"[{get_time()}] {addr[0]}:{addr[1]} > DOWNLOADED: {filename}")
                else:
                    conn.send(f"ERROR:File {filename} tidak ditemukan".encode())
                    print(f"[{get_time()}] {addr[0]}:{addr[1]} > DOWNLOAD FAILED: {filename}")
    except:
        pass
    finally:
        print(f"[{get_time()}] {addr[0]}:{addr[1]} > DISCONNECTED")
        if conn in clients:
            clients.remove(conn)
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Server Thread berjalan di {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            clients.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
    except Exception as e:
        print(f"[!] Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()