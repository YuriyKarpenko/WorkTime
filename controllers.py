import db
import json
from models import *


class OptionController:
    def __init__(self):
        self._filename = 'options.json'
        self._options: Optiopns = None

    def get(self):
        if not self._options:
            self._options = self._load()
        return self._options

    def _load(self):
        data = db.Db.load_file(self._filename)
        if data:
            res = json.loads(data)
            return Optiopns(res)
        return Optiopns()

    def save(self) -> bool:
        if self._options:
            s = json.dumps(self._options.to_dict())
            return db.Db.save_file(s, self._filename)
        return False


optionController = OptionController()


class TaskController:
    # __slots__ = ('current')

    def __init__(self):
        self._tasks: list = None
        self.current: Task = None
        self._filename = optionController.get() and optionController.get().db_path or 'tasks.json'

    def get(self, Id):
        if id:
            self.current = next(i for i in self.get_list() if i.id == Id)
            return self.current
        return None

    def get_list(self) -> list:
        if not self._tasks:
            data = db.Db.load_file(self._filename)
            if data:
                res = list(json.loads(data))
                self._tasks = [Task(i) for i in res]
        return self._tasks or []

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
            if data:
                s = json.dumps(data)  # если писать напрямую, ломает структуру файла при ошибкаx
                db.Db.save_file(s, self._filename)

    # items #########################################

    def get_item(self, Id):
        if self.current and Id:
            return next(i for i in self.current.items if i.id == Id)
        return None


taskController = TaskController()
