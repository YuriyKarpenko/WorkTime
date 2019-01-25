# from datetime import datetime, timedelta
from os import path
from tkinter.constants import *
from tkinter import filedialog as fd, simpledialog as sd, ttk, StringVar
from tkinter import Tk, Button, Menu, Text, Toplevel, Widget
from tkinter.ttk import Frame, Label

from ui import tk_helpers as tkh
from core.models import Task, TaskItem
from core.utils import datetime, timedelta, date_fromisoformat, trim
from core.controllers import optionController, taskController


def button(master, title, command, fg='black', side=LEFT, pad=5, w=10, **kw):
	""" https://younglinux.info/tkinter2/widget.php

	:param master:
	:param title:
	:param command:
	:param fg:
	:param side:
	:param pad:
	:param w:
	:param kw:
	:return:
	"""
	w = max(len(title), w)
	d = {'master': master, 'text': title, 'command': command, 'width': w}
	if Button.__module__ == 'tkinter':
		d = {**d, 'bg': 'lightgray', 'activebackground': '#888', 'activeforeground': fg, }
	b = Button(**{**d, **kw})
	b.pack(padx=pad, pady=pad, side=side)
	return b


def grid(w: Widget, row, col, colspan=1, rowspan=1, pad=5, **kw):
	d = {'row': row, 'column': col, 'columnspan': colspan, 'rowspan': rowspan, 'padx': pad, 'pady': pad, 'sticky': 'ensw'}
	w.grid(**{**d, **kw})
	return w


def from_taskItem(v: TaskItem, getText=None, getValues=None):
	defGetValue = lambda i: (i.date, i.title, i.solution)  # для редактирования задач
	return tkh.TreeViewItem(v, None, getText, getValues or defGetValue)


def from_task(v: Task):
	r = tkh.TreeViewItem(v, None, lambda i: i.title, lambda i: (i.date, i.description, i.time))
	r.childItems = tuple(from_taskItem(i, lambda i: i.title, lambda i: (i.date, i.solution, i.time)) for i in v.items)
	return r


class _DialogBase(sd.Dialog):

	def buttonbox(self):
		box = Frame(self)

		# Button(box, text="OK", width=10, command=self.ok, default=ACTIVE).pack(side=LEFT, padx=5, pady=5)
		# Button(box, text="Cancel", width=10, command=self.cancel).pack(side=LEFT, padx=5, pady=5)
		button(box, 'Ok', self.ok, 'green', default=ACTIVE)
		button(box, 'Cancel', self.cancel, 'red')

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def ok(self, event=None):
		if event:
			if isinstance(event.widget, Text): return
		# if not self.validate():
		#     self.initial_focus.focus_set() # put focus back
		#     return

		# self.withdraw()
		# self.update_idletasks()

		# try:
		#     self.apply()
		# finally:
		#     self.cancel()
		sd.Dialog.ok(self, event)


class Dialog_Option(_DialogBase):
	items_data = []
	sources: Text = None
	res = None

	def __init__(self, master):
		super(Dialog_Option, self).__init__(master, 'Настройки')

	def body(self, body):
		self.items_data.append(StringVar(self))

		r = 1
		grid(Label(body, text='Файл базы:'), r, 0)
		f2 = grid(Frame(body, width=2), r, 1)
		Button(f2, text='...', command=self.act_open_file).pack(side=RIGHT)
		ttk.Entry(f2, textvariable=self.items_data[0]).pack(expand=True, fill=BOTH, side=LEFT)
		r += 1
		grid(Label(body, text='Источники:'), r, 0)
		self.sources: Text = grid(Text(body, height=5, width=40), r, 1)
		r += 1

		self._init_data()

	def _init_data(self):
		v = optionController.get()
		self.items_data[0].set(v.db_path)
		self.sources.insert(1.0, v.sources)

	def apply(self):
		v = optionController.get()
		v.db_path = self.items_data[0].get()
		v.sources = self.sources.get(1.0, END).rstrip('\n')
		return optionController.save()

	def act_open_file(self):
		f_name = fd.askopenfilename(parent=self, filetypes=(("DB files", "*.db *.sqlite3"), ("JSON files", "*.json"), ("All files", "*.*")))
		if f_name:
			f_name = path.relpath(f_name)
			self.items_data[0].set(f_name)

	@staticmethod
	def show(parent):
		Dialog_Option(parent)
		return __class__.res


class Dialog_Task(_DialogBase):
	modal_result = None
	task: Task
	items_task: list
	items_taskItem: list
	items_task_tvh: tkh.TVHelper
	items_taskItem_text: Text

	def __init__(self, master, v: Task):
		self.task = v
		__class__.modal_result = None
		super(Dialog_Task, self).__init__(master, 'Задача')

	def body(self, f):
		# https://docs.python.org/3/library/tkinter.html
		self.items_task = [StringVar(self), StringVar(self), StringVar(self), StringVar(self)]
		self.items_taskItem = [StringVar(self), StringVar(self)]

		r = 1
		grid(Label(f, text='Дата:'), r, 0)
		grid(ttk.Entry(f, textvariable=self.items_task[0]), r, 1)
		r += 1
		grid(Label(f, text='Задача:'), r, 0)
		grid(ttk.Entry(f, textvariable=self.items_task[1]), r, 1)
		r += 1
		grid(Label(f, text='Источник:'), r, 0)
		grid(ttk.Combobox(f, values=optionController.get().sources, textvariable=self.items_task[2]), r, 1, padx=5, pady=5)
		r += 1
		grid(Label(f, text='Описание:'), r, 0)
		grid(ttk.Entry(f, textvariable=self.items_task[3]), r, 1)
		r += 1
		# TreeView
		grid(Label(f, text='Решения:'), r, 0)
		tv = ttk.Treeview(f, selectmode='browse', columns=range(4))
		grid(tv, r, 1)
		tvh = self.items_task_tvh = tkh.TVHelper(tv)
		ids = (1, 2, 3)
		tvh.add_col(ids[0], 'Дата', w=80)
		tvh.add_col(ids[1], 'Задача', w=100)
		tvh.add_col(ids[2], 'Решение', stretch=True)
		tvh.init_tv()
		tvh.cmd_on_select_item = self.act_select_item

		tv["displaycolumns"] = ids
		tv.column('#0', width=0)
		r += 1
		grid(ttk.Separator(f, orient=HORIZONTAL), r, 0, 2)
		##########################################################
		r += 1
		grid(Label(f, text='Решения:'), r, 0)
		f_bar = grid(Frame(f), r, 1)
		button(f_bar, 'Refresh', lambda: self.act_select_item(self.items_task_tvh.selected), w=5)
		button(f_bar, 'Add', self.act_add_item, w=5)
		button(f_bar, 'Save', self.act_save_item, w=5)
		r += 1
		grid(Label(f, text='Дата:'), r, 0)
		grid(ttk.Entry(f, textvariable=self.items_taskItem[0]), r, 1)
		r += 1
		grid(Label(f, text='Задача:'), r, 0)
		grid(ttk.Entry(f, textvariable=self.items_taskItem[1]), r, 1)
		r += 1
		grid(Label(f, text='Решение:'), r, 0)
		self.items_taskItem_text = Text(f, height=5, width=40, wrap=WORD)
		grid(self.items_taskItem_text, r, 1)
		r += 1

		self.load()

	def load(self):
		v = self.task
		if v:
			self.items_task[0].set(v.date)
			self.items_task[1].set(v.title)
			self.items_task[2].set(v.source)
			self.items_task[3].set(v.description)
			tvi = tuple(from_taskItem(i) for i in v.items)
			self.items_task_tvh.items_set(tvi)

	def validate(self):
		""" фиксация изменений"""
		v = self.task
		if v:
			v.date = date_fromisoformat(self.items_task[0].get())
			v.title = self.items_task[1].get()
			v.source = self.items_task[2].get()
			v.description = self.items_task[3].get()
			self.act_save_item()
			__class__.modal_result = v
		return v

	# TreeVpew ##########################################################

	def act_select_item(self, ti: tkh.TreeViewItem):
		""" заполнение полей формы  """
		self.items_taskItem_text.delete(0.0, END)
		if ti:
			self.items_taskItem[0].set(ti.item.date)
			self.items_taskItem[1].set(ti.item.title)
			self.items_taskItem_text.insert(1.0, ti.item.solution)

	def act_add_item(self):
		""" добавление решения в задачу """
		v = TaskItem(self.task)  # создать щиъект
		tvi = from_taskItem(v)  # обвернуть его

		self.task.items.append(v)  # добавить в данные
		self.items_task_tvh.items_add(tvi, True)  # добавить в UI + выделить добавленную запись

	def act_save_item(self):
		""" заполнение данных решения из полей формы"""
		if self.items_task_tvh.selected:
			v = self.items_task_tvh.selected.item
			v.date = date_fromisoformat(self.items_taskItem[0].get())
			v.title = self.items_taskItem[1].get()
			v.solution = self.items_taskItem_text.get(1.0, END).rstrip('\n')
			self.items_task_tvh.selected.update()

	@staticmethod
	def show(master: Widget, task: Task):
		Dialog_Task(master, task)
		return __class__.modal_result


class Dialog_Timer(sd.Dialog):
	_task: TaskItem
	_time_start: datetime
	_time_label: StringVar

	def __init__(self, master, task: TaskItem):
		self._task = task
		super(Dialog_Timer, self).__init__(master, task.title)

	def body(self, master):
		Label(master, text=self._task.solution).pack()
		Label(master, text='last: %s ' % (trim(self._task.time))).pack()
		self._time_label = StringVar(master)
		Label(master, textvariable=self._time_label).pack()
		self.time()

	def buttonbox(self):
		box = Frame(self)

		button(box, "OK", self.ok, 'green', default=ACTIVE)
		# Button(box, text="Cancel", width=10, command=self.cancel).pack(side=LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		# self.bind("<Escape>", self.cancel)

		box.pack()

	def time(self):
		t = datetime.now() - self._time_start
		self._time_label.set(str(trim(t)))
		self.after(1000, func=self.time)

	@staticmethod
	def show(master: Widget, task: TaskItem) -> timedelta:
		__class__._time_start = datetime.now()
		Dialog_Timer(master, task)
		return trim(datetime.now() - __class__._time_start)


class Main(Frame):
	# _colOptions = tuple({'width':200} * len(_columns))
	w_tree = None
	actions = {}
	tvh: tkh.TVHelper = None
	btn_time: Button

	def __init__(self, master):
		super(Main, self).__init__(master)
		# self.tk.eval('package require Tix')
		self.pack()

		self._init_menu()
		self._init_tree()
		self._init_data()

	def _init_menu(self):
		m = Menu()
		self.master.config(menu=m)

		m.add_command(label='Настройки', command=self.act_options)
		m.add_separator()

		m_task = Menu(m, tearoff=0)
		m_task.add_command(label='Создать', command=self.act_task_new)
		m_task.add_command(label='Изменить', command=self.act_task_edit)
		m.add_cascade(label='Задача', menu=m_task)
		m.add_separator()

		# TODO: не получается правильно создать кнопку меню
		# self.btn_time = Checkbutton(m, label='Start', command=self.timer)
		# m.add(self.btn_time)
		m.add_command(label='Start', command=self.timer)

	def _init_tree(self):
		""" https://docs.python.org/3/library/tkinter.ttk.html https://knowpapa.com/ttk-treeview/
		"""
		self.w_tree = tv = ttk.Treeview(self)
		tv.pack(fill=BOTH)
		self.tvh = tvh = tkh.TVHelper(tv)
		_columns = ('date', 'title', 'descr', 'time')
		tvh.add_col(_columns[0], 'Дата', None, 60)
		# tvh.add_col(_columns[1], 'Задача', None, w=100)
		tvh.add_col(_columns[2], 'Описание', w=300, stretch=True)
		tvh.add_col(_columns[3], 'Время', None, 60)
		tvh.init_tv()

	def _init_data(self):
		self.tvh.clear()
		data = taskController.get_list()
		tvi = tuple(from_task(d) for d in data)
		self.tvh.items_set(tvi)

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
			if t.id:
				taskController.refresh(t)
		self._init_data()

	def timer(self):
		t = self.tvh.selected
		if t and isinstance(t.item, TaskItem):
			delta = Dialog_Timer.show(self, t.item)
			t.item.time = trim(t.item.time + delta)
			t.update()  # обнонить UI
			taskController.update(t.item.task)  # обнонить базу
		else:
			self.bell()


class App:
	def __init__(self):
		self.tk = Tk()
		self.tk.title('Время работы')
		self.main = Main(self.tk)
		self._init_styles()

	@staticmethod
	def _init_styles():
		s = ttk.Style()
		s.configure('TCombobox', padding=0)

	def run(self):
		self.tk.mainloop()

