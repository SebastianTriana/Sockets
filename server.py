
import socket
import threading

HOST = "127.0.0.1"  # localhost
PORT = 5000

clients = []        # lista de (conn, addr)
clients_lock = threading.Lock()

def broadcast(message, origen_conn=None):
    """Enviar message (bytes) a todos los clientes excepto origen_conn."""
    with clients_lock:
        for conn, _ in list(clients):
            if conn is origen_conn:
                continue
            try:
                conn.sendall(message)
            except Exception:
                try:
                    conn.close()
                except:
                    pass
                clients.remove((conn, _))

def handle_client(conn, addr):
    print(f"[+] Conexión desde {addr}")
    buffer = b""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buffer += data
            # separar mensajes por nueva línea
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                msg = line.strip()
                if msg:
                    print(f"[{addr}] {msg.decode(errors='replace')}")
                    broadcast(msg + b"\n", origen_conn=conn)
    except Exception as e:
        print(f"[!] Error con {addr}: {e}")
    finally:
        print(f"[-] Desconectado {addr}")
        with clients_lock:
            try:
                clients.remove((conn, addr))
            except ValueError:
                pass
        try:
            conn.close()
        except:
            pass

def accept_loop(server_sock):
    while True:
        conn, addr = server_sock.accept()
        with clients_lock:
            clients.append((conn, addr))
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()

def main():
    print("[*] Iniciando servidor papacho...")
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"[*] Escuchando en {HOST}:{PORT}")
    try:
        accept_loop(server_sock)
    except KeyboardInterrupt:
        print("\n[*] Cerrando servidor...")
    finally:
        with clients_lock:
            for conn, _ in clients:
                try:
                    conn.close()
                except:
                    pass
        server_sock.close()

if __name__ == "__main__":
    main()
