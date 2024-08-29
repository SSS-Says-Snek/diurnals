from configparser import ConfigParser
import pathlib

import schedule
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GLib, Adw

from src.window import TodoistWindow
from src.api_dialog import APIKeyDialog

APPLICATION_ID = "com.bmcomis2018.todoist-dailies"
CONFIG_PATH = pathlib.Path(GLib.get_user_config_dir()) / "todoist-dailies.conf"

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
    api_key_path = pathlib.Path(GLib.get_user_config_dir()) / ".todoist-dailies.env"

    if not CONFIG_PATH.exists():
        config = ConfigParser()
        config["Routine"] = {}
        with open(CONFIG_PATH, "w") as w:
            config.write(w)
    else:
        config = ConfigParser()
        config.read(CONFIG_PATH)

    if not api_key_path.exists():
        api_key_path.touch()

        api_dialog = APIKeyDialog(app, lambda api_key: api_dialog_ok(app, api_key_path, api_key, config))
        api_dialog.present()
    else:
        api_key = api_key_path.read_text().replace("API_KEY=", "")
        inner_main(app, api_key, config)


def api_dialog_ok(app: Adw.Application, api_key_path: pathlib.Path, api_key: str, config: ConfigParser):
    api_key_path.write_text(f"API_KEY={api_key}")
    inner_main(app, api_key, config)


if __name__ == "__main__":
    app = Adw.Application(application_id=APPLICATION_ID)
    app.connect("activate", main)

    app.run(None)
