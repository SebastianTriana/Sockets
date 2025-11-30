import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import queue
import sys

HOST = "127.0.0.1"
PORT = 5000

class ChatClient:
    def __init__(self, master, host, port):
        self.master = master
        self.host = host
        self.port = port
        self.sock = None
        self.recv_thread = None
        self.running = False
        self.q = queue.Queue()

        self.master.title("Chat - Cliente")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # interfaz
        lbl_name = tk.Label(master, text="Tu nombre:")
        lbl_name.pack(anchor="w", padx=5)

        self.entry_name = tk.Entry(master)
        self.entry_name.pack(fill="x", padx=5)

        self.chat_area = scrolledtext.ScrolledText(master, state="disabled", height=20)
        self.chat_area.pack(fill="both", padx=5, pady=5, expand=True)

        frame = tk.Frame(master)
        frame.pack(fill="x", padx=5, pady=(0,5))

        self.entry_msg = tk.Entry(frame)
        self.entry_msg.pack(side="left", fill="x", expand=True)

        btn_send = tk.Button(frame, text="Enviar", command=self.send_message)
        btn_send.pack(side="right")

        # coneccion al servidor
        self.connect_dialog()

        # actualizar la interfaz periódicamente
        self.master.after(100, self.poll_queue)

    def connect_dialog(self):
        name = simpledialog.askstring("Nombre", "Introduce tu nombre:", parent=self.master)
        if not name:
            messagebox.showwarning("Nombre requerido", "Debes introducir un nombre para conectarte.")
            self.master.after(0, self.master.destroy)
            return
        self.name = name.strip()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar al servidor:\n{e}")
            self.master.after(0, self.master.destroy)
            return

        self.running = True
        self.recv_thread = threading.Thread(target=self.recv_loop, daemon=True)
        self.recv_thread.start()

        # notificacion cuando alguien se une
        join_msg = f"** {self.name} se ha unido al chat **"
        try:
            self.sock.sendall((join_msg + "\n").encode("utf-8"))
        except:
            pass

    def recv_loop(self):
        buffer = b""
        try:
            while self.running:
                data = self.sock.recv(4096)
                if not data:
                    # servidor cerró
                    self.q.put("** Conexión cerrada por el servidor **")
                    break
                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    msg = line.decode("utf-8", errors="replace")
                    # push al queue para que actualice la interfaz
                    self.q.put(msg)
        except Exception as e:
            self.q.put(f"** Error de red: {e} **")
        finally:
            self.running = False
            try:
                self.sock.close()
            except:
                pass

    def send_message(self):
        text = self.entry_msg.get().strip()
        if not text or not self.running:
            return
        full = f"{self.name}: {text}"
        try:
            self.sock.sendall((full + "\n").encode("utf-8"))
            self.entry_msg.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el mensaje: {e}")
            self.on_close()

    def poll_queue(self):
        while not self.q.empty():
            msg = self.q.get_nowait()
            self.append_chat(msg)
        if self.running:
            self.master.after(100, self.poll_queue)
        else:
            # si ya no estamos corriendo, deshabilitar entrada
            self.entry_msg.config(state="disabled")

    def append_chat(self, msg):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, msg + "\n")
        self.chat_area.see(tk.END)
        self.chat_area.config(state="disabled")

    def on_close(self):
        # intentar notificar salida
        try:
            if self.sock and self.running:
                leave_msg = f"** {self.name} ha abandonado el chat **\n"
                self.sock.sendall(leave_msg.encode("utf-8"))
        except:
            pass
        self.running = False
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
        except:
            pass
        self.master.destroy()

def main():
    root = tk.Tk()
    app = ChatClient(root, HOST, PORT)
    root.mainloop()

if __name__ == "__main__":
    main()
