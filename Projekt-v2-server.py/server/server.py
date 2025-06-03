import socket
import json
import sys
import yaml


class NetworkServer:
    def __init__(self, port: int):
        self.port = port

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', self.port))
            s.listen()
            print(f"[INFO] Serwer nasłuchuje na porcie {self.port}...")

            while True:
                client_sock, addr = s.accept()
                print(f"[INFO] Połączenie od {addr}")
                self._handle_client(client_sock)

    def _handle_client(self, client_socket) -> None:
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
                print("[INFO] Odebrano dane:")
                for k, v in data.items():
                    print(f"  {k}: {v}")

                client_socket.sendall(b"ACK\n")
            except json.JSONDecodeError as e:
                print(f"[ERROR] Błąd parsowania JSON: {e}", file=sys.stderr)
            except Exception as e:
                print(f"[ERROR] Błąd obsługi klienta: {e}", file=sys.stderr)


if __name__ == "__main__":
    with open("config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    port = config['server']['port']

    server = NetworkServer(port)
    server.start()
