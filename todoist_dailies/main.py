#!/usr/bin/python3
import pathlib
from configparser import ConfigParser

import gi
import schedule

from todoist_dailies.constants import API_KEY_PATH, APPLICATION_ID, CONFIG_PATH

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib

from todoist_dailies.api_dialog import APIKeyDialog
from todoist_dailies.window import TodoistWindow


def run_schedule():
    schedule.run_pending()
    return True


def hide_window(window):
    window.hide()
    return True


def inner_main(app: Adw.Application, api_key: str, config: ConfigParser):
    window = TodoistWindow(api_key, config=config, application=app)

    GLib.timeout_add(1000, run_schedule)
    window.connect("destroy", lambda _: app.quit())  # Actually ends

    for routine in config["Routine"].values():
        day, time = routine.split()

        schedule_days_dict = {
            "day": schedule.every().day,
            "Monday": schedule.every().monday,
            "Tuesday": schedule.every().tuesday,
            "Wednesday": schedule.every().wednesday,
            "Thursday": schedule.every().thursday,
            "Friday": schedule.every().friday,
            "Saturday": schedule.every().saturday,
            "Sunday": schedule.every().sunday
        }
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        weekends = ["Saturday", "Sunday"]
        if day == "weekday":
            for d in weekdays:
                schedule_days_dict[d].at(time).do(window.on_schedule)
        elif day == "weekend_day":
            for d in weekends:
                schedule_days_dict[d].at(time).do(window.on_schedule)
        else:
            schedule_days_dict[day].at(time).do(window.on_schedule)

    window.present()


def main(app: Adw.Application):

    if not CONFIG_PATH.exists():
        config = ConfigParser()
        config["Routine"] = {}
        with open(CONFIG_PATH, "w") as w:
            config.write(w)
    else:
        config = ConfigParser()
        config.read(CONFIG_PATH)

    if not API_KEY_PATH.exists():
        API_KEY_PATH.touch()

        api_dialog = APIKeyDialog(app, lambda api_key: api_dialog_ok(app, API_KEY_PATH, api_key, config))
        api_dialog.present()
    else:
        api_key = API_KEY_PATH.read_text().replace("API_KEY=", "")
        inner_main(app, api_key, config)


def api_dialog_ok(app: Adw.Application, api_key_path: pathlib.Path, api_key: str, config: ConfigParser):
    api_key_path.write_text(f"API_KEY={api_key}")
    inner_main(app, api_key, config)


def real_main():
    app = Adw.Application(application_id=APPLICATION_ID)
    app.connect("activate", main)

    app.run(None)


if __name__ == "__main__":
    real_main()
