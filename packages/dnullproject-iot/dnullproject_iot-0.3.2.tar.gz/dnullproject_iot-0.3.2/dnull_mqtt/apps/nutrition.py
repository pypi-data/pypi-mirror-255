from dnull_mqtt.apps.app import App
from fatsecret import Fatsecret
from dnull_mqtt.config import Config


class AppNutrition(App):
    def __init__(self, Config: Config) -> None:
        self.name = "nutrition"
        super().__init__(self.name, Config)

    def example(self):
        fs = Fatsecret(
            self.config.fatsecret_secret_key, self.config.fatsecret_client_id
        )
        auth_url = fs.get_authorize_url()

        print(
            f"Browse to the following URL in your browser to authorize access:\n{auth_url}"
        )

        pin = input("Enter the PIN provided by FatSecret: ")
        session_token = fs.authenticate(pin)

        foods = fs.foods_get_most_eaten()
        print("Most Eaten Food Results: {}".format(len(foods)))
