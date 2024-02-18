import time

import pytest

from mfire.utils.parallel import Parallel, Task, TaskStatus


def func(n: int) -> int:
    if n in [1, 3]:
        raise ValueError(n)
    if n == 2:
        time.sleep(0.5)
    if n == 4:
        time.sleep(15)
    return n**2


class TestTask:
    def test_default_init(self):
        task = Task(func=func)
        assert str(task) == "Task (status=NEW)"

    def test_change_status(self):
        task = Task(func=func)
        assert task.status == TaskStatus.NEW

        task.change_status(TaskStatus.PENDING)
        assert task.status == TaskStatus.PENDING

        task.change_status(TaskStatus.FAILED)
        assert task.status == TaskStatus.FAILED

    def test_run(self):
        task = Task(func=func, args=(2,))
        result = task.run()
        assert task.status == TaskStatus.DONE
        assert result == 4

        task = Task(func=func, args=(1,))
        with pytest.raises(ValueError, match="1"):
            task.run()
        assert task.status == TaskStatus.FAILED


class TestParallel:
    def test_apply(self):
        p = Parallel()
        assert p.apply(func, task_name="TestParallelx") == "TestParallelx (task n°1)"
        assert p.apply(func, task_name="TestParallely") == "TestParallely (task n°2)"

    def test_clean(self):
        p = Parallel()
        p.apply(func, task_name="TestParallel")
        assert len(p) == 1

        p.clean()
        assert len(p) == 0

    def test_run(self):
        p = Parallel(2)
        res = []

        for i in range(5):
            p.apply(func, task_name="TestParallel", args=(i,), callback=res.append)

        p.run(timeout=10)
        assert res == [0, 4]

        expected_statuses = [
            TaskStatus.DONE,
            TaskStatus.FAILED,
            TaskStatus.DONE,
            TaskStatus.FAILED,
            TaskStatus.TIMEOUT,
        ]
        for task, exp_status in zip(p, expected_statuses):
            assert task.status == exp_status

        assert str(p) == "Parallel(5 tasks: 2 FAILED; 1 TIMEOUT; 2 DONE)"
