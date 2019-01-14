import datetime


def date_fromisoformat(ISOstr: str):
    ss = ISOstr.split('-', 3)
    return datetime.date(int(ss[0]), int(ss[1]), int(ss[2]))


def to_dict(o):
    res = {}
    for k in o:
        v = o[k]
        # t = type(v)
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


class _model(object):
    id: int = None


class Task(_model):
    #__slots__ = ('id', 'date', 'title', 'source', 'description', 'items', 'time')
    #__slots__ = ('date', 'title', 'source', 'description', 'items', 'time')

    def __init__(self):
        self.date = datetime.date.today()
        self.title = ''
        self.source = ''
        self.description = ''

        self.items = [TaskItem(self)]
        self.time = datetime.timedelta(0)

    def calc_time(self):
        r: datetime.timedelta = datetime.timedelta(0)
        # for i in self.items:
        #     r += i.time
        # return r
        return sum((i.time for i in self.items), r)

    def __repr__(self):
        return "<%s(%i, %s, '%s')>" % (self.__class__.__name__, self.id or 0, self.date, self.title)


class TaskItem(_model):
    #__slots__ = ('id', 'parentId', 'date', 'title', 'solution', 'time')
    _time: datetime.timedelta

    def __init__(self, parent: Task):
        self.date = datetime.date.today()
        self.title = ''
        self.solution = ''
        self.time_seconds = 0
        #self.time = datetime.timedelta(0)

        self.task_id = parent.id
        self.task = parent

    def __str__(self):
        return '{0} {1}'.format(self.solution, self.time)

    @property
    def time(self) -> datetime.timedelta:
        self._time = datetime.timedelta(0, self.time_seconds or 0)
        return self._time
    
    @time.setter
    def time(self, value: datetime.timedelta):
        self._time = value
        self.time_seconds = value and value.total_seconds() or 0
