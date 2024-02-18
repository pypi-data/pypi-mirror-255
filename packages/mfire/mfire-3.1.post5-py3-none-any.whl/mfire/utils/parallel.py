"""Module for safe parallel processing
"""
from __future__ import annotations

import os
import time
import traceback
from enum import Enum
from multiprocessing import TimeoutError as MultiTimeoutError
from multiprocessing import get_context
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple

from mfire.settings.logger import Logger

LOGGER = Logger(name="utils.parallel")
error_callback = 0


class TaskStatus(str, Enum):
    """Possible status of a task"""

    NEW = ("NEW", False)
    PENDING = ("PENDING", False)
    RUNNING = ("RUNNING", False)
    FAILED = ("FAILED", True)
    TIMEOUT = ("TIMEOUT", True)
    DONE = ("DONE", False)

    is_error: bool

    def __new__(cls, value: str, is_error: bool) -> "TaskStatus":
        """Initialize a new TaskStatus object.

        Args:
            value (str): String value of the Task Status.
            is_error (bool): Whether the given status is an error.

        Returns:
            TaskStatus: New TaskStatus object.
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.is_error = is_error
        return obj


class Task:
    """Wrapping of a task containing a function to apply on given
    arguments and keyword arguments.
    """

    def __init__(
        self,
        func: Callable,
        args: Optional[Iterable] = None,
        kwds: Optional[Mapping] = None,
        callback: Optional[Callable] = None,
        name: Optional[str] = None,
    ) -> None:
        """Initialization method.

        Args:
            func (Callable): Function to call.
            args (Optional[Iterable]): Arguments to pass to the function. Defaults
                to None.
            kwds (Optional[Mapping]): Keyword arguments to pass to the function.
                Defaults to None.
            callback (Optional[Callable]): Function to call when the data is ready.
                Defaults to None.
            name (Optional[str]): Name of the tasks (for logging its status).
                Defaults to None.
        """
        self.func = func
        self.args = list(args) if args is not None else []
        self.kwds = dict(kwds) if kwds is not None else {}
        self.callback = callback if callback is not None else lambda x: None
        self.name = name if name is not None else "Task"
        self.status = TaskStatus.NEW
        self.async_result = None

    def change_status(self, new_status: TaskStatus, **kwargs):
        """Changes the task's status and notifies through the logger.

        Args:
            new_status (TaskStatus): New status of the task.
        """
        if self.status != new_status:
            msg = f"Task {self.name}: {self.status.value} -> {new_status.value}"
            if new_status.is_error:
                LOGGER.error(msg, **kwargs)
            else:
                LOGGER.info(msg, **kwargs)
            self.status = new_status

    def run(self) -> Any:
        """Method for calling self.func with self.args and self.kwds.

        Returns:
            Any: The result of self.func(*self.args, **self.kwds).
        """
        try:
            self.change_status(TaskStatus.RUNNING)
            result = self.func(*self.args, **self.kwds)
            self.callback(result)
            self.change_status(TaskStatus.DONE)
            return result
        except Exception as excpt:
            self.change_status(TaskStatus.FAILED)
            raise excpt

    def __repr__(self) -> str:
        return f"{self.name} (status={self.status.value})"

    def __str__(self) -> str:
        return repr(self)


class Parallel(Iterable):
    """Class that wraps the usage of multiprocessing.pool.Pool.apply_async
    to make it safer by catching Exceptions and triggering timeouts.
    """

    def __init__(self, processes: Optional[int] = os.cpu_count()):
        """Initialization method for a Parallel object.

        Args:
            processes (Optional[int]): Number of processes to use. Defaults to
                os.cpu_count().
        """
        self.processes = max(processes or 1, 1)
        self._tasks: List[Task] = []
        global error_callback
        error_callback = 0

    def __iter__(self) -> Iterable[Task]:
        return iter(self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __repr__(self) -> str:
        status_counts = self.status_count
        status_str = "; ".join(
            f"{count} {status.value}" for status, count in status_counts if count > 0
        )
        return f"Parallel({len(self)} tasks: {status_str})"

    @property
    def status_count(self) -> List[Tuple[str, int]]:
        """Counts the number of tasks for each possible status.

        Returns:
            List[Tuple[str, int]]: A list containing each TaskStatus
                and the corresponding number of tasks with that status.
        """
        statuses = [task.status for task in self._tasks]
        return [(status, statuses.count(status)) for status in TaskStatus]

    def clean(self) -> None:
        """Cleans the tasks."""
        self._tasks = []
        global error_callback
        error_callback = 0

    @property
    def queue(self) -> List[Task]:
        """Tasks that are new or pending.

        Returns:
            List[Task]: A list of tasks in the queue.
        """
        return [
            t for t in self._tasks if t.status in (TaskStatus.NEW, TaskStatus.PENDING)
        ]

    def _error_callback(self, excpt: Exception) -> None:
        """Error callback method used during the "get" execution.
        It is used when a sub-process fails and logs the caught exception.

        Args:
            excpt (Exception): The exception to log.
        """
        try:
            trace = traceback.format_exception(type(excpt), excpt, excpt.__traceback__)
            LOGGER.error(f"An error has been caught: {repr(excpt)}.\n" + "".join(trace))
        finally:
            global error_callback
            error_callback += 1
            return  # to avoid exception propagation

    def apply(
        self,
        func: Callable,
        task_name: str,
        args: Optional[Iterable] = None,
        kwds: Optional[Mapping] = None,
        callback: Optional[Callable] = None,
    ) -> str:
        """Loads a task into the queue following an "apply" schema,
        which means providing a function and its arguments and keyword arguments.

        Warning: This method doesn't trigger any processing. To run the
        loaded tasks, you must call self.run() after.

        Args:
            func (Callable): The function to apply.
            task_name (str): The name of the task (for logging purposes).
            args (Optional[Iterable]): The arguments to pass to the function.
                Defaults to None.
            kwds (Optional[Mapping]): The keyword arguments to pass to the function.
                Defaults to None.
            callback (Optional[Callable]): The function to call when the data is ready.
                Defaults to None.

        Returns:
            str: The name of the added task.
        """
        task = Task(func=func, args=args, kwds=kwds, callback=callback, name=task_name)
        self._tasks.append(task)
        return f"{task_name} (task n°{len(self._tasks)})"

    def run(self, timeout: Optional[int] = None):
        """Launches the multiprocessing of the previously loaded tasks.

        Args:
            timeout (Optional[int]): The maximum duration in seconds to run all the
            tasks. Defaults to None.
        """
        start = time.time()
        keep_running = True
        remaining_time = 1
        nb_tasks, nb_success = len(self.queue), 0
        LOGGER.info(f"Starting parallel processing: {nb_tasks} tasks to process.")
        # maxtasksperchild = 20 to speed up by avoiding respawn of processes
        processes = max(1, self.processes - 1) if self.processes is not None else 1
        with get_context("spawn").Pool(
            processes=processes, maxtasksperchild=20
        ) as pool:
            while keep_running and remaining_time > 0:
                # Managing remaining time if needed
                if timeout is not None:
                    elapsed_time = time.time() - start
                    remaining_time = max(timeout - elapsed_time, 0)

                keep_running = False
                for task in self.queue:
                    if task.status == TaskStatus.NEW:
                        task.async_result = pool.apply_async(
                            task.func,
                            args=task.args,
                            kwds=task.kwds,
                            callback=task.callback,
                            error_callback=self._error_callback,
                        )
                        task.change_status(TaskStatus.PENDING)
                        time.sleep(0.001)  # To force the process to start
                        keep_running = True

                    elif task.async_result.ready():
                        if task.async_result.successful():
                            task.change_status(TaskStatus.DONE)
                            nb_success += 1
                        else:
                            task.change_status(TaskStatus.FAILED)
                    else:
                        keep_running = True
                time.sleep(0.5)  # To prevent main CPU hogging

            for task in self.queue:
                try:
                    task.async_result.get(timeout=0)
                    task.change_status(TaskStatus.DONE)
                    nb_success += 1
                except MultiTimeoutError:
                    task.change_status(TaskStatus.TIMEOUT)
                except Exception:
                    task.change_status(TaskStatus.FAILED, exc_info=True)

        LOGGER.info(
            "End of parallel processing."
            f"\t{nb_success-error_callback}/{nb_tasks} tasks done."
            f"\tElapsed time: {time.time() - start:.3f}s."
            f"\t(errors in callback {error_callback})."
        )
