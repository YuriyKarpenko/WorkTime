from datetime import date, timedelta


class Optiopns:
	__slots__ = ('db_path', 'sources')
	db_path: str
	sources: str

	def __init__(self, json: dict = None):
		if json:
			self.db_path = json.get('db_path', '')
			self.sources = json.get('sources', '')
		else:
			self.db_path = ''
			self.sources = ''

	def to_dict(self):
		return {'db_path': self.db_path, "sources": self.sources}


class IModel(object):
	def __init__(self):
		self.id: int = None
		self.date = date.today()
		self.title = ''


class Task(IModel):
	# __slots__ = ('id', 'date', 'title', 'source', 'description', 'items', 'time')
	# __slots__ = ('date', 'title', 'source', 'description', 'items', 'time')

	time: timedelta = property(lambda self: timedelta(0, sum((i.time_seconds for i in self.items), 0) // 1))

	def __init__(self):
		super(Task, self).__init__()
		self.source = ''
		self.description = ''
		self.items = [TaskItem(self)]

	def __repr__(self):
		return "<%s(%i, %s, '%s', '%s', '%s', %i)>" % (self.__class__.__name__, self.id or 0, self.date, self.title, self.source, self.description, len(self.items))


class TaskItem(IModel):
	# __slots__ = ('id', 'parentId', 'date', 'title', 'solution', 'time')
	time: timedelta = property(lambda self: timedelta(0, self.time_seconds or 0), lambda self, value: setattr(self, 'time_seconds', (value and value.total_seconds() // 1)))

	def __init__(self, parent: Task):
		super(TaskItem, self).__init__()
		self.solution = ''
		self.time_seconds = 0
		# self.time = datetime.timedelta(0)

		self.task_id = parent.id
		self.task = parent

	def __str__(self):
		return '{0} {1}'.format(self.solution, self.time)
