"""
Contains utility scripts for multithreading related tasks.
"""

import logging
import multiprocessing
from typing import Callable, Iterator, TypeVar, Any, List


T = TypeVar("T")
R = TypeVar("R")


class SimpleConsumer(multiprocessing.Process):
    """Simple consumer thread."""

    class TerminateTask:
        """When received by the simple consumer, it terminates."""

    def __init__(
        self,
        on_message_received: Callable,
        task_list: multiprocessing.JoinableQueue,
        worker_index: int,
        result_queue: multiprocessing.Queue,
        consumer_name: str = "SimpleConsumer",
        *args,
        **kwargs,
    ) -> None:
        super().__init__()

        self._on_message_received = on_message_received
        self._task_list = task_list
        self._worker_index = worker_index
        self._result_queue = result_queue
        self._args = args
        self._kwargs = kwargs
        self._consumer_name = f"{consumer_name}-{worker_index}"

    def run(self) -> None:
        """Implements simple execution lifecycle."""
        for task in self._my_tasks():
            self._execute_task(task)

    def _my_tasks(self) -> Iterator[R]:
        """Yields new tasks as long as no `TerminateTask` is found."""
        has_terminated = False
        while not has_terminated:
            task = self._task_list.get()
            if not isinstance(task, SimpleConsumer.TerminateTask):
                yield task
            else:
                has_terminated = True

    def _execute_task(self, task: R):
        """Attempts to execute the task."""
        try:
            task_kwargs = {
                **self._kwargs,
                **task,
                "worker_id": self._worker_index,
            }
            result = self._on_message_received(*self._args, **task_kwargs)
            if not self._result_queue is None:
                self._result_queue.put(result)
        except Exception as ex:
            logging.warning(f"{self._consumer_name}: Failed with entry {task}: {ex}.")
            raise


class ExecutorService:
    def __init__(
        self,
        thread_count: int = 1,
        return_results: bool = False,
        use_early_return_results: bool = True,
        *args,
        **kwargs,
    ):
        """
        Constructs a simple executor service.
        :param thread_count: The number of used threads (min. 1).
        :param return_results: Whether the return value of the
        submitted tasks should be stored.
        :param use_early_return_results: If there are return values,
        whether these should be collected before threads are joined.
        :param *args, **kwargs: Any other parameters that are passed
        to the worker threads.
        """

        if thread_count < 1:
            raise ValueError("You can't have less than one thread.")

        self._thread_count = thread_count
        self._return_results = return_results
        self._use_early_return_results = use_early_return_results
        self._args = args
        self._kwargs = kwargs

        self._worklist = multiprocessing.JoinableQueue()
        self._workers: list[SimpleConsumer] = [None] * thread_count
        self._result_queue = multiprocessing.Queue() if return_results else None
        self._early_return_results: List[R] | None = None

    def do_task(self, task_callable, targs, tkwargs, *args, **kwargs):
        return task_callable(*targs, *args, **tkwargs, **kwargs)

    def start(self):
        """Initializes worker threads."""
        for index in range(self._thread_count):
            worker = SimpleConsumer(
                self.do_task,
                self._worklist,
                index,
                result_queue=self._result_queue,
                *self._args,
                **self._kwargs,
            )
            worker.start()
            self._workers[index] = worker

    def submit(self, task_callable: Callable[[T, Any], R], *targs, **tkwargs):
        """
        Submits a task.
        :param task_callable: the method that is executed by the thread.
        :param *targs, **tkwargs: Any other parameter that is passed to the method.
        """
        task_wrapper = {
            "task_callable": task_callable,
            "targs": targs,
            "tkwargs": tkwargs,
        }
        self._worklist.put(task_wrapper)

    def stop(self):
        """
        Terminates all the workers, collects their results
        early (if specified in the constructor), and joins
        them. This method is blocking.
        """
        # Kills workers.
        for _ in range(self._thread_count):
            self._worklist.put(SimpleConsumer.TerminateTask())

        # Collects results early if desired.
        if self._return_results and self._use_early_return_results:
            self._early_return_results = list(self.get_results_iter())

        # Waits until workers terminate.
        for worker in self._workers:
            worker.join()

    def get_results_iter(self) -> Iterator[R] | None:
        """
        Yields a result iterator, if there is one.
        """
        if self._early_return_results:
            raise ValueError(
                "Constructor parameter `early_return_results` can't be true when using this method."
            )
        if not self._return_results:
            return
        while not self._result_queue.empty() or not self._worklist.empty():
            yield self._result_queue.get()

    def get_results(self) -> List[R] | None:
        """
        Yields a list of results if there are any.
        """
        if not self._return_results:
            return None
        if self._use_early_return_results and not self._early_return_results is None:
            return self._early_return_results
        return list(self.get_results_iter())


def parallelize_tasks(
    tasks: Iterator[T],
    on_task_received: Callable[[T, int, int, int | str], R],
    thread_count: int = 1,
    return_results: bool = False,
    use_early_return_results: bool = True,
    *args,
    **kwargs,
) -> Iterator[R] | List[R] | None:
    """
    Implements basic scheme for emberassingly parallel
    work; i.e., data parallelism.
    :param tasks: The tasks that are executed.
    :param on_message_received: Callable that processes a task.
    It receives named parameters: `task`, `task_id`, `worker_id`, `total_tasks`
    and any other parameter that is passed in `*args` or `**kwargs`.
    :param thread_count: The number of used threads.
    :param return_results: Whether the results of `on_message_received`
    should be kept.
    :param use_early_return_results: If there are return values,
    whether these should be collected before threads are joined.
    :return: If `return_results` is set to True, it returns the results,
    otherwise, it returns `None`.
    """

    executor = ExecutorService(
        thread_count, return_results, use_early_return_results, *args, **kwargs
    )
    executor.start()
    total_tasks = len(tasks) if isinstance(tasks, list) else "unknown"
    for task_id, task in enumerate(tasks):
        executor.submit(
            task_callable=on_task_received,
            task=task,
            task_id=task_id,
            total_tasks=total_tasks,
        )
    executor.stop()
    if use_early_return_results:
        return executor.get_results()
    else:
        return executor.get_results_iter()
