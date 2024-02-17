from dnull_mqtt.apps.app import App
from binance.spot import Spot
from binance.error import ClientError
from dnull_mqtt.config import Config
from dnull_mqtt.base_log import log


class AppBinance(App):
    def __init__(self, Config: Config) -> None:
        self.name = "binance"
        super().__init__(self.name, Config)
        self.client = Spot()
        self.awtrix.icon(self.name)
        self.awtrix.settings["pushIcon"] = 1

    def get_price(self, pair: str):
        price = int(str(self.client.avg_price(pair)["price"]).split(".")[0])
        return f"{price:_}"

    def get_diff(self, pair: str):
        data = self.client.klines(pair, self.config.binance_candlestick_inverval)[-1]
        return round(float(data[1]) - float(data[4]), 2)

    def run(self):
        pairs = [x.strip() for x in self.config.binance_pairs.split(',')]
        messages = list()
        for pair in pairs:
            try:
                price = self.get_price(pair)
                diff = self.get_diff(pair)
            except ClientError as e:
                log.error(f"Binance - Error getting price for {pair}, possible typo")
                log.error(e)
                continue
            if diff < 0:
                diff = f"--Red::({diff})--"
            elif diff == 0:
                diff = f"--White::({diff})--"
            else:
                diff = f"--Green::({diff})--"

            message = f"--White::{price}--{diff}"
            self.awtrix.icon(pair)
            messages.append(self.awtrix.message(message).copy())

            log.debug(f"binance: {pair} - {message}")
        log.debug(f"binance: {messages}")
        self.mqtt.publish(messages)
