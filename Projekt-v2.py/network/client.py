import socket
import json
from network.config import load_client_config


class NetworkClient:
    def __init__(self, host: str, port: int, timeout: float = 5.0, retries: int = 3):
        """
        Inicjalizuje klienta sieciowego.
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.sock = None

    def connect(self) -> None:
        """
        Nawiązuje połączenie z serwerem.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))
        print(f"[INFO] Połączono z {self.host}:{self.port}")

    def send(self, data: dict) -> bool:
        """
        Wysyła dane w formacie JSON i czeka na potwierdzenie ACK.
        """
        payload = self._serialize(data)
        attempts = 0

        while attempts < self.retries:
            try:
                self.sock.sendall(payload + b'\n')
                ack = self.sock.recv(1024).decode('utf-8').strip()
                if ack == "ACK":
                    print(f"[INFO] Potwierdzenie ACK odebrane.")
                    return True
                else:
                    print(f"[ERROR] Otrzymano niepoprawne potwierdzenie: {ack}")
            except (socket.timeout, socket.error) as e:
                print(f"[ERROR] Błąd sieci: {e}")
            attempts += 1
            print(f"[INFO] Ponawianie próby ({attempts}/{self.retries})...")

        return False

    def close(self) -> None:
        """
        Zamyka połączenie.
        """
        if self.sock:
            self.sock.close()
            print("[INFO] Połączenie zamknięte.")

    def _serialize(self, data: dict) -> bytes:
        """
        Serializuje słownik do formatu JSON i koduje do bajtów.
        """
        return json.dumps(data).encode('utf-8')

    def _deserialize(self, raw: bytes) -> dict:
        """
        Deserializuje bajty do słownika JSON.
        """
        return json.loads(raw.decode('utf-8'))
