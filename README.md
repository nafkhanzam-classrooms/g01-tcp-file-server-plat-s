[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
|Zulkarnaen Ramdhani | 5025241043 | ProgJar D |
| Vityaz Ali Firdaus | 5025241050 | ProgJar D |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```
https://youtu.be/mqZDwa2pu_A
```

## Penjelasan Program

1. Pendekatan Multi-Threading (server-thread.py)
   Pendekatan pertama menggunakan modul threading bawaan Python untuk mendelegasikan setiap koneksi klien ke dalam proses atau "jalur" yang terpisah.

```
# ... [inisialisasi socket] ...
clients = [] # Menyimpan daftar klien untuk fitur broadcast

def start_server():
    # ... [bind dan listen] ...
    try:
        while True:
            conn, addr = server.accept()
            clients.append(conn)
            
            # Membuat thread baru khusus untuk klien yang baru terhubung
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
    except Exception as e:
        print(f"[!] Server error: {e}")
```

Pada arsitektur synchronous, fungsi server.accept() dan proses penerimaan pesan ( recv() ) akan memblokir (block) jalannya program utama. Dengan menggunakan threading.Thread, setiap kali ada klien baru yang terhubung, server akan menugaskan sebuah thread baru untuk menjalankan fungsi handle_client.

Dengan cara ini, thread utama (Main Thread) dapat langsung kembali ke posisi server.accept() untuk menunggu klien berikutnya, sementara thread anakan mengurus transfer file dan chat dari klien yang sudah terhubung. Selain itu, ditambahkan list clients secara global untuk menyimpan koneksi yang aktif, yang nantinya di-looping pada fungsi broadcast() agar pesan chat dari satu klien dapat diteruskan ke klien lainnya secara real-time.

2. Pendekatan I/O Multiplexing (server-select.py)
   Pendekatan kedua menggunakan modul select untuk memantau aktivitas banyak socket sekaligus dalam satu thread tunggal (tanpa membuat thread baru).

```
# ... [inisialisasi socket] ...
sockets_list = [server] # Daftar socket yang dipantau
clients = {} 

def start_server():
    # ... [bind dan listen] ...
    try:
        while True:
            # Memantau socket mana yang siap dibaca (Non-blocking)
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

            for notified_socket in read_sockets:
                # Kondisi 1: Jika server menerima koneksi baru
                if notified_socket == server:
                    conn, addr = server.accept()
                    sockets_list.append(conn)
                    clients[conn] = addr
                
                # Kondisi 2: Jika ada pesan/perintah dari klien yang sudah terhubung
                else:
                    data = notified_socket.recv(4096).decode()
                    # ... [Logika pemrosesan perintah LIST, UPLOAD, DOWNLOAD, CHAT] ...   
```

Alih-alih membuat banyak thread yang dapat membebani CPU dan memori, metode ini memanfaatkan I/O Multiplexing. Fungsi select.select() menerima daftar koneksi (sockets_list) dan akan menahan program sampai ada salah satu socket yang menerima data (baik itu koneksi baru ke server, maupun pesan dari klien).

Ketika ada aktivitas, program akan mengecek: apakah aktivitas tersebut berasal dari server (berarti ada klien baru mendaftar), atau dari socket klien lama (berarti klien tersebut mengirimkan file atau chat). Karena semuanya diproses dalam satu loop secara efisien, metode ini jauh lebih hemat sumber daya (resource) dibandingkan metode threading, terutama jika jumlah klien mulai bertambah.

3. Pendekatan Polling (server-poll.py)
   Pendekatan ketiga menggunakan system call poll() yang fungsinya serupa dengan select, namun didesain untuk menangani jumlah koneksi yang jauh lebih masif (skalabilitas tinggi).

```
def start_server():
    # ... [bind dan listen] ...
    
    # Setup Poll dengan penanganan kompatibilitas Sistem Operasi
    try:
        poller = select.poll()
    except AttributeError:
        print("[!] Error: Sistem operasi ini (kemungkinan Windows) tidak mendukung select.poll(). Gunakan Linux/macOS.")
        return

    poller.register(server, select.POLLIN)
    fd_to_socket = {server.fileno(): server}
    
    # ... [looping events = poller.poll() dan pemrosesan I/O] ...
```

Fungsi poll() lebih efisien dari select() karena tidak mengharuskan sistem operasi untuk memindai ulang seluruh daftar socket setiap kali ada kejadian baru. Metode ini langsung memetakan File Descriptor (FD) dari socket yang aktif.

Pada implementasi ini, disisipkan sebuah blok try-except AttributeError sebagai bentuk error handling. Hal ini dikarenakan fungsi select.poll() merupakan fitur native dari sistem operasi keluarga Unix/Linux dan tidak didukung oleh sistem operasi Windows. Saat program dijalankan di lingkungan Windows (seperti pada PowerShell), program akan menangkap error tersebut dan memberikan pesan peringatan yang elegan tanpa menyebabkan aplikasi crash secara mendadak. Hal ini menunjukkan pemahaman yang baik terkait lingkungan sistem operasi dalam pemrograman jaringan (Network Programming).



## Screenshot Hasil
