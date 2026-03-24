import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 12345

def receive_messages(sock):
    while True:
        try:
            response = sock.recv(4096).decode()
            if not response: break
            
            if response.startswith("FILE_DATA:"):
                _, name, content = response.split(':', 2)
                with open(f"client_rec_{name}", 'w') as f:
                    f.write(content)
                print(f"\r[*] File {name} berhasil diunduh.\nInput > ", end="", flush=True)
            else:
                print(f"\r[SERVER] {response}")
                print("Input > ", end="", flush=True)
        except:
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((HOST, PORT))
        print(f"[*] Terhubung ke {HOST}:{PORT}")
        print("[*] Perintah: /list, /upload <file>, /download <file>, /exit")

        threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

        while True:
            user_input = input("Input > ")
            if not user_input: continue
            if user_input == "/exit": break
            
            if user_input.startswith('/list'):
                client.send("LIST".encode())
            
            elif user_input.startswith('/upload'):
                parts = user_input.split(maxsplit=1)
                if len(parts) == 2 and os.path.exists(parts[1]):
                    with open(parts[1], 'r') as f:
                        client.send(f"UPLOAD:{parts[1]}:{f.read()}".encode())
                else:
                    print("Error: File tidak ditemukan atau format salah.")

            elif user_input.startswith('/download'):
                parts = user_input.split(maxsplit=1)
                if len(parts) == 2:
                    client.send(f"DOWNLOAD:{parts[1]}".encode())
                else:
                    print("Gunakan: /download <filename>")

            else:
                client.send(f"CHAT:{user_input}".encode())

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client.close()
        print("[*] Koneksi ditutup.")

if __name__ == "__main__":
    start_client()