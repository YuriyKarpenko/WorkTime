#!/usr/bin/python3
# -*- coding: utf-8 -*-

# from sys import argv
from tk_helpers import *
import tkinter.ttk as ttk
from controllers import *
from ui import *  # Dialog_Option, Dialog_Task, Dialog_Timer


class Main(Tk):
	# _colOptions = tuple({'width':200} * len(_columns))
	w_tree = None
	actions = {}
	tvh: TVHelper = None
	btn_time: Button

	def __init__(self):
		super(Main, self).__init__()
		# self.tk.eval('package require Tix')
		self.init()

	def init(self):
		self.title('Время работы')
		self._init_menu()
		self.init_tree()
		self.init_data()

	def _init_menu(self):
		m = Menu()
		self.config(menu=m)

		m.add_command(label='Настройки', command=self.act_options)
		m.add_separator()

		m_task = Menu(m, tearoff=0)
		m_task.add_command(label='Создать', command=self.act_task_new)
		m_task.add_command(label='Изменить', command=self.act_task_edit)
		m.add_cascade(label='Задача', menu=m_task)
		m.add_separator()

		m.add_command(label='Start', command=self.timer)

	# TODO: не получается правильно создать кнопку меню
	# self.btn_time = Checkbutton(m, label='Start', command=self.timer)
	# m.add(self.btn_time)

	def init_tree(self):
		""" https://docs.python.org/3/library/tkinter.ttk.html https://knowpapa.com/ttk-treeview/
		"""
		self.w_tree = tv = ttk.Treeview(self)
		tv.pack(fill=BOTH)
		self.tvh = tvh = TVHelper(tv)
		_columns = ('date', 'title', 'descr', 'time')
		tvh.add_col(_columns[0], 'Дата', None, 60)
		# tvh.add_col(_columns[1], 'Задача', None, w=100)
		tvh.add_col(_columns[2], 'Описание', w=300, stretch=True)
		tvh.add_col(_columns[3], 'Время', None, 60)
		tvh.init_tv()

	def init_data(self):
		self.tvh.clear()
		data = taskController.get_list()
		tvi = list(from_task(d) for d in data)
		self.tvh.fill_tv(tvi)

	def run(self):
		s = ttk.Style()
		s.configure('TCombobox', padding=-5)

		self.mainloop()

	def act_options(self):
		Dialog_Option.show(self)

	def act_task_new(self):
		self.act_task(Task())

	def act_task_edit(self):
		t = self.tvh.selected
		while t and isinstance(t.item, TaskItem):
			t = t.parent

		if t:
			self.act_task(t.item)
		else:
			self.bell()

	def act_task(self, t: Task):
		t = taskController.get(t.id) or t
		v = Dialog_Task.show(self, t)
		if v:
			if v.id:
				taskController.update(v)
			else:
				taskController.insert(v)
		else:
			taskController.refresh(t)
		self.init_data()

	def timer(self):
		t = self.tvh.selected
		if t and isinstance(t.item, TaskItem):
			delta = Dialog_Timer.show(self, t.item)
			t.item.time += delta
			taskController.update(t.item.task)
		else:
			self.bell()
