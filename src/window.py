from configparser import ConfigParser
from datetime import datetime

from gi.repository import Adw, Gtk
from todoist_api_python.api import TodoistAPI

from src.config_window import ConfigWindow
from src.todoist_element import TodoistElement
from src.todoist_worker import TodoistWorker


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
        box.add_css_class("window-box")

        # Header
        self.header_bar = Adw.HeaderBar()
        self.header_bar.add_css_class("flat")
        self.update_date()
        outer_box.append(self.header_bar)

        # Banner
        self.banner = Adw.Banner(title="Changes have been applied. Close?")
        self.banner.set_button_label("Close")
        self.banner.connect("button-clicked", lambda _: self.destroy())
        outer_box.append(self.banner)

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
        self.listbox.set_sort_func(TodoistElement.sort_rows)  # type: ignore

        no_tasks_page = Adw.StatusPage(
            title="No tasks to do currently",
            description="Enjoy the day with your free time!",
            icon_name="task-due-symbolic",
        )

        self.main_content = Gtk.Stack()
        self.main_content.add_named(self.listbox, "task-list")
        self.main_content.add_named(no_tasks_page, "no-tasks")
        box.append(self.main_content)

        # Get tasks and add them
        self.sync_tasks()

        # Bottom buttons
        self.close_button = Gtk.Button(label="Mark Done & Close")
        self.close_button.connect("clicked", self.on_close_button)

        self.quit_button = Gtk.Button(label="Quit Process")
        self.quit_button.connect("clicked", lambda _: self.destroy())

        buttons_hbox = Gtk.Box(spacing=24, halign=Gtk.Align.END)
        buttons_hbox.append(self.quit_button)
        buttons_hbox.append(self.close_button)
        box.append(buttons_hbox)

        self.widgets_to_remove: list[TodoistElement] = []

    def open_config(self, _):
        config_window = ConfigWindow(self.config, self.banner)
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

            if len(tasks) == 0:
                self.main_content.set_visible_child_name("no-tasks")
            else:
                self.main_content.set_visible_child_name("task-list")
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
