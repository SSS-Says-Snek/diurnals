import pathlib

import schedule
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GLib, Adw

from src.window import TodoistWindow
from src.api_dialog import APIKeyDialog

APPLICATION_ID = "com.bmcomis2018.todoist-dailies"

def run_schedule():
    schedule.run_pending()
    return True

def hide_window(window):
    window.hide()
    return True

def inner_main(app: Adw.Application, api_key: str):
    window = TodoistWindow(api_key, application=app)

    GLib.timeout_add(1000, run_schedule)
    # window.connect("delete-event", lambda *_: hide_window(window)) # Keeps the schedule alive
    window.connect("destroy", lambda _: app.quit()) # Actually ends

    schedule.every(10).seconds.do(window.on_schedule)
    window.present()


def main(app: Adw.Application):
    api_key_path = pathlib.Path(GLib.get_user_config_dir()) / ".todoist-dailies.env"
    if not api_key_path.exists():
        api_key_path.touch()

        api_dialog = APIKeyDialog(app, lambda api_key: api_dialog_ok(app, api_key_path, api_key))
        api_dialog.present()
    else:
        api_key = api_key_path.read_text().replace("API_KEY=", "")
        inner_main(app, api_key)


def api_dialog_ok(app: Adw.Application, api_key_path: pathlib.Path, api_key: str):
    api_key_path.write_text(f"API_KEY={api_key}")
    inner_main(app, api_key)

if __name__ == "__main__":
    app = Adw.Application(application_id=APPLICATION_ID)
    app.connect('activate', main)

    app.run(None)

