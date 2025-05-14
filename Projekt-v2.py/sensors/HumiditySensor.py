from sensors.base_sensor import Sensor
import random


class HumiditySensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        base = random.uniform(self.min_value, self.max_value)
        fluctuation = random.uniform(-5, 5)
        value = max(self.min_value, min(self.max_value, base + fluctuation))

        self.last_value = round(value, 2)
        self.history.append(self.last_value)
        self._notify_callbacks(self.last_value)
        return self.last_value
