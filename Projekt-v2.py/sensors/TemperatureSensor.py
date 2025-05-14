from sensors.base_sensor import Sensor
import math
import random
from datetime import datetime


class TemperatureSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = datetime.now().hour
        base_temp = (self.max_value + self.min_value) / 2
        amplitude = (self.max_value - self.min_value) / 2

        temp = base_temp + amplitude * math.sin((2 * math.pi / 24) * hour)
        temp += random.uniform(-1, 1)

        self.last_value = round(temp, 2)
        self.history.append(self.last_value)
        self._notify_callbacks(self.last_value)
        return self.last_value
