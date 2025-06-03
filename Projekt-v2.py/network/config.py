import yaml


def load_client_config(config_path="config.yaml") -> dict:
    """
    Wczytuje ustawienia klienta z pliku YAML.
    :param config_path: Ścieżka do pliku konfiguracyjnego
    :return: słownik z konfiguracją klienta
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['client']
