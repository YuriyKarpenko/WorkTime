#!/usr/bin/python3
# -*- coding: utf-8 -*-

# from sys import argv
from tkinter import *
import tkinter.ttk as ttk
import models
from ui import *



class Main(Tk):
    # _colOptions = tuple({'width':200} * len(_columns))
    w_tree = None
    actions = {}

    def __init__(self):
        super(Main, self).__init__()
        # self.tk.eval('package require Tix')
        self.init()

    def init(self):
        self.title('Время работы')
        self.tvh: TVHelper = None
        self._init_menu()
        self.init_tree()

    def _init_menu(self):
        m = Menu()
        m.add_command(label='Настройки', command=self.act_options)

        m_task = Menu(m, tearoff=0)
        m_task.add_command(label='Создать', command=self.act_task_new)
        m.add_cascade(label='Задача', menu=m_task)

        self.config(menu=m)

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

        self.init_data()

    def init_data(self):
        data = taskController.get_list()
        tvi = (TVItem.from_taskItem(d) for d in data)
        self.tvh.fill_tv(tvi)

    def run(self):
        s = ttk.Style()
        s.configure('TCombobox', padding=-5)

        self.mainloop()

    def act_options(self, *e):
        WOption.show(self)

    def act_task_new(self):
        t = WTask.show(self, Task())

