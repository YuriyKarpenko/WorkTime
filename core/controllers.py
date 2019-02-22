from db.db import IDb, IRepo
import json
import os
import shutil
from core.models import Optiopns, Task
from datetime import datetime


class OptionController:
	def __init__(self):
		self._filename = 'options.json'
		self._options: Optiopns = None

	def get(self):
		if not self._options:
			self._options = self._load()
		return self._options

	def _load(self):
		data = OptionController.load_file(self._filename)
		if data:
			res = json.loads(data)
			return Optiopns(res)
		return Optiopns({'db_path': 'db.sqlite3', 'sources': 'EMail\nSkype\nTrello'})

	def save(self) -> bool:
		if self._options:
			s = json.dumps(self._options.to_dict())
			return OptionController.save_file(s, self._filename)
		return False

	@staticmethod
	def load_file(filename: str) -> str or None:
		if filename:
			try:
				with open(filename, 'rt') as f:
					data = f.read()
				return data
			except FileNotFoundError:
				pass
		return None

	@staticmethod
	def save_file(data: str, filename: str) -> bool:
		if filename and data:
			try:
				with open(filename, 'wt') as f:
					f.write(data)
				return True
			except OSError:
				raise
		return False


optionController = OptionController()


class _DbDbController:
	def __init__(self, repo: IRepo): self._repo = repo

	def refresh(self, entity): return self._repo.refresh(entity)


class TaskController(_DbDbController):
	# __slots__ = ('current')
	db: IDb

	def __init__(self):
		self.current: Task = None
		self._filename = optionController.get() and optionController.get().db_path or 'tasks.json'
		# TODO: create backup
		bak = self._filename + '.bak'
		c = 0
		min_date = datetime.now().timestamp()
		min_name = bak
		while c < 5 and os.path.exists(bak):
			d = os.path.getctime(bak)
			if(min_date > d):
				min_date = d
				min_name = bak
			bak = self._filename + '.bak' + str(c)
			c += 1
		if (c >= 5): bak = min_name
		shutil.copy(self._filename, bak)

		import db.db_native as db
		self.db = db.Db(self._filename)
		super(TaskController, self).__init__(self.db.repoTask)

	def get(self, Id):
		if Id:
			self.current = self._repo.get(Id)
			return self.current
		return None

	def get_list(self) -> tuple:
		res = self._repo.get_list()
		# print(__class__, 'get_list', res)
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
