from collections.abc import Callable
from datetime import date

from src.todoist_worker import TodoistWorker
from src.config_window import ConfigWindow

from gi.repository import Gtk, Adw
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

class TodoistElement(Gtk.ListBoxRow):
    def __init__(self, todoist_task: Task, callback: Callable[[Gtk.CheckButton, "TodoistElement"], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.todoist_task = todoist_task

        self.set_selectable(False)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        self.check_button = Gtk.CheckButton()
        self.check_button.connect("toggled", lambda button: callback(button, self))

        label = Gtk.Label(label=todoist_task.content)
        hbox.append(self.check_button)
        hbox.append(label)
        self.set_child(hbox)


class TodoistWindow(Adw.ApplicationWindow):
    def __init__(self, api_key: str, application: Adw.Application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = application
        self.set_application(self.app)

        self.set_default_size(1000, 800)
        self.set_hide_on_close(True)

        self.api = TodoistAPI(api_key)
        self.todoist_worker = TodoistWorker(self.api) # Concurrent

        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        box.props.margin_start = 24
        box.props.margin_end = 24
        box.props.margin_top = 24
        box.props.margin_bottom = 24

        # Header
        self.header_bar = Adw.HeaderBar()
        self.header_bar.add_css_class("flat")
        self.update_date()
        outer_box.append(self.header_bar)
        outer_box.append(box)
        self.set_content(outer_box)

        config_button = Gtk.Button.new_from_icon_name("open-menu-symbolic")
        config_button.connect("clicked", self.open_config)
        self.header_bar.pack_end(config_button)

        self.listbox = Gtk.ListBox()
        self.listbox.props.selection_mode = Gtk.SelectionMode.NONE
        self.listbox.set_vexpand(True)
        box.append(self.listbox)

        # Get tasks and add them
        self.sync_tasks()

        # Bottom buttons
        self.close_button = Gtk.Button(label="Mark Done & Close")
        self.quit_button = Gtk.Button(label="Quit Process")

        self.close_button.connect('clicked', self.on_close_button)
        self.quit_button.connect('clicked', lambda _: self.destroy())

        buttons_hbox = Gtk.Box(spacing=24, halign=Gtk.Align.END)
        buttons_hbox.append(self.quit_button)
        buttons_hbox.append(self.close_button)
        box.append(buttons_hbox)

        self.widgets_to_remove: list[TodoistElement] = []

    def open_config(self, _):
        config_window = ConfigWindow()
        config_window.present(self)

    def toggle_complete_task(self, button: Gtk.CheckButton, child: TodoistElement):
        if button.get_active():
            self.widgets_to_remove.append(child)
        else:
            self.widgets_to_remove.remove(child)

    def complete_selected_tasks(self, todoist_element: TodoistElement, task_ids: list[str]):
        if todoist_element.check_button.get_active():
            task_ids.append(todoist_element.todoist_task.id)

    def update_date(self):
        formatted_date = date.today().strftime("%B %d, %Y")
        self.set_title(f"Tasks for {formatted_date}")

    def sync_tasks(self):
        self.todoist_worker.get_tasks_async(self.on_get_tasks_finished)

    ### CALLBACKS AND LISTENERS

    def on_schedule(self):
        """Activate according to schedule set"""
        self.sync_tasks()
        self.update_date()

        self.show()

    def on_close_button(self, _):
        task_ids: list[str] = []
        for widget_to_remove in self.widgets_to_remove:
            task_ids.append(widget_to_remove.todoist_task.id)
            self.listbox.remove(widget_to_remove)
        self.widgets_to_remove.clear()
        self.todoist_worker.complete_tasks_async(task_ids, error_callback=self.on_complete_tasks_failed)

        self.close()

    def on_get_tasks_finished(self, worker: TodoistWorker, result, _):
        tasks = worker.extract_value(result)
        if tasks != -1 and not None:
            self.listbox.remove_all()

            for task in tasks:
                task_element = TodoistElement(task, self.toggle_complete_task)
                self.listbox.append(task_element)
        else: # get_tasks Error
            self.on_get_tasks_failed()
        self.listbox.show()

    def on_get_tasks_failed(self):
        self._error_dialog("Todoist Dailies - Network Error", "Could not retrieve tasks!")

    def on_complete_tasks_failed(self):
        self._error_dialog("Todoist Dailies - Network Error", "Could not complete tasks!")
    
    def _error_dialog(self, title: str, secondary_text: str):
        error_dialog = Adw.AlertDialog(heading=title, body=secondary_text)
        error_dialog.add_response("ok", "Okay")
        error_dialog.present(self)

