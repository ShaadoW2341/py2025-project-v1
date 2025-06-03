import tkinter as tk
from tkinter import ttk, messagebox
import threading
import socket
import json
import datetime
import sys
import queue
import yaml


class NetworkServer:
    def __init__(self, port, on_new_reading):
        self.port = port
        self.on_new_reading = on_new_reading
        self.running = False

    def start(self):
        self.running = True
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.port))
            s.listen()
            while self.running:
                try:
                    client_sock, addr = s.accept()
                    self._handle_client(client_sock)
                except Exception as e:
                    print(f"[ERROR] {e}", file=sys.stderr)

    def stop(self):
        self.running = False

    def _handle_client(self, client_socket):
        with client_socket:
            try:
                raw = b''
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    raw += chunk
                    if b'\n' in chunk:
                        break
                message = raw.strip().decode('utf-8')
                data = json.loads(message)
                data['timestamp'] = datetime.datetime.now()
                self.on_new_reading(data)
                client_socket.sendall(b"ACK\n")
            except Exception as e:
                print(f"[ERROR] Błąd: {e}", file=sys.stderr)


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Server GUI")

        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(top_frame, text="Port:").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(top_frame, width=6)
        self.port_entry.insert(0, "9999")
        self.port_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(top_frame, text="Start", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(top_frame, text="Stop", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        columns = ("sensor", "value", "unit", "timestamp", "avg_1h", "avg_12h")
        self.tree = ttk.Treeview(root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status = tk.StringVar(value="Zatrzymany")
        status_bar = tk.Label(root, textvariable=self.status, anchor='w')
        status_bar.pack(fill=tk.X, padx=5, pady=2)

        self.readings = {}
        self.update_queue = queue.Queue()

        self.root.after(2000, self.update_table)

    def start_server(self):
        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowy port!")
            return

        self.server = NetworkServer(port, self.on_new_reading)
        self.server_thread = threading.Thread(target=self.server.start, daemon=True)
        self.server_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status.set(f"Nasłuchiwanie na porcie {port}...")

    def stop_server(self):
        if hasattr(self, 'server'):
            self.server.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status.set("Zatrzymany")

    def on_new_reading(self, data):
        sensor_id = data["sensor_id"]
        if sensor_id not in self.readings:
            self.readings[sensor_id] = []
        self.readings[sensor_id].append(data)
        self.update_queue.put(sensor_id)

    def update_table(self):
        while not self.update_queue.empty():
            sensor_id = self.update_queue.get()
            latest = self.readings[sensor_id][-1]
            avg_1h = self.calculate_avg(sensor_id, 1)
            avg_12h = self.calculate_avg(sensor_id, 12)

            values = (
                latest["name"],
                latest["value"],
                latest["unit"],
                latest["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                round(avg_1h, 2),
                round(avg_12h, 2)
            )

            if self.tree.exists(sensor_id):
                self.tree.item(sensor_id, values=values)
            else:
                self.tree.insert('', 'end', iid=sensor_id, values=values)

        self.root.after(2000, self.update_table)

    def calculate_avg(self, sensor_id, hours):
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(hours=hours)
        values = [r["value"] for r in self.readings[sensor_id] if r["timestamp"] >= cutoff]
        if values:
            return sum(values) / len(values)
        else:
            return 0.0


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
