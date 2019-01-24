from contextlib import contextmanager
from core.models import IModel, Task, TaskItem
try:
	# sudo pip3 install SQLAlchemy
	import sqlalchemy as sa
	import sqlalchemy.orm as orm
except ModuleNotFoundError:
	from subprocess import call
	exit_code = call('sudo pip3 install SQLAlchemy', shell=True)
	import sqlalchemy as sa
	import sqlalchemy.orm as orm
from db import IDb, IRepo

class _Repo(IRepo):
	__abstract__ = True

	def __init__(self, session: orm.Session):
		self.db = session
		self._type = self._class()
		self.query = self._query(session) or session.query(self._type)

	# opt = orm.Load(self._type).()
	# self.query.options(orm.joinedload())

	def get(self, Id):
		try:
			return self.query.filter(self._type.id == Id).one()
		except:
			return None

	def get_list(self) -> tuple:
		r1 = tuple(self.query.all())
		return r1

	def insert(self, entity):
		self.db.add(entity)
		return self.db.commit()

	def update(self, entity):
		return self.db.commit()

	def refresh(self, entity): self.db.refresh(entity)

	def _class(self): pass

	def _query(self, session: orm.Session): pass


class RepoTask(_Repo):
	def _class(self): return Task

	def _query(self, session: orm.Session):
		return session.query(Task).options(orm.joinedload('items'))


class RepoTaskItem(_Repo):
	def _class(self): return TaskItem


class Db(IDb):
	session_maker: orm.sessionmaker

	def __init__(self, db_file):
		meta = sa.MetaData()
		self._init_map(meta)

		engine = sa.create_engine('sqlite:///' + db_file, pool_recycle=7200, echo=True, )
		__class__.session_maker = orm.sessionmaker(engine)
		self.session = self.session_maker()

		self.repoTask = RepoTask(self.session)
		self.repoTaskItem = RepoTaskItem(self.session)

		meta.create_all(engine)

	@staticmethod
	def _init_map(meta):
		tabTask = sa.Table('task', meta,
			sa.Column('id', sa.Integer, primary_key=True),
			sa.Column('date', sa.Date), sa.Column('title',
				sa.String), sa.Column('source', sa.String),
			sa.Column('description', sa.String), )
		orm.mapper(Task, tabTask, properties={'items': orm.relationship(TaskItem, backref='task')})

		tabTaskItem = sa.Table('task_item', meta,
			sa.Column('id', sa.Integer, primary_key=True),
			sa.Column('task_id', sa.Integer, sa.ForeignKey('task.id')),
			sa.Column('date', sa.Date),
			sa.Column('title', sa.String),
			sa.Column('solution', sa.String),
			sa.Column('time_seconds', sa.Integer), )
		orm.mapper(TaskItem, tabTaskItem)

	def commit(self):
		self.session.commit()

	# @contextmanager
	# def session_scope(self):
	# 	"""Provide a transactional scope around a series of operations."""
	# 	session: orm.Session = __class__.session_maker()
	# 	try:
	# 		yield session
	# 		session.flush()
	# 		session.commit()
	# 	except:
	# 		session.rollback()
	# 		raise
	# 	finally:
	# 		session.close()

	@contextmanager
	def db_scope(self):
		"""Provide a transactional scope around a series of operations."""
		# session: orm.Session = __class__.session_maker()
		try:
			yield self
			self.session.flush()
			self.session.commit()
		except:
			self.session.rollback()
			raise
# finally:
#     session.close()
