from dataclasses import dataclass

from .request import Request


@dataclass
class Task:
    def __init__(self, task: list[Request] | None = None):
        self._tasks = task if task else []

    def add(self, task: Request):
        self._tasks.append(task)

    def remove(self, task: Request):
        self._tasks.remove(task)

    def __repr__(self):
        return f'{self._tasks}'

    def __len__(self):
        return len(self._tasks)

    def __getitem__(self, index):
        return self._tasks[index]

    def __setitem__(self, index, value):
        self._tasks[index] = value

    def __delitem__(self, index):
        del self._tasks[index]
