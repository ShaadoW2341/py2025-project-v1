from server.server import NetworkServer
import yaml


def main():
    # Wczytanie konfiguracji serwera z config.yaml
    with open("config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    port = config['server']['port']

    # Uruchomienie serwera
    server = NetworkServer(port)
    server.start()


if __name__ == "__main__":
    main()
