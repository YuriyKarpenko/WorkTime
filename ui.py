from datetime import datetime, timedelta
from os import path
from tkinter import *
from tkinter import filedialog as fd
import tkinter.ttk as ttk
import tk_helpers as tkh
from models import date_fromisoformat, Task, TaskItem
from controllers import optionController
import tkinter.simpledialog as sd


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
	d = {'text': title, 'command': command, 'width': w, 'bg': 'lightgray', 'activebackground': '#888', 'activeforeground': fg}
	b = Button(master, {**d, **kw})
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
	r = tkh.TreeViewItem(v, None, lambda i: i.title, lambda i: (i.date, i.description, i.title))
	r.childItems = tuple(from_taskItem(i, lambda i: i.title, lambda i: (i.date, i.solution, i.time)) for i in v.items)
	return r


class WButtoms(Frame):
	def __init__(self, master: Toplevel, onOk, onCancel=None):
		""" отображает нижние кнопки в диалоговом окне

		:param master: диалоговое окно
		:param onOk: метод нажатия кнопки (если вернет , то вызывается метод act_cancel() для закрытия окна
		:param onCancel: метод нажатия кнопки "Отмена", по умолчанию просто уничтожает диалоговое окно
		"""
		super(WButtoms, self).__init__(master)
		self.onCancel = onCancel
		self.onOk = onOk
		self.btnOk = button(self, 'Ok', self.act_ok, 'green', RIGHT)
		self.btnCancel = button(self, 'Cancel', self.act_cancel, 'red', RIGHT)
		self.pack(side='bottom', fill='x', expand=0)

	def act_cancel(self):
		if self.onCancel:
			self.onCancel()
		else:
			self.master.destroy()

	def act_ok(self):
		r = self.onOk and self.onOk()
		return r and self.act_cancel()


class Dialog_Option(sd.Dialog):
	items_data = []
	sources: Text = None
	res = None

	def __init__(self, master):
		super(Dialog_Option, self).__init__(master, 'Настройки')

	def body(self, body):
		self.items_data.append(StringVar(self))

		r = 1
		grid(Label(body, text='Файл базы:'), r, 0)
		f2 = grid(Frame(body, bd=1, width=2), r, 1)
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


class Dialog_Task(sd.Dialog):
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
		# TODO: Combobox стрвнно растягивается - за окно ((
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
			tvi = list(from_taskItem(i) for i in v.items)
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
		v = TaskItem(self.task) # создать щиъект
		tvi = from_taskItem(v) # обвернуть его

		self.task.items.append(v) # добавить в данные
		self.items_task_tvh.items_add(tvi, True) # добавить в UI

		# TODO: надо выделять новую запись в списке
		# self.items_task_tvh.select(tvi.iid)
		# self.act_select_item(tvi)

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
	_time: timedelta
	_time_start: datetime
	_time_label: Label

	def __init__(self, master, task: TaskItem):
		self._task = task
		self._time = task.time
		super(Dialog_Timer, self).__init__(master)

	def body(self, master):
		self._time_label = Label(master)

	def apply(self):
		self._task.time = self._time

	@staticmethod
	def show(master: Widget, task: TaskItem) -> timedelta:
		__class__._time_start = datetime.now()
		Dialog_Timer(master, task)
		return datetime.now() - __class__._time_start
