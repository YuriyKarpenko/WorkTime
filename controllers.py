from db import Db 
import json
from models import Optiopns, Task, TaskItem


class OptionController:
    def __init__(self):
        self._filename = 'options.json'
        self._options: Optiopns = None

    def get(self):
        if not self._options:
            self._options = self._load()
        return self._options

    def _load(self):
        data = Db.load_file(self._filename)
        if data:
            res = json.loads(data)
            return Optiopns(res)
        return Optiopns()

    def save(self) -> bool:
        if self._options:
            s = json.dumps(self._options.to_dict())
            return Db.save_file(s, self._filename)
        return False


optionController = OptionController()


class TaskController:
    # __slots__ = ('current')
    db: Db

    def __init__(self):
        self.current: Task = None
        self._filename = optionController.get() and optionController.get().db_path or 'tasks.json'
        self.db = Db(self._filename)

    def get(self, Id):
        if id:
            self.current = self.db.repoTask.get(Id)
            return self.current
        return None

    def get_list(self) -> tuple:
        res = self.db.repoTask.get_list()
        print(res)
        return tuple(res)

    def insert(self, task: Task):
        self.current = task
        if task:
            self.db.repoTask.insert(task)

    def update(self, task: Task):
        self.current = task
        if task:
            self.db.repoTask.update(task)

    # items #########################################

    def get_item(self, Id):
        if self.current and Id:
            return next(i for i in self.current.items if i.id == Id)
        return None


taskController = TaskController()
