import logging
from dnull_mqtt.config import Config

config = Config()
logging.basicConfig(format="[%(asctime)s %(levelname)s]\t%(message)s")
log = logging.getLogger(__name__)
log.setLevel(config.log_level)
