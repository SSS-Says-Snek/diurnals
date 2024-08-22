from collections.abc import Callable
import gi

from todoist_api_python.api import TodoistAPI

gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gio, GLib

class TodoistWorker(GObject.GObject):
    def __init__(self, api: TodoistAPI):
        super().__init__()
        
        self.api = api

    def get_tasks_async(self, callback: Callable):
        task = Gio.Task.new(self, None, callback, None)
        task.set_return_on_cancel(False)
        task.run_in_thread(self._get_tasks_thread)

    def complete_tasks_async(self, completed_task_ids: list[str], error_callback: Callable[[], None]): # List of Todoist tasks, NOT GIO
        task = Gio.Task.new(self, None, None, None)
        task.set_return_on_cancel(False)
        task.run_in_thread(lambda *args: self._complete_tasks_thread(completed_task_ids, error_callback, *args))

    def extract_value(self, result):
        """Extract data from the task result"""
        if not Gio.Task.is_valid(result, self) or result.had_error():
            return -1
        else:
            return result.propagate_value().value

    def _get_tasks_thread(self, task: Gio.Task, *_):
        """Internal thread callback. don't use it dawg"""
        if task.return_error_if_cancelled():
            return
        
        try:
            tasks = self.api.get_tasks(filter="today|overdue")
        except Exception:
            task.return_error(GLib.Error("Failed to get tasks"))
        else:
            task.return_value(tasks)

    def _complete_tasks_thread(self, completed_task_ids: list[str], error_callback: Callable[[], None], task: Gio.Task, *_):
        """Internal thread callback. don't use it dawg"""
        if task.return_error_if_cancelled():
            return
        
        for completed_task in completed_task_ids:
            try:
                self.api.close_task(completed_task)
            except Exception:
                error_callback()
