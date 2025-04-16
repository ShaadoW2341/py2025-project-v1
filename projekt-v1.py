import random
import time

class Sensor:
    def __init__(self, sensor_id, name, unit, min_value, max_value, frequency=1):
        self.sensor_id = sensor_id
        self.name = name
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.frequency = frequency
        self.active = True
        self.last_value = None
        self.history = []

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        value = random.uniform(self.min_value, self.max_value)
        self.last_value = value
        self.history.append(value)
        return value

    def calibrate(self, calibration_factor):
        if self.last_value is None:
            self.read_value()

        self.last_value *= calibration_factor
        return self.last_value

    def get_last_value(self):
        if self.last_value is None:
            return self.read_value()
        return self.last_value

    def get_history(self, limit=10):
        return self.history[-limit:]

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def __str__(self):
        return f"Sensor(id={self.sensor_id}, name={self.name}, unit={self.unit})"

# --- Typy czujników ---

class TemperatureSensor(Sensor):
    def __init__(self, sensor_id, name="Temperature Sensor", min_value=-20, max_value=50, frequency=1):
        super().__init__(sensor_id, name, "°C", min_value, max_value, frequency)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        value = round(random.gauss((self.min_value + self.max_value) / 2, 2), 2)
        value = max(min(value, self.max_value), self.min_value)
        self.last_value = value
        self.history.append(value)
        return value

class HumiditySensor(Sensor):
    def __init__(self, sensor_id, name="Humidity Sensor", min_value=0, max_value=100, frequency=2):
        super().__init__(sensor_id, name, "%", min_value, max_value, frequency)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        value = round(random.uniform(30, 70), 1)
        self.last_value = value
        self.history.append(value)
        return value

class PressureSensor(Sensor):
    def __init__(self, sensor_id, name="Pressure Sensor", min_value=950, max_value=1050, frequency=3):
        super().__init__(sensor_id, name, "hPa", min_value, max_value, frequency)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        value = round(random.gauss(1013.25, 5), 2)
        value = max(min(value, self.max_value), self.min_value)
        self.last_value = value
        self.history.append(value)
        return value

class LightSensor(Sensor):
    def __init__(self, sensor_id, name="Light Sensor", min_value=0, max_value=10000, frequency=0.5):
        super().__init__(sensor_id, name, "lux", min_value, max_value, frequency)

    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")
        hour = time.localtime().tm_hour
        if 6 <= hour <= 18:
            value = random.uniform(3000, 10000)  # dzień
        else:
            value = random.uniform(0, 100)       # noc
        value = round(value, 2)
        self.last_value = value
        self.history.append(value)
        return value

# --- Testowanie ---

if __name__ == "__main__":
    sensors = [
        TemperatureSensor(1),
        HumiditySensor(2),
        PressureSensor(3),
        LightSensor(4)
    ]

    for sensor in sensors:
        print(f"\n{sensor}")
        for _ in range(3):
            print(f"Odczyt: {sensor.read_value()} {sensor.unit}")
        print(f"Historia: {sensor.get_history()}")
