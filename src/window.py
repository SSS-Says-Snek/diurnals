from collections.abc import Callable
from configparser import ConfigParser
from datetime import date, datetime, timedelta

from gi.repository import Adw, Gtk
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

from src.config_window import ConfigWindow
from src.todoist_worker import TodoistWorker


class TodoistElement(Gtk.ListBoxRow):
    def __init__(
        self,
        task: Task,
        callback: Callable[[Gtk.CheckButton, "TodoistElement"], None],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.task = task

        self.set_selectable(False)
        self.due_date = None

        hbox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=24,
            margin_start=12,
            margin_end=12,
            margin_top=6,
            margin_bottom=6,
        )
        vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            halign=Gtk.Align.FILL
        )
        self.check_button = Gtk.CheckButton()
        self.check_button.connect("toggled", lambda button: callback(button, self))

        label = Gtk.Label(label=task.content, halign=Gtk.Align.START)
        vbox.append(label)
        if self.task.due is not None: # Set due date label
            label = "Due {}"
            css_classes = ["due-date"]
            due_date_str = self.task.due.date
            self.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            days_left = self.due_date - date.today()
            if days_left < timedelta(days=0):
                label = "Overdue"
                css_classes.append("overdue")
            elif days_left == timedelta(days=0):
                due_date_str = "today"
                css_classes.append("due-today")
            elif days_left < timedelta(days=7): # If less than a week, you can just refer to it by the weekday
                due_date_str = self.due_date.strftime("%A")
            else:
                due_date_str = self.due_date.strftime("%b %-d")

            due_date_label = Gtk.Label(label=label.format(due_date_str), halign=Gtk.Align.START) # Stupid noqa idk
            due_date_label.set_css_classes(css_classes)
            vbox.append(due_date_label)
        
        hbox.append(self.check_button)
        hbox.append(vbox)
        self.set_child(hbox)

    @staticmethod
    def sort_rows(left: "TodoistElement", right: "TodoistElement"):
        if left.due_date is None and right.due_date is None: # If there's no due date for both, they're equal
            return 0
        elif left.due_date is not None and right.due_date is None: # If L has due date, but R doesn't, L gets moved up
            return -1
        elif left.due_date is None and right.due_date is not None: # If R has due date, but L doesn't, L gets moved down
            return 1
        elif left.due_date is not None and right.due_date is not None: # for the type hint
            if left.due_date < right.due_date:
                return -1
            elif left.due_date == right.due_date:
                return 0
            elif left.due_date > right.due_date:
                return 1


class TodoistWindow(Adw.ApplicationWindow):
    def __init__(self, api_key: str, config: ConfigParser, application: Adw.Application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = application
        self.set_application(self.app)

        self.set_default_size(1000, 800)
        self.set_hide_on_close(True)

        self.api = TodoistAPI(api_key)
        self.todoist_worker = TodoistWorker(self.api, config)  # Concurrent

        self.config = config

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

        # List box
        self.listbox = Gtk.ListBox()
        self.listbox.add_css_class("boxed-list")
        self.listbox.props.selection_mode = Gtk.SelectionMode.NONE
        self.listbox.set_vexpand(True)
        self.listbox.set_sort_func(TodoistElement.sort_rows)
        box.append(self.listbox)

        # Get tasks and add them
        self.sync_tasks()

        # Bottom buttons
        self.close_button = Gtk.Button(label="Mark Done & Close")
        self.quit_button = Gtk.Button(label="Quit Process")

        self.close_button.connect("clicked", self.on_close_button)
        self.quit_button.connect("clicked", lambda _: self.destroy())

        buttons_hbox = Gtk.Box(spacing=24, halign=Gtk.Align.END)
        buttons_hbox.append(self.quit_button)
        buttons_hbox.append(self.close_button)
        box.append(buttons_hbox)

        self.widgets_to_remove: list[TodoistElement] = []

    def open_config(self, _):
        config_window = ConfigWindow(self.config)
        config_window.present(self)

    def toggle_complete_task(self, button: Gtk.CheckButton, child: TodoistElement):
        if button.get_active():
            self.widgets_to_remove.append(child)
        else:
            self.widgets_to_remove.remove(child)

    def complete_selected_tasks(self, todoist_element: TodoistElement, task_ids: list[str]):
        if todoist_element.check_button.get_active():
            task_ids.append(todoist_element.task.id)

    def update_date(self):
        formatted_date = datetime.now().strftime("%B %d, %Y")
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
            task_ids.append(widget_to_remove.task.id)
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
        else:  # get_tasks Error
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
