from datetime import date

import gi

from src.todoist_worker import TodoistWorker

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

class TodoistElement(Gtk.ListBoxRow):
    def __init__(self, todoist_task: Task, *args, **kwargs):
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
        self.todoist_worker = TodoistWorker(self.api) # Kind of async

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

        config_button = Gtk.Button.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON)
        self.header_bar.pack_end(config_button)

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

    def complete_selected_tasks(self, todoist_element: TodoistElement, task_ids: list[str]):
        if todoist_element.check_button.get_active():
            task_ids.append(todoist_element.todoist_task.id)

    def update_date(self):
        formatted_date = date.today().strftime("%B %d, %Y")
        self.header_bar.props.title = f"Tasks for {formatted_date}"

    def sync_tasks(self):
        self.todoist_worker.get_tasks_async(self.on_get_tasks_finished)

    ### CALLBACKS AND LISTENERS

    def on_schedule(self):
        self.sync_tasks()
        self.update_date()

        self.show_all()

    def on_close_button(self, _):
        task_ids: list[str] = []
        self.listbox.foreach(lambda e: self.complete_selected_tasks(e, task_ids)) # Adds appropriate task ids to list. MF WHERE IS THE GET_ALL_ROWS AT
        self.todoist_worker.complete_tasks_async(task_ids, error_callback=self.on_complete_tasks_failed)

        self.close()

    def on_get_tasks_finished(self, worker: TodoistWorker, result, _):
        tasks = worker.extract_value(result)
        if tasks != -1 and not None:
            self.listbox.foreach(lambda widget: self.listbox.remove(widget))

            for task in tasks:
                task_element = TodoistElement(task)
                self.listbox.add(task_element)
        else: # get_tasks Error
            self.on_get_tasks_failed()
        self.listbox.show_all()

    def on_get_tasks_failed(self):
        self._error_dialog("Todoist Dailies - Network Error", "Could not retrieve tasks!")

    def on_complete_tasks_failed(self):
        self._error_dialog("Todoist Dailies - Network Error", "Could not complete tasks!")
    
    def _error_dialog(self, title: str, secondary_text: str):
        error_dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        error_dialog.format_secondary_text(secondary_text)
        error_dialog.run()
        error_dialog.destroy()
