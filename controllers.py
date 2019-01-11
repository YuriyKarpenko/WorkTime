from db import *


class TaskController:
    # __slots__ = ('current')

    def __init__(self):
        self._tasks: list = None
        self.current: Task = None
        self._filename = db.options and db.options.db_path or 'tasks.json'

    def get(self, Id):
        if id:
            self.current = next(i for i in self.get_list() if i.id == Id)
            return self.current
        return None

    def get_list(self):
        if not self._tasks:
            self._tasks = Db.load_tasks(self._filename) or []
        return self._tasks

    def insert(self, task: Task):
        self.current = task
        if task:
            self.get_list()
            self._tasks.append(task)

    def save(self):
        if self._tasks:
            data = []
            for i in self._tasks:
                if not i.id:
                    i.id = id(i)
                    for j in i.items:
                        j.parentId = i.id
                        j.id = j.id or id(j)
                data.append(i.to_dict())
            Db.save_tasks(data, self._filename)

    # items #########################################

    def get_item(self, Id):
        if self.current and Id:
            return next(i for i in self.current.items if i.id == Id)
        return None


taskController = TaskController()
