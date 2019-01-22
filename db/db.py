from contextlib import contextmanager
from subprocess import call
from core.models import IModel, Task, TaskItem

try:
	# sudo pip3 install SQLAlchemy
	import sqlalchemy as sa
	import sqlalchemy.orm as orm
except ModuleNotFoundError:
	exit_code = call('sudo pip3 install SQLAlchemy', shell=True)
	import sqlalchemy as sa
	import sqlalchemy.orm as orm
import sqlite3 as s3


class _Repo3:
	conn: s3.connect
	cmd_get = 'SELECT * FROM ? '
	cmd_get1 = 'SELECT * FROM ? WHERE id = ?'
	cmd_insert: str
	cmd_update: str

	def __init__(self, db: s3.connect):
		self.conn = db

	def get(self, Id): pass

	def get_list(self) -> tuple: return self._using_db(self._get_list)

	def insert(self, entity: IModel):
		if not entity.id:
			return self._using_db(lambda db: self._insert(db, entity), True)

	def update(self, entity: IModel): return self._using_db(lambda db: self._update(db, entity), True)

	#####################################################

	def _using_db(self, act, isCommit=False):
		db = self.conn.cursor()
		db.row_factory = self._map
		try:
			return act(db)
		finally:
			if isCommit:
				db.connection.commit()
			db.close()

	def _map(self, c: s3.Cursor, val): pass

	def _get_list(self, c: s3.Cursor) -> tuple: pass

	def _insert(self, c: s3.Cursor, entity: IModel): pass

	def _update(self, c: s3.Cursor, entity: IModel): pass


class RepoTask3(_Repo3):
	def __init__(self, conn: s3.connect):
		super(RepoTask3, self).__init__(conn)

	def _get_list(self, c: s3.Cursor):
		s1 = '''SELECT id, date, title, source, description, ti.* 
        FROM [task] t
        JOIN [task_item] ti ON ti.task_id = t.id'''
		c.execute('SELECT id, date, title, source, description FROM [task]')
		t = c.fetchall()
		return t

	def _insert(self, c: s3.Cursor, v: Task):
		s = 'INSERT INTO [task] (date, title, source, description) VALUES("%s", "%s", "%s", "%s")' % (v.date, v.title, v.source, v.description)
		r = c.execute(s)
		v.id = r
		return r

	def _update(self, c: s3.Cursor, v: Task):
		s = 'UPDATE [task] SET date = "%s", title = "%s", source = "%s", description = "%s" WHERE id = %i' % (v.date, v.title, v.source, v.description, v.id)
		r = c.executescript(s)
		return r

	def _map(self, c: s3.Cursor, t: tuple) -> Task:
		r = Task()
		r.id = t[0]
		r.date = t[1]
		r.title = t[2]
		r.source = t[3]
		r.description = t[4]

		s = 'SELECT id, task_id, date, title, solution, time_seconds FROM [task_item] WHERE task_id = ' + str(r.id)
		c2 = c.connection.execute(s)
		tt = c2.fetchall()
		r.items = tuple(self._map_item(r, i) for i in tt)
		return r

	@staticmethod
	def _map_item(r: Task, t: tuple) -> TaskItem:
		r = TaskItem(r)
		r.id = t[0]
		r.task_id = t[1]
		r.date = t[2]
		r.title = t[3]
		r.solution = t[4]
		r.time_seconds = t[5]
		return r


class Db3:
	def __init__(self, db_file):
		conn = s3.connect(db_file)
		conn.set_trace_callback(print)
		self.conn = conn
		self.repoTask = RepoTask3(conn)


#################################################################################################


class IRepo(object):
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

	def _class(self): pass

	def _query(self, session: orm.Session): pass


class RepoTask(IRepo):
	def _class(self): return Task

	def _query(self, session: orm.Session):
		return session.query(Task).options(orm.joinedload('items'))


class RepoTaskItem(IRepo):
	def _class(self): return TaskItem


class Db:
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
