from core.models import IModel


class IRepo:
	__abstract__ = True
	def get(self, Id: str) -> IModel: pass

	def get_list(self) -> tuple: pass

	def insert(self, entity: IModel): pass

	def update(self, entity: IModel): pass

	def refresh(self, entity: IModel): pass


class IDb:
	__abstract__ = True
	repoTask: IRepo
	repoTaskItem: IRepo
