from dataclasses import dataclass
import unittest
import multiprocessing

from wmeijer_utils.multithreading import parallelize_tasks


THREAD_COUNT = 8
WORK_LOAD = 10000


@dataclass
class MyObject:
    task: int
    task_id: int
    worker_id: int
    total_tasks: int | str


def return_task(task, task_id, worker_id, total_tasks):
    return task


def return_dict(task, task_id, worker_id, total_tasks):
    return {
        "task": task,
        "task_id": task_id,
        "worker_id": worker_id,
        "total_tasks": total_tasks,
        "constant": "my_constant",
    }


def return_object(task, task_id, worker_id, total_tasks):
    return MyObject(task, task_id, worker_id, total_tasks)


class TestMultithreading(unittest.TestCase):
    def test_paralellize_tasks_termination(self):
        tasks = range(WORK_LOAD)

        def bar():
            results = parallelize_tasks(
                tasks, return_object, thread_count=THREAD_COUNT, return_results=True
            )

        p = multiprocessing.Process(target=bar)
        p.start()
        p.join(timeout=2)
        self.assertFalse(p.is_alive(), "Process did not terminate.")
        p.kill()

    def test_paralellize_tasks_no_results(self):
        tasks = range(WORK_LOAD)

        results = parallelize_tasks(
            tasks, return_task, thread_count=THREAD_COUNT, return_results=False
        )

        self.assertIsNone(results)

    def test_paralellize_tasks_with_primitive_results(self):
        tasks = range(WORK_LOAD)

        results = parallelize_tasks(
            tasks, return_task, thread_count=THREAD_COUNT, return_results=True
        )

        results = list(results)

        self.assertEqual(len(results), WORK_LOAD)

        tasks = set(tasks)
        results = set(results)
        intersect = tasks.intersection(results)
        self.assertEqual(len(intersect), WORK_LOAD, "Received incorrect results.")

    def test_paralellize_countable_tasks_with_dict_results(self):
        tasks = list(range(WORK_LOAD))

        results = parallelize_tasks(
            tasks, return_dict, thread_count=THREAD_COUNT, return_results=True
        )

        # Result size test
        results = list(results)
        self.assertEqual(len(results), WORK_LOAD)

        # Content test.
        valid_worker_ids = set(range(0, THREAD_COUNT))
        results = sorted(results, key=lambda element: element["task"])
        for result, task in zip(results, tasks):
            self.assertEqual(result["task"], task)
            self.assertIn(result["worker_id"], valid_worker_ids)
            self.assertEqual(result["total_tasks"], len(tasks))
            self.assertEqual(result["constant"], "my_constant")

    def test_paralellize_uncountable_tasks_with_dict_results(self):
        tasks = range(WORK_LOAD)

        results = parallelize_tasks(
            tasks, return_dict, thread_count=THREAD_COUNT, return_results=True
        )

        # Result size test
        results = list(results)
        self.assertEqual(len(results), WORK_LOAD)

        # Content test.
        valid_worker_ids = set(range(0, THREAD_COUNT))
        results = sorted(results, key=lambda element: element["task"])
        for result, task in zip(results, tasks):
            self.assertEqual(result["task"], task)
            self.assertIn(result["worker_id"], valid_worker_ids)
            self.assertEqual(result["total_tasks"], "unknown")
            self.assertEqual(result["constant"], "my_constant")

    def test_paralellize_tasks_with_object_results(self):
        tasks = range(WORK_LOAD)

        results = parallelize_tasks(
            tasks, return_object, thread_count=THREAD_COUNT, return_results=True
        )

        # Result size test
        results = list(results)
        self.assertEqual(len(results), WORK_LOAD)

        # Content test.
        valid_worker_ids = set(range(0, THREAD_COUNT))
        valid_task_ids = set(range(0, WORK_LOAD))
        used_task_ids = set()
        results = sorted(results, key=lambda element: element.task)
        for result, task in zip(results, tasks):
            self.assertIsInstance(result, MyObject)
            self.assertEqual(result.task, task)
            self.assertIn(result.worker_id, valid_worker_ids)
            self.assertEqual(result.total_tasks, "unknown")
            self.assertIn(result.task_id, valid_task_ids)
            self.assertNotIn(result.task_id, used_task_ids)

            used_task_ids.add(result.task_id)
