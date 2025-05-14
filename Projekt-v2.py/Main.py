from sensors.TemperatureSensor import TemperatureSensor
from sensors.HumiditySensor import HumiditySensor
from sensors.PressureSensor import PressureSensor
from sensors.LightSensor import LightSensor
from sensors.logger.logger import Logger


def main():
    logger = Logger("config.json")
    logger.start()

    temp_sensor = TemperatureSensor(1, "Temp Room", "°C", -20, 50)
    humidity_sensor = HumiditySensor(2, "Humidity Room", "%", 0, 100)
    pressure_sensor = PressureSensor(3, "Pressure Outside", "hPa", 950, 1050)
    light_sensor = LightSensor(4, "Light Window", "lx", 0, 10000)

    sensors = [temp_sensor, humidity_sensor, pressure_sensor, light_sensor]

    for sensor in sensors:
        sensor.register_callback(logger.log_reading)

    print("Symulacja odczytów:")
    for _ in range(5):
        for sensor in sensors:
            value = sensor.read_value()
            print(f"{sensor.name}: {value} {sensor.unit}")

    logger.stop()


if __name__ == "__main__":
    main()
