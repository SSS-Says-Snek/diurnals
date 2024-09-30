import gi
import schedule

from src.welcome_carousel import WelcomeCarousel

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, GLib, Gio, Gtk

from src.constants import API_KEY_PATH, APPLICATION_ID
from src.window import TodoistWindow

class Diurnals(Adw.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.settings = Gio.Settings(schema_id=APPLICATION_ID)

    def do_activate(self):
        # Calls welcome window when no API key, otherwise skips
        if not API_KEY_PATH.exists():
            welcome_window = WelcomeCarousel(self, self.on_finish_welcome)
            welcome_window.present()
        else:
            api_key = API_KEY_PATH.read_text().replace("API_KEY=", "")
            self.main(api_key)

    def main(self, api_key: str):
        window = TodoistWindow(api_key, application=self)

        GLib.timeout_add(1000, self.run_schedule)
        window.connect("destroy", lambda _: self.quit())  # Actually ends

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource("/io/github/sss_says_snek/diurnals/style.css")
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        for routine in self.settings.get_value("routines").unpack():
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

    def on_finish_welcome(self, api_key: str):
        API_KEY_PATH.write_text(f"API_KEY={api_key}")
        self.main(api_key)

    @staticmethod
    def run_schedule():
        schedule.run_pending()
        return True


def main():
    app = Diurnals(application_id=APPLICATION_ID)

    app.run(None)


if __name__ == "__main__":
    main()
