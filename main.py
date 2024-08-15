import pathlib

import schedule
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from src.statusicon import TodoistStatusIcon
from src.window import TodoistWindow
from src.api_dialog import APIKeyDialog

def run_schedule():
    schedule.run_pending()
    return True

def hide_window(window):
    window.hide()
    return True

def main(api_key: str):
    window = TodoistWindow(api_key)
    status_icon = TodoistStatusIcon()

    GLib.timeout_add(1000, run_schedule)
    window.connect("delete-event", lambda *_: hide_window(window)) # Keeps the schedule alive
    window.connect("destroy", lambda _: Gtk.main_quit()) # Actually ends
    status_icon.connect("quit_item", lambda _: Gtk.main_quit()) # Ends process but with tray icon

    schedule.every(10).seconds.do(window.on_schedule)
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    api_key_path = pathlib.Path(GLib.get_user_config_dir()) / ".todoist-dailies.env"
    if not api_key_path.exists():
        api_key_path.touch()

        api_dialog = APIKeyDialog(None)
        api_dialog_response = api_dialog.run()

        if api_dialog_response == Gtk.ResponseType.OK:
            api_key = api_dialog.get_input()
            api_key_path.write_text(f"API_KEY={api_key}")
            api_dialog.destroy()
            
            try:
                main(api_key)
            except Exception as e: # EAFP
                # TODO: MessageDialog for error
                api_key_path.unlink()
                raise e
    else:
        api_key = api_key_path.read_text().replace("API_KEY=", "")
        main(api_key)
