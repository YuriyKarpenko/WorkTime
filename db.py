import json
from models import *


class Db:
    _optionsFilename = 'options.json'

    _options: Optiopns = None

    @property
    def options(self):
        if not Db._options:
            Db._options = Db.load_option()
        return Db._options

    # @taskList.deleter
    # def taskList(self):
    #     pass
    #
    # @taskList.setter
    # def taskList(self, v: TaskList):
    #     pass

    @staticmethod
    def load_option():
        try:
            with open(Db._optionsFilename, 'rt') as f:
                data = f.read()
            if data:
                res = json.loads(data)
                return Optiopns(res)
        except FileNotFoundError:
            pass
        return Optiopns()

    @staticmethod
    def load_tasks(fileName: str):
        try:
            with open(fileName, 'rt') as f:
                data = f.read()
            if data:
                res = list(json.loads(data))
                return [Task(i) for i in res]
        except FileNotFoundError:
            pass
        return []

    @staticmethod
    def _save_options(value: Optiopns):
        try:
            with open(Db._optionsFilename, 'wt') as f:
                # d = to_dict(value)
                json.dump(value.to_dict(), f)
            return True
        except OSError:
            return False

    @staticmethod
    def save_options():
        return Db._save_options(Db._options)

    @staticmethod
    def save_tasks(value, fileName: str):
        if value:
            data = json.dumps(value)  # если писать напрямую, ломает структуру файла при ошибкаx
            with open(fileName, 'wt') as f:
                f.write(data)


db = Db()
