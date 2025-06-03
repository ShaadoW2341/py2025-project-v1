from sensors.base_sensor import Sensor
import random


class PressureSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        base = (self.min_value + self.max_value) / 2
        value = base + random.gauss(0, 1)

        value = max(self.min_value, min(self.max_value, value))
        self.last_value = round(value, 2)
        self.history.append(self.last_value)
        self._notify_callbacks(self.last_value)
        return self.last_value
