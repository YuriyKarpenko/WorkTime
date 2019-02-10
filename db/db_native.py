from contextlib import contextmanager
import sqlite3 as s3
from core.models import IModel, Task, TaskItem
from db.db import IDb, IRepo


def screening(s: str) -> str: return s.replace('"', "'")

class _Repo(IRepo):
	__abstract__ = True
	_create_table : str
	_select_base : str
	db : IDb

	def __init__(self, db: IDb):
		self.db = db
		db.exec_1(self._create_table)

	def get(self, Id: int): return self.db.exec_1(self._get_sql(Id), self._row_factory)

	def get_list(self) -> tuple: return self.db.exec_list(self._get_list_sql(), self._row_factory)

	def insert(self, entity: IModel): return self.db.exec_ins(self._insert_sql(entity))

	def update(self, entity: IModel): return self.db.exec_1(self._update_sql(entity))

	def refresh(self, entity: IModel):	pass

	def set(self, entity: IModel):
		if entity:
			return self.update(entity) if entity.id else self.insert(entity)

	#####################################################

	def _map(self, vals: tuple): return vals

	def _row_factory(self, c: s3.Cursor, row: tuple): return self._map(row)

	def _get_sql(self, Id: int) -> str: return self._select_base + ' WHERE id = {}'.format(Id)

	def _get_list_sql(self) -> str: return self._select_base

	def _insert_sql(self, entity: IModel) -> str: pass

	def _update_sql(self, entity: IModel) -> str: pass


class RepoTask(_Repo):
	_create_table = """CREATE TABLE IF NOT EXISTS [task] (
	[id] INTEGER NOT NULL,
	[date] DATE NOT NULL,
	[title] VARCHAR,
	[source] VARCHAR,
	[description] VARCHAR,
	PRIMARY KEY ([id])
	)"""
	_select_base = 'SELECT id, date, title, source, description FROM [task] '

	def _insert_sql(self, v):
		return 'INSERT INTO [task] (date, title, source, description) VALUES("%s", "%s", "%s", "%s")' % (v.date, screening(v.title), screening(v.source), screening(v.description))

	def _update_sql(self, v):
		return 'UPDATE [task] SET date = "%s", title = "%s", source = "%s", description = "%s" WHERE id = %i' % (v.date, screening(v.title), screening(v.source), screening(v.description), v.id)

	def insert(self, entity: Task):
		if entity:
			entity.id = self.db.exec_ins(self._insert_sql(entity))
			for i in entity.items:
				i.task_id = entity.id
				self.db.repoTaskItem.insert(i)
			return entity.id
		return None

	def update(self, entity):
		if entity:
			self.db.exec_1(self._update_sql(entity))
			for i in entity.items:
				self.db.repoTaskItem.set(i)

	def _map(self, t: tuple) -> Task:
		r = Task()
		r.id = t[0]
		r.date = t[1]
		r.title = t[2]
		r.source = t[3]
		r.description = t[4]

		r.items = self.db.repoTaskItem.get_for_parent(r)

		return r


class RepoTaskItem(_Repo):
	_create_table = """CREATE TABLE IF NOT EXISTS [task_item] (
	[id] INTEGER NOT NULL PRIMARY KEY,
	[task_id] INTEGER NOT NULL REFERENCES [task](id),
	[date] DATE NOT NULL,
	[title] VARCHAR,
	[solution] VARCHAR,
	[time_seconds] INTEGER
	)"""
	_select_base = 'SELECT id, task_id, date, title, solution, time_seconds FROM [task_item] '

	def get_for_parent(self, task: Task) -> list:
		if task:
			r = self.db.exec_list(self._select_base + ' WHERE task_id = {}'.format(task.id))
			return list(self._map(i, task) for i in r)
		else:
			return None

	def _insert_sql(self, v: TaskItem) -> str:
		return 'INSERT INTO [task_item] (task_id, date, title, solution, time_seconds) VALUES(%i, "%s", "%s", "%s", %i)' % (v.task_id, v.date, screening(v.title), screening(v.solution), v.time_seconds)

	def _update_sql(self, v: TaskItem) -> str:
		return 'UPDATE [task_item] SET task_id = %i, date = "%s", title = "%s", solution = "%s", time_seconds = %i WHERE id = %i' % (v.task_id, v.date, screening(v.title), screening(v.solution), v.time_seconds, v.id)

	def _map(self, t: tuple, task = None) -> Task:
		r = TaskItem(task)
		r.id = t[0]
		r.task_id = t[1]
		r.date = t[2]
		r.title = t[3]
		r.solution = t[4]
		r.time_seconds = t[5]
		return r


#################################################################################################

class Db(IDb):
	def __init__(self, db_file):
		self.conn = s3.connect(db_file)
		self.conn.set_trace_callback(print)
		self.repoTask = RepoTask(self)
		self.repoTaskItem = RepoTaskItem(self)

	def exec_1(self, sql: str, row_factory = None) -> IModel:
		with self._execute(sql, row_factory) as c:
			return c.fetchone()

	def exec_list(self, sql: str, row_factory = None) -> tuple:
		with self._execute(sql, row_factory) as c:
			return c.fetchall()

	def exec_ins(self, sql: str, row_factory = None) -> int:
		with self._execute(sql, row_factory) as c:
			return c.lastrowid

	@contextmanager
	def _execute(self, sql: str, row_factory = None) -> s3.Cursor:
		cursor = self.conn.cursor()
		cursor.row_factory = row_factory
		try:
			yield cursor.execute(sql)
			self.conn.commit()
		# except sqlite3.DatabaseError as err:
		except Exception as err:
			self.conn.rollback()
			print('Error: ', err, sql)
		finally:
			cursor.close()

