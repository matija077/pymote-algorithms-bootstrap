import random
from pymote.sensor import Sensor

class TemperatureSensor(Sensor):

    """Provides node's random temperature."""

    def read(self, node):
        minTemp = -40
        maxTemp = 40
        temperature = random.randrange(minTemp, maxTemp)
        return {'Temperature': temperature}
