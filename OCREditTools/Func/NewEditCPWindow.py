# -*- coding:utf-8 -*-

from tkinter import ttk


class NewWindow:
    def __init__(self, win, title, message):
        self.str = ""
        self.message = message
        self.win = win
        self.win.title = title

    def widget(self):
        self.win.resizable(0, 0)
        self.win.geometry("300x100")
        self.lable = ttk.Label(self.win, text=self.message)
        self.lable.grid(column=0, row=0, pady=20, padx=5)
        self.entry = ttk.Entry(self.win)
        self.entry.grid(column=1, row=0, pady=20)
        self.entry.bind("<Return>", self.event_get_entry)
        self.button = ttk.Button(self.win, text="OK", width=8, command=self.get_entry)
        self.button.grid(column=0, row=1)
        button_cancel = ttk.Button(self.win, text="Cancel", width=8, command=self.cancel)
        button_cancel.grid(column=1, row=1)

    def event_get_entry(self, event):
        self.get_entry()

    def get_entry(self):
        self.str = self.entry.get()
        self.win.destroy()

    def cancel(self):
        self.win.destroy()


