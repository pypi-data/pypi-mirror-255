from dnull_mqtt.config import Config
from dnull_mqtt.apps.binance import AppBinance
from dnull_mqtt.apps.budget import AppBudget

# from apps.nutrition import AppNutrition
from dnull_mqtt.apps.notion import AppNotion
import time
from dnull_mqtt.base_log import log



def run():
    config = Config()

    log.info("DNULL MQTT started...")
    log.debug("debug enabled")
    app_binance = AppBinance(config)
    # app_budget = AppBudget(config)
    # app_nutrition = AppNutrition(config)
    app_notion = AppNotion(config)

    while True:
        app_binance.run()
        # app_budget.run()
        app_notion.run()

        time.sleep(config.mqtt_interval)

if __name__ == "__main__":
    run()

