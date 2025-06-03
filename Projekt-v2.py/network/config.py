import yaml


def load_client_config(config_path="config.yaml") -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config['client']
