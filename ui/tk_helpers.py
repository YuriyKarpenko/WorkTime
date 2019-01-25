from tkinter.constants import *
from tkinter.ttk import Treeview


class TreeViewItem:
	def __init__(self, item, image, getText, getValues, childs: list = None):
		""" инкапсулирует методы для работы с элементами Treeview

		:param item: экземпляр ползовательсих данныз
		:param image: картинка узла
		:param getText: метод получения текста узла из пользовательских данных
		:param getValues: метод получения текста для колонок узла из пользовательских данных
		:param childs: дочерние элементы узла
		"""
		self.item = item
		self.iid = ''
		self.tv: Treeview = None  # установитс при заполнении Treeview

		self.image = image
		self.tags = None
		self._getText = getText
		self._getValues = getValues

		self.parent: TreeViewItem = None
		self.childItems = childs

	@property
	def text(self):
		a = self._getText
		return a and a(self.item) or ''

	@property
	def values(self):
		a = self._getValues
		return a and a(self.item)

	def insert_self(self, tv: Treeview, parent: str = ''):
		""" добавляет себя в новый узел Treeview + заполняет вои iid"""
		self.tv = tv
		self.iid = tv.insert(parent, END, tags=self.tags or (), text=self.text, values=self.values)
		if self.childItems:
			for c in self.childItems:
				c.parent = self
				c.insert_self(tv, self.iid)
		return self

	def update(self):
		self.tv.item(self.iid, text=self.text, values=self.values)

	def __repr__(self): return '%s: [%i], %s' % (self.iid, len(self.childItems) if self.childItems else 0, str(self.item))


class TVHelper:
	""" Помогает в настройке Treeview (https://infohost.nmt.edu/tcc/help/pubs/tkinter2/web/ttk-Treeview.html)
	"""

	def __init__(self, tv: Treeview):
		self._keys = {}  # справочник - средство получения уникальных ключей
		self._cols = {}
		self._heads = {}
		self.items = []
		self.tv = tv
		self.selected: TreeViewItem = None

	def col_key(self, key):
		key = key or len(self._keys)
		self._keys[key] = key
		r = tuple(self._keys.keys())
		return r

	def add_col(self, name, title='', image=None, w=200, stretch=False, command=None, anch=W, min_w=10):
		key = self.col_key(name)
		c = self._cols.get(key, {})
		self._cols[key] = c
		c['anchor'] = anch
		c['minwidth'] = min_w
		c['stretch'] = stretch
		c['width'] = w

		h = self._heads.get(key, {})
		self._heads[name] = h
		h['anchor'] = anch
		h['command'] = command
		h['image'] = image
		h['text'] = title

	def col(self, name=None, anch=W, stretch=True, min_w=10, w=200):
		key = self.col_key(name)
		c = self._cols.get(key, {})
		self._cols[key] = c
		c['anchor'] = anch
		c['minwidth'] = min_w
		c['stretch'] = stretch
		c['width'] = w
		return c

	def header(self, name=None, title: str = '', anch=W, image=None, command=None):
		key = self.col_key(name)
		h = self._heads.get(key, {})
		self._heads[name] = h
		h['anchor'] = anch
		h['command'] = command
		h['image'] = image
		h['text'] = title
		return h

	# def headers(self, keys: set, titles: list, anchs: list = None, images: list = None, commands: list = None):
	#     self._keys = keys
	#     self._heads.clear()
	#     for i in keys:
	#         d = {'anchor': anchs and anchs[i] or W, 'command': commands and commands[i], 'image': images and images[i], 'text': titles[i]}
	#         self._heads[i] = d
	#     return self._heads

	def init_tv(self, displaycolumns='#all', height=None, selectmode='browse'):
		tv = self.tv
		names = tuple(self._keys.keys())
		cc = self._cols
		hh = self._heads

		""" Последовательность строк идентификатора столбца. Эти строки используются внутри для идентификации столбцов в виджете.
			Столбец значков, идентификатор которого всегда равен «# 0», содержит значки свертывания/развертывания и всегда является первым столбцом.
			Столбцы, которые вы указываете с аргументом столбцов, являются дополнением к столбцу значка. """
		tv['columns'] = names
		# Список идентификаторов столбцов (символьных или целочисленных индексов), определяющих, какие столбцы данных отображаются и в каком порядке они отображаются, или строку «#all»
		tv['displaycolumns'] = displaycolumns
		tv['height'] = height  # Определяет количество строк, которые должны быть видны. Примечание: запрашиваемая ширина определяется из суммы значений ширины столбца.
		# tv['padding'] =  # Определяет внутренний отступ для виджета. Заполнение представляет собой список до четырех спецификаций длины
		# Управляет тем, как встроенные привязки классов управляют выбором. Допустимые значения “extended”, “browse” или “none”.
		# Если “extended” (по умолчанию), можно выбрать несколько элементов. Если “browse”, только один элемент будет выбран за один раз. If “none”, the selection will not be changed
		tv['selectmode'] = selectmode
		# tv['show'] = # Чтобы подавить метки в верхней части каждого столбца, укажите show = 'tree'. По умолчанию показываются метки столбцов.

		tv.bind('<<TreeviewSelect>>', self.act_select)
		tv.bind('<<TreeviewOpen>>', self.act_open)
		tv.bind('<<TreeviewClose>>', self.act_close)

		for col_id in names:
			c = cc.get(col_id)
			if c:
				tv.column(col_id, None, **c)
			h = hh.get(col_id)
			if h:
				tv.heading(col_id, **h)
		return tv

	# menage items

	def clear(self):
		if self.items:
			to_del = tuple(map(lambda i: i.iid, self.items))
			# print('clear()', 1, to_del)
		else:
			to_del = self.tv.get_children()
			# print('clear()', 2, to_del)

		self.items = None
		if to_del:
			self.tv.delete(*to_del)

	def items_add(self, tvi: TreeViewItem, set_selected: bool, parent_iid=''):
		""" добавление в elf.items + выделение в tv"""
		if tvi:
			self.items.append(tvi)
			if not tvi.iid:
				tvi.insert_self(self.tv, parent_iid)
			else:
				for i in tvi.childItems:
					self.items_add(i, set_selected, tvi.iid)

			if set_selected:
				self.selected = tvi
				self.select(tvi.iid)

	def items_set(self, items: tuple):
		""" утановка elf.items + замена значений tv """
		self.clear()
		self.items = list(items)
		for i in items:
			self.items_add(i, False)

	def _find_recusive(self, iid: str, src_items: list) -> TreeViewItem:
		if src_items:
			for i in src_items:
				if i.iid == iid:
					self.selected = i
					return i
				self.selected = self._find_recusive(iid, i.childItems)
				if self.selected: break  # return self.selected
		return self.selected

	def find_item(self, Id: str):
		self.selected = None
		if Id:
			return self._find_recusive(Id, self.items)

	def select(self, iid: str):
		""" выделение в tv"""
		if iid:
			self.tv.selection('set', (iid,))

	# оббаботчики событий Treeview

	cmd_on_close_item = None
	cmd_on_open_item = None
	cmd_on_select_item = None

	def act_close(self, *e):
		# print('act_close', e)
		return self.cmd_on_close_item and self.cmd_on_close_item()

	def act_open(self, *e):
		# print('act_open', e)
		return self.cmd_on_open_item and self.cmd_on_open_item()

	def act_select(self, *e):
		ii = self.tv.selection()
		# print('act_select', e, ii)
		i = self.find_item(ii[0])
		if self.cmd_on_select_item and i:
			self.cmd_on_select_item(i)
