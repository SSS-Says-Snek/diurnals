from configparser import ConfigParser
from pathlib import Path

import gi
import schedule

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, GLib, Gtk

from src.api_dialog import APIKeyDialog
from src.constants import API_KEY_PATH, APPLICATION_ID, CONFIG_PATH
from src.window import TodoistWindow


class TodoistDailies(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = ConfigParser()

    def do_activate(self):
        # Creates new config file if doesn't exist, otherwise just read from it
        if not CONFIG_PATH.exists():
            self.config["Routine"] = {}
            self.config["General"] = {"filter": "today|overdue"}
            with open(CONFIG_PATH, "w") as w:
                self.config.write(w)
        else:
            self.config.read(CONFIG_PATH)

        # Creates new API token file if doesn't exist, other just read from it
        if not API_KEY_PATH.exists():
            API_KEY_PATH.touch()

            api_dialog = APIKeyDialog(self, self.api_dialog_ok)
            api_dialog.present()
        else:
            api_key = API_KEY_PATH.read_text().replace("API_KEY=", "")
            self.main(api_key, self.config)

    def main(self, api_key: str, config: ConfigParser):
        window = TodoistWindow(api_key, config=config, application=self)

        GLib.timeout_add(1000, self.run_schedule)
        window.connect("destroy", lambda _: self.quit())  # Actually ends

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(str(Path(__file__).parent / "style.css"))
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

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
                "Sunday": schedule.every().sunday,
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

    def api_dialog_ok(self, api_key: str):
        API_KEY_PATH.write_text(f"API_KEY={api_key}")
        self.main(api_key, self.config)

    @staticmethod
    def run_schedule():
        schedule.run_pending()
        return True


def main():
    app = TodoistDailies(application_id=APPLICATION_ID)

    app.run(None)


if __name__ == "__main__":
    main()
