import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk
from todoist_api_python.api import TodoistAPI

class TodoistElement(Gtk.ListBoxRow):
    def __init__(self, todoist_task, *args, **kwargs):
        self.todoist_task = todoist_task
        super().__init__(*args, **kwargs)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        check_button = Gtk.CheckButton()
        label = Gtk.Label(label=todoist_task.content)
        hbox.add(check_button)
        hbox.add(label)
        self.add(hbox)

class TodoistWindow(Gtk.Window):
    def __init__(self, api_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GLib.set_application_name('Todoist Dailies')

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        box.props.margin_start = 24
        box.props.margin_end = 24
        box.props.margin_top = 24
        box.props.margin_bottom = 24
        self.add(box)

        header_bar = Gtk.HeaderBar()
        header_bar.props.title = "Todoist Dailies for August 6th, 2024"
        self.set_titlebar(header_bar)

        listbox = Gtk.ListBox()
        listbox.props.selection_mode = Gtk.SelectionMode.NONE
        listbox.set_vexpand(True)
        box.add(listbox)

        tasks = self.get_tasks_sync(api_key)
        if tasks is not None:
            for task in tasks:
                listbox.add(TodoistElement(task))

        self.close_button = Gtk.Button(label="Close")
        self.quit_button = Gtk.Button(label="Quit Process")

        self.close_button.connect('clicked', lambda _: self.close())
        self.quit_button.connect('clicked', lambda _: self.destroy())

        buttons_hbox = Gtk.HBox(spacing=24)

        buttons_hbox.add(self.quit_button)
        buttons_hbox.add(self.close_button)
        box.add(buttons_hbox)

    @staticmethod
    def get_tasks_sync(api_key: str):
        api = TodoistAPI(api_key)
        try:
            tasks = api.get_tasks(filter="today|overdue")
            for task in tasks:
                print(task)
        except Exception as error:
            raise error
        else:
            return tasks

