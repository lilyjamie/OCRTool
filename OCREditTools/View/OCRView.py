# -*- coding:utf-8 -*-
import tkinter as tk
from tkinter.filedialog import *
from tkinter import ttk
from tkinter import scrolledtext


class OCREditTool:
    def __init__(self, win):
        """OCREditTool类.
        UI of OCRTool.
        Args:
            win(window):接收一个活动窗口
        """

        self.window = win
        self.window.title("OCREditTool")
        vscrollbar = tk.Scrollbar(self.window)
        canvas = tk.Canvas(self.window, height=630, width=735, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=canvas.yview)
        vscrollbar.grid(column=1, row=0, sticky="NS")
        self.base_frame = LabelFrame(canvas)
        canvas.grid(column=0, row=0, sticky="wns")
        canvas.create_window(0, 0, window=self.base_frame, anchor="nw")
        self.file_frame = ttk.LabelFrame(self.base_frame, text="file")
        self.open_button = ttk.Button(self.file_frame, text="open file")
        self.open_button.grid(column=0, row=0, sticky="W")
        # 新建Entry获取打开的文件名
        self.file_name = tk.StringVar()
        self.file_entry = Entry(self.file_frame, textvariable=self.file_name, width=20)
        self.file_entry.grid(column=1, row=0, sticky="W")
        self.file_frame.grid(column=0, row=0, sticky=W)

        self.origin_checkpoint_frame = ttk.LabelFrame(self.base_frame, text="checkpoint key value")
        up_frame = LabelFrame(self.origin_checkpoint_frame, text="choose checkpoint")
        up_frame.grid(column=0, row=0, padx=10, pady=10, sticky="WN")
        self.cp_list_value = tk.StringVar()
        self.key_cp = tk.Listbox(up_frame, listvariable=self.cp_list_value, width=35,
                                 selectmode="browse", exportselection=False)
        self.key_cp.grid(column=0, columnspan=3)

        scr_y = tk.Scrollbar(up_frame)
        self.key_cp.configure(yscrollcommand=scr_y.set)
        scr_y["command"] = self.key_cp.yview()
        scr_y.grid(row=0, column=4)

        scr_x = tk.Scrollbar(up_frame, orient="horizontal")
        self.key_cp.configure(xscrollcommand=scr_x.set)
        scr_x["command"] = self.key_cp.yview()
        scr_x.grid(row=1, columnspan=3, column=0)

        self.add_button = ttk.Button(up_frame, text="Add")
        self.add_button.grid(column=0, row=2, sticky="W")
        self.rename_button = ttk.Button(up_frame, text="Rename")
        self.rename_button.grid(column=1, row=2)
        self.delete_button = ttk.Button(up_frame, text="Delete")
        self.delete_button.grid(column=2, row=2, sticky="W")
        self.origin_checkpoint_frame.grid(column=1, columnspan=2, row=0)

        self.cp_edit_frame = ttk.LabelFrame(self.base_frame, text="edit choice")
        edit_frame = ttk.LabelFrame(self.cp_edit_frame)

        # edit point
        ttk.Label(edit_frame, text="x1y1_x2y2").grid(column=0, row=0, sticky="W")
        point_value = tk.StringVar()
        self.point_entry = ttk.Entry(edit_frame, textvariable=point_value)
        self.point_entry.grid(column=1, row=0, sticky="W")
        self.camera_picture_button = ttk.Button(edit_frame, text="Capture Picture")
        self.camera_picture_button.grid(column=2, row=0, sticky="W")
        self.re_choose_camera_button = ttk.Button(edit_frame, text="ReChoose Cam_port")
        self.re_choose_camera_button.grid(column=3, row=0, sticky="W")
        self.choose_picture_button = ttk.Button(edit_frame, text="choose picture")
        self.choose_picture_button.grid(column=4, row=0, sticky="W")

        # target_text
        ttk.Label(edit_frame, text="target_text").grid(column=0, row=1, sticky="W")
        self.target_text = scrolledtext.ScrolledText(edit_frame, height=5, wrap=tk.WORD)
        self.target_text.grid(column=1, row=1, columnspan=4, sticky="EW")

        # edit img filter
        filter_label = ttk.Label(edit_frame, text="img_filter:")
        filter_label.grid(column=0, row=2, sticky="W")
        key_value = tk.StringVar()
        self.filter_combox = ttk.Combobox(edit_frame, width=12, textvariable=key_value, state="readonly")
        self.filter_combox["values"] = ("auto", "gray", "binary", "binary-inv")
        self.filter_combox.grid(column=1, row=2, sticky="W")

        # max_check_count
        ttk.Label(edit_frame, text="max_check_count").grid(column=0, row=3, sticky="W")
        count_value = tk.IntVar()
        self.count_entry = ttk.Entry(edit_frame, textvariable=count_value)
        self.count_entry.grid(column=1, row=3, sticky="W")

        # lang
        ttk.Label(edit_frame, text="lang").grid(column=0, row=4, sticky="W")
        lang_value = tk.StringVar()
        self.lang_entry = ttk.Entry(edit_frame, textvariable=lang_value)
        self.lang_entry.grid(column=1, row=4, sticky="W")

        # nice
        ttk.Label(edit_frame, text="nice").grid(column=0, row=5, sticky="W")
        nice_value = tk.StringVar()
        self.nice_entry = ttk.Entry(edit_frame, textvariable=nice_value)
        self.nice_entry.grid(column=1, row=5, sticky="W")

        # text_compare_method
        ttk.Label(edit_frame, text="text_compare_method").grid(column=0, row=6, sticky="W")
        text_compare_method_value = tk.StringVar()
        text_compare_method_value.set(("br2auto-sp", "br2sp", "no-br", "no-sp", "substr", "regular"))
        self.cmp_method_index = {"br2auto-sp": 0, "br2sp": 1, "no-br": 2, "no-sp": 3, "substr": 4, "regular": 5}
        self.text_cmp_method_listbox = Listbox(edit_frame, listvariable=text_compare_method_value,
                                               height=7, selectmode=tk.MULTIPLE, exportselection=False)
        self.text_cmp_method_listbox.grid(column=1, row=6, sticky="W")

        # inherit
        ttk.Label(edit_frame, text="inherit").grid(column=0, row=7, sticky="W")
        inherit_value = tk.StringVar()
        self.inherit_entry = ttk.Entry(edit_frame, textvariable=inherit_value)
        self.inherit_entry.grid(column=1, row=7, sticky="W")

        # config
        ttk.Label(edit_frame, text="config").grid(column=0, row=8, sticky="W")
        self.config_var = StringVar()
        self.config_box = ttk.Combobox(edit_frame, textvariable=self.config_var, state="readonly")
        self.config_box['value'] = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13")
        self.config_box.grid(column=1, row=8, sticky="W")

        self.check_button = ttk.Button(edit_frame, text="Check Config In Picture")
        self.check_button.grid(column=0, row=9, sticky="W")
        self.check_text = scrolledtext.ScrolledText(edit_frame, height=5, wrap=tk.WORD)
        self.check_text.grid(column=1, row=9, columnspan=4, sticky="W")
        self.save_button = Button(edit_frame,fg="red", text="Save Config", width=20)
        self.save_button.grid(column=1, row=10)
        edit_frame.grid(column=0, row=0, columnspan=3)
        self.cp_edit_frame.grid(column=0, row=1, pady=28, columnspan=3)

        self.window.update()
        canvas.config(scrollregion=canvas.bbox("all"))

    def update(self, subject):
        self.checkpoint_dict = subject.file_dict
        self.key_list = tuple(self.checkpoint_dict.keys())
        self.cp_list_value.set(self.key_list)
