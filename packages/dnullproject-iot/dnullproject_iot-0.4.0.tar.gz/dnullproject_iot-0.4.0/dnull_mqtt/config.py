from os import environ


class Config:
    def __init__(self) -> None:
        self.log_level = environ.get("LOG_LEVEL", "INFO")
        # Binance
        self.binance_key = environ.get("BINANCE_KEY")
        self.binance_secret = environ.get("BINANCE_SECRET")
        self.binance_candlestick_inverval = "1h"
        self.binance_pairs = environ.get("BINANCE_PAIRS", "BTCUSDT,ETHUSDT")

        # MQTT
        self.mqtt_broker = environ.get("BROKER_HOST")
        self.mqtt_port = int(environ.get("BROKER_PORT", 1883))
        self.mqtt_interval = int(environ.get("MQTT_INTERVAL", 60))
        self.mqtt_username = environ.get("MQTT_USER")
        self.mqtt_password = environ.get("MQTT_PASSWORD")
        self.mtqq_prefix = environ.get("MQTT_PREFIX", "awtrix/custom")

        # FatSecret
        self.fatsecret_client_id = environ.get("FATSECRET_KEY")
        self.fatsecret_secret_key = environ.get("FATSECRET_SECRET")

        # Notion
        self.notion_database_id = environ.get("NOTION_PAGE")
        self.notion_token = environ.get("NOTION_TOKEN")
        self.notion_todo_statuses = environ.get(
            "NOTION_TODO_STATUSES", "Backlog,Ready,In progress"
        )
        self.notion_delete_prefixes = environ.get("NOTION_DELETE_PREFIXES", "")
        self.notion_database_filter = {
            "and": [
                {
                    "property": "Time",
                    "date": {
                        "this_week": {},
                    },
                },
                {
                    "property": "Name",
                    "rich_text": {
                        "does_not_contain": "Journal: ",
                    },
                },
            ],
        }
