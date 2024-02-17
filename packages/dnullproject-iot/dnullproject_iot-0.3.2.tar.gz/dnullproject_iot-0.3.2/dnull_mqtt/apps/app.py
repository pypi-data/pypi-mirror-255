from dnull_mqtt.mqtt import MQTT
from dnull_mqtt.awtrix import Awtrix
from dnull_mqtt.base_log import log


class App:
    def __init__(self, name, Config) -> None:
        self.name = name
        self.config = Config
        self.mqtt = MQTT(self.config, self.name)
        self.awtrix = Awtrix(scrollSpeed=50)
        self.awtrix.icon("default")
        log.info(f"{self.name} inited")
