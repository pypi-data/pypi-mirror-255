# Lib: https://github.com/ramnes/notion-sdk-py
# Examples of usage: https://github.com/kris-hansen/notion-cli/blob/main/notioncli/cli.py#L26
# Database filters: https://developers.notion.com/reference/post-database-query-filter

from dnull_mqtt.apps.app import App
from notion_client import Client
from dnull_mqtt.config import Config
from datetime import datetime, timedelta
import httpx

from dnull_mqtt.base_log import log


class AppNotion(App):
    def __init__(self, Config: Config) -> None:
        self.name = "notion"
        super().__init__(self.name, Config)
        self.awtrix.settings["textCase"] = 1
        self.awtrix.settings["duration"] = 0
        self.awtrix.settings["icon"] = self.awtrix.icons.get(self.name)
        self.notion = Client(auth=self.config.notion_token)

    def _get_todays_todo(self):
        current_datetime_utc2 = datetime.utcnow() + timedelta(hours=2)
        today = current_datetime_utc2.date()

        database = self.notion.databases.query(
            **{
                "database_id": self.config.notion_database_id,
                "filter": self.config.notion_database_filter,
                "sorts": [{"property": "Time", "direction": "ascending"}],
            }
        )
        # Time:
        # '.results[0].properties.Time.date.start'
        # Status:
        # '.results[0].properties.Status.status.name'

        todays_todo = list()
        if not database["results"]:
            log.info("No TODOs")
        else:
            for item in database["results"]:
                try:
                    name = item["properties"]["Name"]["title"][0]["plain_text"]
                    status = item["properties"]["Status"]["status"]["name"]
                    time = datetime.fromisoformat(
                        item["properties"]["Time"]["date"]["start"]
                    ).date()

                    if time == today:
                        todays_todo.append(
                            {"name": name, "time": time, "status": status}
                        )
                except KeyError as e:
                    log.error(f"Error parsing Notion response: {e}")
                    log.error(item)
                    continue

        log.info(todays_todo)
        return todays_todo

    def _set_scroll_speed(self, text: str):
        # TODO: use formula instead of hardcode
        symbols = len(text)
        if symbols <= 15:
            self.awtrix.settings["scrollSpeed"] = 50
        elif symbols > 15 and symbols <= 25:
            self.awtrix.settings["scrollSpeed"] = 75
        else:
            self.awtrix.settings["scrollSpeed"] = 100

    def _set_icon(self, todo_tasks_no, all_tasks_no):
        if todo_tasks_no == 0 or all_tasks_no == 0:
            self.awtrix.icon("green_checkmark")
        else:
            icon_no = str(todo_tasks_no) + str(all_tasks_no)
            self.awtrix.icon(icon_no)

    def _format_tasks(self, tasks):
        task_names = str()
        todo_tasks_no = 0
        all_tasks_no = len(tasks)
        if all_tasks_no == 0:
            message = "--Middle grey::No tasks--"
        else:
            todo_statuses = self.config.notion_todo_statuses.split(",")
            todo = list()
            for task in tasks:
                if task["status"] in todo_statuses:

                    if self.config.notion_delete_prefixes:
                        for prefix in self.config.notion_delete_prefixes.split(','):
                            task["name"] = task["name"].replace(f"{prefix} ", "")
                    todo.append(task["name"])
            todo_tasks_no = len(todo)
            if todo_tasks_no == 0:
                message = f"--Green::{all_tasks_no} completed--"
            else:
                task_names = ", ".join(todo)
                message = f"--White::{task_names}--"

        self._set_icon(todo_tasks_no, all_tasks_no)
        self._set_scroll_speed(task_names)
        return self.awtrix.message(message)

    def run(self):
        try:
            tasks = self._get_todays_todo()
        except httpx.HTTPStatusError as e:
            log.error(f"Issue with Notion API: {e}")
            self.awtrix.icon("error")
            self.mqtt.publish(self.awtrix.message("--Red::connection error--"))
        else:
            self.mqtt.publish(self._format_tasks(tasks))


class TestAppNotion(AppNotion):
    def __init__(self, Config: Config) -> None:
        super().__init__(Config)
        self.name = "test_notion"
        self.awtrix.settings["textCase"] = 1
        self.awtrix.settings["duration"] = 0
        self.awtrix.settings["icon"] = self.awtrix.icons.get(self.name)

    def test(self, tasks):
        print(self._format_tasks(tasks))
        return str(self._format_tasks(tasks))
