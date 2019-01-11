import datetime


def date_fromisoformat(ISOstr: str):
    ss = ISOstr.split('-', 3)
    return datetime.date(int(ss[0]), int(ss[1]), int(ss[2]))


# class JsonAbstract:
def to_dict(o):
    res = {}
    for k in o:
        v = o[k]
        t = type(v)
        # if t.
        res[k] = v
    return res


class Optiopns:
    __slots__ = ('db_path', 'sources')
    db_path: str
    sources: list

    def __init__(self, json: dict = None):
        if json:
            self.db_path = json.get('db_path') or ''
            self.sources = json.get('sources') or []
        else:
            self.db_path = ''
            self.sources = []

    def to_dict(self):
        return {'db_path': self.db_path, "sources": self.sources}


class Task:
    __slots__ = ('id', 'date', 'title', 'source', 'description', 'items', 'time')

    def __init__(self, json: dict = None):
        if json:
            self.id = int(json.get('id'))
            self.date = date_fromisoformat(json.get('date'))
            self.title = json.get('title') or ''
            self.source = json.get('source') or ''
            self.description = json.get('description') or ''
            self.items = [TaskItem(self, i) for i in list(json.get('items') or ())]
            self.time = self.calc_time()
        else:
            self.id = 0
            self.date = datetime.date.today()
            self.title = ''
            self.source = ''
            self.description = ''
            self.items = [TaskItem(self)]
            self.time = datetime.timedelta(0)

    def calc_time(self):
        r: datetime.timedelta = datetime.timedelta(0)
        for i in self.items:
            r += i.time
        return r
        return sum(i.time for i in self.items)

    def to_dict(self):
        """ https://python-scripts.com/json """
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'items': list(i.to_dict() for i in self.items),
            # 'time': self.time.
        }


class TaskItem:
    __slots__ = ('id', 'parentId', 'date', 'title', 'solution', 'time')

    def __init__(self, parent: Task, json: dict = None):
        if json:
            self.date = date_fromisoformat(json.get('date'))
            self.title = json.get('title', '')
            self.solution = json.get('solution', '')
            self.time = datetime.timedelta(0, int(json.get('time', '0')))
        else:
            self.date = datetime.date.today()
            self.title = ''
            self.solution = ''
            self.time = datetime.timedelta(0)

        self.parentId = parent.id
        self.id = None

    def __str__(self):
        return '{0} {1}'.format(self.solution, self.time)

    def to_dict(self):
        return {'date': self.date.isoformat(), 'title': self.title, 'solution': self.solution, 'time': self.time.total_seconds()}
