from datetime import date

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from todoist_api_python.api import TodoistAPI

class TodoistElement(Gtk.ListBoxRow):
    def __init__(self, todoist_task, *args, **kwargs):
        self.todoist_task = todoist_task
        super().__init__(*args, **kwargs)

        self.set_selectable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        self.check_button = Gtk.CheckButton()
        label = Gtk.Label(label=todoist_task.content)
        hbox.add(self.check_button)
        hbox.add(label)
        self.add(hbox)

class TodoistWindow(Gtk.Window):
    def __init__(self, api_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(500, 250)
        self.api = TodoistAPI(api_key)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        box.props.margin_start = 24
        box.props.margin_end = 24
        box.props.margin_top = 24
        box.props.margin_bottom = 24
        self.add(box)

        # Header
        self.header_bar = Gtk.HeaderBar()
        self.update_date()
        self.set_titlebar(self.header_bar)

        self.listbox = Gtk.ListBox()
        self.listbox.props.selection_mode = Gtk.SelectionMode.NONE
        self.listbox.set_vexpand(True)
        box.add(self.listbox)

        # Get tasks and add them
        self.sync_tasks()

        # Bottom buttons
        self.close_button = Gtk.Button(label="Mark Done & Close")
        self.quit_button = Gtk.Button(label="Quit Process")

        self.close_button.connect('clicked', self.on_close_button)
        self.quit_button.connect('clicked', lambda _: self.destroy())

        buttons_hbox = Gtk.HBox(spacing=24)
        buttons_hbox.add(self.quit_button)
        buttons_hbox.add(self.close_button)
        box.add(buttons_hbox)

    def on_close_button(self, _):
        self.listbox.foreach(self.eee)
        self.sync_tasks()
        self.close()

    def eee(self, todoist_element: TodoistElement):
        if todoist_element.check_button.get_active():
            self.api.close_task(todoist_element.todoist_task.id)

    def update_date(self):
        formatted_date = date.today().strftime("%B %d, %Y")
        self.header_bar.props.title = f"Tasks for {formatted_date}"

    def on_schedule(self):
        self.show_all()
        self.update_date()

    def sync_tasks(self):
        self.listbox.foreach(lambda widget: self.listbox.remove(widget))

        try:
            tasks = self.api.get_tasks(filter="today|overdue")
            for task in tasks:
                print(task)
        except Exception as error:
            raise error
        else:
            if tasks is not None:
                for task in tasks:
                    task_element = TodoistElement(task)
                    self.listbox.add(task_element)
    

