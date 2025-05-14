from sensors.base_sensor import Sensor
import random
from datetime import datetime


class LightSensor(Sensor):
    def read_value(self):
        if not self.active:
            raise Exception(f"Czujnik {self.name} jest wyłączony.")

        hour = datetime.now().hour

        if 6 <= hour <= 18:
            if hour <= 12:
                brightness = (hour - 6) / 6
            else:
                brightness = (18 - hour) / 6
            base = brightness * self.max_value
        else:
            base = self.min_value

        value = base + random.uniform(-100, 100)
        value = max(self.min_value, min(self.max_value, value))

        self.last_value = round(value, 2)
        self.history.append(self.last_value)
        self._notify_callbacks(self.last_value)
        return self.last_value
