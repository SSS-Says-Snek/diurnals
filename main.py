import schedule
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from src.statusicon import TodoistStatusIcon
from src.window import TodoistWindow

def run_schedule():
    schedule.run_pending()
    return True

def e(window):
    window.hide()
    return True

if __name__ == "__main__":
    window = TodoistWindow()
    status_icon = TodoistStatusIcon()

    GLib.timeout_add(1000, run_schedule)
    window.connect("delete-event", lambda *_: e(window)) # Keeps the schedule alive
    window.connect("destroy", lambda _: Gtk.main_quit()) # Actually ends
    window.show_all()

    schedule.every(2).seconds.do(lambda: window.show_all())
    Gtk.main()
