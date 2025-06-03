from sensors.TemperatureSensor import TemperatureSensor
from sensors.HumiditySensor import HumiditySensor
from sensors.PressureSensor import PressureSensor
from sensors.LightSensor import LightSensor
from sensors.logger.logger import Logger
from network.client import NetworkClient
from network.config import load_client_config


def main():
    # Inicjalizacja loggera
    logger = Logger("config.json")
    logger.start()

    # Inicjalizacja czujników
    temp_sensor = TemperatureSensor(1, "Temp Room", "°C", -20, 50)
    humidity_sensor = HumiditySensor(2, "Humidity Room", "%", 0, 100)
    pressure_sensor = PressureSensor(3, "Pressure Outside", "hPa", 950, 1050)
    light_sensor = LightSensor(4, "Light Window", "lx", 0, 10000)

    sensors = [temp_sensor, humidity_sensor, pressure_sensor, light_sensor]

    # Wczytanie konfiguracji klienta
    client_config = load_client_config()

    # Dla każdego sensora – nowa sesja połączenia!
    for sensor in sensors:
        value = sensor.read_value()
        print(f"[LOCAL] {sensor.name}: {value} {sensor.unit}")

        data = {
            "sensor_id": sensor.sensor_id,
            "name": sensor.name,
            "value": value,
            "unit": sensor.unit
        }

        # 🔥 Nowe połączenie dla każdego odczytu!
        network_client = NetworkClient(
            host=client_config['host'],
            port=client_config['port'],
            timeout=client_config['timeout'],
            retries=client_config['retries']
        )
        network_client.connect()
        success = network_client.send(data)
        network_client.close()

        if not success:
            print(f"[ERROR] Nie udało się wysłać danych: {data}")

    # Zakończenie loggera
    logger.stop()


if __name__ == "__main__":
    main()
