import os
from models import Task, TaskItem
#import sqlite3 as sl3
# sudo pip3 install SQLAlchemy
import sqlalchemy as sa
import sqlalchemy.orm as orm


class _Repo:
    def __init__(self, db):
        self.db = db

    def get(self, id):
        pass

    def get_list(self):
        pass

    def insert(self, entity):
        self.db.add(entity)
        self.db.commit()

    def update(self, entity):
        self.db.update(entity)
        self.db.commit()


class RepoTask(_Repo):
    def __init__(self, meta: sa.MetaData, session):
        super().__init__(session)
        #self.db = session

        tab = sa.Table('task', meta,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('date', sa.Date),
                       sa.Column('title', sa.String),
                       sa.Column('source', sa.String),
                       sa.Column('description', sa.String),
                       #orm.RelationshipProperty('items', )
                       )
        orm.mapper(Task, tab, properties={
                   'items': orm.relationship(TaskItem, backref='task')
                   })

    def get(self, id):
        return self.db.query(Task).filter(Task.id == id)

    def get_list(self):
        return self.db.query(Task)

class RepoTaskItem(_Repo):
    def __init__(self, meta: sa.MetaData, session):
        super().__init__(session)
        #self.db = session

        tab = sa.Table('task_item', meta,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('task_id', sa.Integer, sa.ForeignKey('task.id')),
                       sa.Column('date', sa.Date),
                       sa.Column('title', sa.String),
                       sa.Column('solution', sa.String),
                       sa.Column('time_seconds', sa.Integer),
                       #orm.RelationshipProperty(Task, backref='items')
                       )
        orm.mapper(TaskItem, tab)

    def get(self, id):
        return self.db.query(TaskItem).filter(TaskItem.id == id)

    def get_list(self):
        return self.db.query(TaskItem)


class Db:
    def __init__(self, db_file):
        self.db_file = './db.sqlite3'

        # sl3.connect(db_file)

        meta = sa.MetaData()

        engine = sa.create_engine('sqlite:///'+self.db_file, pool_recycle=7200, echo=True)
        session = orm.sessionmaker(engine)()

        self.repoTask = RepoTask(meta, session)
        self.repoTaskItem = RepoTaskItem(meta, session)

        meta.create_all(engine)

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
