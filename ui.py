from tkinter import *
from tkinter import filedialog as fd
import tkinter.ttk as ttk
from controllers import *


def button(master, title, command, fg='black', side=LEFT, pad=5, w=10, **kw):
    """ https://younglinux.info/tkinter/widget.php

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
    b = Button(master, **d)
    b.pack(padx=pad, pady=pad, side=side)
    return b


def grid(w: Widget, row, col, colspan=1, rowspan=1, pad=5, **kw):
    d = {'row': row, 'column': col, 'columnspan': colspan, 'rowspan': rowspan, 'padx': pad, 'pady': pad, 'sticky': 'ensw'}
    w.grid(**{**d, **kw})
    return w


class TVItem:
    def __init__(self, item, image, getText, getValues, childs: list = None):
        self.item = item
        self.iid = ''

        self.image = image
        self.tags = None
        self._getText = getText
        self._getValues = getValues

        self.childs = childs

    @property
    def text(self):
        a = self._getText
        return a and a(self.item) or ''

    @property
    def values(self):
        a = self._getValues
        return a and a(self.item)

    def insert(self, tv: ttk.Treeview, parent: str = ''):
        self.iid = tv.insert(parent, END, tags=self.tags or (), text=self.text, values=self.values)
        if self.childs:
            for c in self.childs:
                c.insert(tv, self.iid)
        return self

    @staticmethod
    def from_taskItem(v: TaskItem, getText=None, getValues=None):
        defGetValue = lambda i: (i.date, i.title, i.solution)  # для редактирования задач
        return TVItem(v, None, getText, getValues or defGetValue)

    @staticmethod
    def from_task(v: Task):
        r = TVItem(v, None, lambda i: i.title, lambda i: (i.date, i.description, i.time))
        r.childs = (TVItem.from_taskItem(i, lambda i: i.title, lambda i: (i.date, i.solution, i.time)) for i in v.items)
        return r


class TVHelper:
    """ Помогает в настройке Treeview (https://infohost.nmt.edu/tcc/help/pubs/tkinter/web/ttk-Treeview.html)
    """

    def __init__(self, tv: ttk.Treeview):
        self._keys = ()
        self._cols = {}
        self._heads = {}
        self.items = None
        self.tv = tv
        self.selected: TVItem = None

    def col_key(self, key):
        key = key or len(self._keys)
        self._keys += (key,)
        # self._keys = tuple(set(self._keys))   TODO: Надо бы создавать только уникальные ключи
        return key

    # def col_keys(self, *keys):
    #     self._keys = set(keys)

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
        names = tuple(self._keys)
        cc = self._cols
        hh = self._heads

        """ Последовательность строк идентификатора столбца. Эти строки используются внутри для идентификации столбцов в виджете. 
            Столбец значков, идентификатор которого всегда равен «# 0», содержит значки свертывания/развертывания и всегда является первым столбцом. Столбцы, которые вы указываете с аргументом столбцов, являются дополнением к столбцу значка. """
        tv['columns'] = names
        tv[
            'displaycolumns'] = displaycolumns  # Список идентификаторов столбцов (символьных или целочисленных индексов), определяющих, какие столбцы данных отображаются и в каком порядке они отображаются, или строку «#all»
        tv['height'] = height  # Определяет количество строк, которые должны быть видны. Примечание: запрашиваемая ширина определяется из суммы значений ширины столбца.
        # tv['padding'] =  # Определяет внутренний отступ для виджета. Заполнение представляет собой список до четырех спецификаций длины
        tv['selectmode'] = selectmode  # Управляет тем, как встроенные привязки классов управляют выбором. One of “extended”, “browse” or “none”. If set to “extended” (по умолчанию), можно выбрать несколько элементов. If “browse”, только один элемент будет выбран за один раз. If “none”, the selection will not be changed
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

    def fill_tv(self, items: list):
        self.items = items
        for i in items:
            i.insert(self.tv)

    def find_item(self, Id: str):
        print(Id)
        if self.items and Id:
            self.selected = next(i for i in self.items if i.iid == Id)
        else:
            self.selected = None
        return self.selected

    def update_item(self):
        s = self.selected
        if s:
            self.tv.item(s.iid, text=s.text, values=s.values)

    def act_close(self, *e):
        print(e)

    def act_open(self, *e):
        print(e)

    def act_select(self, *e):
        ii = self.tv.selection()
        if self.cmd_on_select_item and ii:
            i = self.find_item(ii[0])
            self.cmd_on_select_item(i)

    cmd_on_select_item = None


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
        button(self, 'Ok', self.act_ok, 'green', RIGHT)
        button(self, 'Cancel', self.act_cancel, 'red', RIGHT)
        self.pack(side='bottom', fill='x', expand=0)

    def act_cancel(self):
        if self.onCancel:
            self.onCancel()
        else:
            self.master.destroy()

    def act_ok(self):
        r = self.onOk and self.onOk()
        return r and self.act_cancel()


class WDialogBase(Toplevel):
    """ базовый класс дл диалоговых окон
    """

    def __init__(self, master):
        super(WDialogBase, self).__init__(master)

        self._list_controls = [WButtoms(self, self._act_ok, self._act_cancel)]
        self._init_controls()

    def _init_controls(self): pass

    def _act_cancel(self): self.destroy()

    def _act_ok(self): pass


class WOption(WDialogBase):
    _values: Optiopns

    # def __init__(self, parent):
    #    super(WOption, self).__init__(parent)
    #     self.transient(self.master)
    #     self.lift(self.master)

    def _init_controls(self):
        self.geometry('600x300')
        self.title('Настройки')
        self._init_()
        self._init_data()

    def _init_(self):
        self.items_data = [StringVar(self), ]
        # WButtoms(self, self.act_ok)
        f = Frame(self)
        f.pack(fill=BOTH)

        r = 1
        grid(Label(f, text='Файл базы:'), r, 0)
        f2 = grid(Frame(f, bd=1, width=2), r, 1)
        Button(f2, text='...', command=self.act_open_file).pack(side=RIGHT)
        ttk.Entry(f2, textvariable=self.items_data[0]).pack(expand=True, fill=BOTH, side=LEFT)
        r += 1
        grid(Label(f, text='Источники:'), r, 0)
        self.sources: Text = grid(Text(f, height=5, width=40), r, 1)
        r += 1

    def _init_data(self):
        v = optionController.get()
        self.items_data[0].set(v.db_path)
        sources = '\n'.join(v.sources)
        self.sources.insert(1.0, sources)

    def _act_ok(self):
        v = optionController.get()
        v.db_path = self.items_data[0].get()
        s = self.sources.get(1.0, END).rstrip('\n')
        v.sources = s.split('\n')
        return optionController.save()

    def act_open_file(self):
        f_name = fd.askopenfilename(parent=self, filetypes=(("JSON files", "*.json"), ("DB files", "*.db;*.sqlite3"), ("All files", "*.*")))
        if f_name:
            self.items_data[0].set(f_name)

    @staticmethod
    def show(parent):
        WOption(parent)


class WTask(WDialogBase):
    # __slots__ = ('value')

    def __init__(self, master, v: Task):
        super(WTask, self).__init__(master)
        self.geometry('500x600')
        self.title('Задача')
        self.task = v

        # https://docs.python.org/3/library/tkinter.html
        self.items_task = [StringVar(self), StringVar(self), StringVar(self)]
        self.items_taskItem = [StringVar(self), StringVar(self)]
        self.items_task_tvh = None

        # WButtoms(self, self.act_ok)
        f = Frame(self)
        f.pack(fill=BOTH)

        r = 1
        grid(Label(f, text='Дата:'), r, 0)
        grid(ttk.Entry(f, textvariable=self.items_task[0]), r, 1)
        r += 1
        grid(Label(f, text='Задача:'), r, 0)
        grid(ttk.Entry(f, textvariable=self.items_task[1]), r, 1)
        r += 1
        grid(Label(f, text='Источник:'), r, 0)
        # TODO: Combobox стрвнно растягивается - за окно ((
        grid(ttk.Combobox(f, values=db.options.sources, textvariable=self.items_task[2]), r, 1, padx=5, pady=5)
        r += 1
        grid(Label(f, text='Решения:'), r, 0)
        tv = ttk.Treeview(f, selectmode='browse', columns=range(4))
        tvh = self.items_task_tvh = TVHelper(tv)
        ids = (1, 2, 3)
        tvh.add_col(ids[0], 'Дата', w=80)
        tvh.add_col(ids[1], 'Задача', w=100)
        tvh.add_col(ids[2], 'Решение', stretch=True)
        tvh.init_tv()
        tvh.cmd_on_select_item = self.act_select_item

        tv["displaycolumns"] = ids
        tv.column('#0', width=0)
        self.items_w_tv = grid(tv, r, 1)
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
            tvi = list(TVItem.from_taskItem(i) for i in v.items)
            self.items_task_tvh.fill_tv(tvi)

    def _act_ok(self):
        v = self.task
        if v:
            v.date = date_fromisoformat(self.items_task[0].get())
            v.title = self.items_task[1].get()
            v.source = self.items_task[2].get()
            self.act_save_item()
            if not v.id:
                taskController.insert(v)
            taskController.save()
        return v

    # TreeVpew ##########################################################

    def act_select_item(self, ti: TVItem):
        self.items_taskItem_text.delete(1.0, END)
        if ti:
            self.items_taskItem[0].set(ti.item.date)
            self.items_taskItem[1].set(ti.item.title)
            self.items_taskItem_text.insert(1.0, ti.item.solution)

    def act_add_item(self):
        v = TaskItem()
        self.task.items.append(v)
        tvi = TVItem.from_taskItem(v)
        tvi.insert(self.items_task_tvh.tv)
        self.act_select_item(tvi)

    def act_save_item(self):
        if self.items_task_tvh.selected:
            v = self.items_task_tvh.selected.item
            v.date = date_fromisoformat(self.items_taskItem[0].get())
            v.title = self.items_taskItem[1].get()
            v.solution = self.items_taskItem_text.get(1.0, END).rstrip('\n')
            self.items_task_tvh.update_item()

    @staticmethod
    def show(master: Widget, task: Task):
        WTask(master, task)
