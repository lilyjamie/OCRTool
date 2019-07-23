from tkinter.filedialog import *
from tkinter import messagebox
from collections import OrderedDict
import tkinter as tk
import json

from OCREditTools.View.OCRView import OCREditTool
from OCREditTools.Func.FiledictObserver import *
from OCREditTools.Func.NewEditCPWindow import NewWindow
from OCREditTools.Func.NewAutoPointWindow import CaptureWindow
from OCREditTools.PicturePoint.GetCameraPicture import CameraPicture
from OCREditTools.PicturePoint.GetPoint import DrawPoint
from OCREditTools.Func.PicturePathObserver import PicturePathObserver
from TVHybridTestLibrary.drivers.usbcapturehdmi import VideoCaptureBase
from OCREditTools.OCRCheck.ocrCheck import OCRCheck


class Control:
    def __init__(self, win):
        self.win = win
        self.origin_file_dict = {}
        # text_compare_method
        self.text_compare_method = ("br2auto-sp", "br2sp", "no-br", "no-sp", "substr", "regular")
        # text_compare_method 冲突表
        self.conflict_table = [["substr", "regular"]]
        # 保存select_index
        self.select_method_index = []

        # 默认输入照相机端口的输入值
        self.camera_port = 999
        # 创建观察者
        self.file_watch = File({})
        self.picture_path_watch = PicturePathObserver("")
        self.ocr = OCREditTool(self.win)
        self.frame = VideoCaptureBase.instance(0)
        self.picture_path_watch.attach(self.frame)
        self.picture_path = ""
        # 添加文件字典被观察者
        self.file_watch.attach(self.ocr)
        self.filter_combobox_get_value()
        self.ocr.open_button.bind("<Button-1>", self.open)
        self.ocr.add_button.bind("<Button-1>", self.add)
        self.ocr.rename_button.bind("<Button-1>", self.rename)
        self.ocr.delete_button.bind("<Button-1>", self.delete)
        self.ocr.key_cp.bind("<<ListboxSelect>>", self.send_cp_value_to_edit_event)
        self.ocr.save_button.bind("<Button-1>", self.save_edit)
        self.ocr.camera_picture_button.bind("<Button-1>", self.auto_camera_capture_point)
        self.ocr.re_choose_camera_button.bind("<Button-1>", self.reinput_auto_camera_capture)
        self.ocr.choose_picture_button.bind("<Button-1>", self.choose_picture_get_point)
        self.ocr.check_button.bind("<Button-1>", self.ocr_check)
        self.ocr.text_cmp_method_listbox.bind("<<ListboxSelect>>", self.judge_conflict)
        self.win.mainloop()

    def filter_combobox_get_value(self):
        self.filter_index = OrderedDict()
        self.filter_index["auto"] = 0
        self.filter_index["gray"] = 1
        self.filter_index["binary"] = 2
        self.filter_index["binary-inv"] = 3
        self.filter_index[""] = 4
        self.ocr.filter_combox["values"] = tuple(self.filter_index.keys())

    def open(self, events):
        ''' 打开文件
        打开文件后列表获取json文件key值，并且存取整个文件内容
        Args: None
        '''

        file_types = [
            ("Json Files", "*.json", 'TEXT')]
        file_obj = askopenfile(filetypes=file_types)
        if file_obj:
            self.ocr.file_entry.delete(0, END)
            self.ocr.file_entry.insert(0, file_obj.name)
            with open(file_obj.name, "r") as f:
                # 获取整个json文件为有序字典
                self.origin_file_dict = json.load(f, object_pairs_hook=OrderedDict)
                # 触发更新事件
                self.file_watch.file_dict = self.origin_file_dict

    # 定位到checkpoint最后一个位置
    def listbox_select_end(self):
        size = self.ocr.key_cp.size()
        indexs = self.ocr.key_cp.curselection()
        if indexs:
            cur_index = indexs[0]
            self.ocr.key_cp.select_clear(cur_index)
        self.ocr.key_cp.select_set(size-1)

    def add(self, events):
        self.checkpoint_name = ''
        self.new_window = Tk()
        self.add_window = NewWindow(self.new_window, "add checkpoint", "checkpoint name")
        self.add_window.widget()
        self.add_window.button.bind("<Destroy>", self.handle_add_window_return)

    def handle_add_window_return(self, event):
        self.checkpoint_name = self.add_window.str
        # 如果返回checkpoint name,则新增checkpoint
        if self.checkpoint_name:
            if self.checkpoint_name in self.file_watch.file_dict.keys():
                messagebox.showerror("error", "checkpoint name already exits")
            else:
                value = {
                    "x1y1_x2y2": [20, 50, 280, 130],
                    }
                self.file_watch.add(self.checkpoint_name, value)
                self.save()
                self.listbox_select_end()
                self.send_cp_value_to_edit()

    def rename(self, events):
        cur_indexs = self.ocr.key_cp.curselection()
        if cur_indexs:
            self.cur_index = int(cur_indexs[0])
            self.origin_checkpoint = self.ocr.key_list[self.cur_index]
            self.checkpoint_name = ''
            self.new_window = Tk()
            self.rename_window = NewWindow(self.new_window, "rename checkpoint", " new checkpoint name")
            self.rename_window.widget()
            self.rename_window.button.bind("<Destroy>", self.handle_rename_window_return)
        else:
            messagebox.showerror("error", "no select item")

    def handle_rename_window_return(self, event):
        self.checkpoint_name = self.rename_window.str
        # 如果返回checkpoint name,则新增checkpoint
        if self.checkpoint_name:
            if self.checkpoint_name in self.file_watch.file_dict.keys():
                messagebox.showerror("error", "cp name already exist")
            else:
                # 新增checkpointname内容和之前一样
                self.file_watch.change_key(self.origin_checkpoint, self.checkpoint_name)
                self.save()
                self.listbox_select_end()
                self.send_cp_value_to_edit()

    def delete(self, events):
        cur_indexs = self.ocr.key_cp.curselection()
        if cur_indexs:
            cur_index = int(cur_indexs[0])
            origin_checkpoint = self.ocr.key_list[cur_index]
            self.file_watch.delete(origin_checkpoint)
            self.save()
            self.clear_widget()
        else:
            messagebox.showerror("error", "no select item")

    def send_cp_value_to_edit_event(self, events):
        self.send_cp_value_to_edit()

    def send_cp_value_to_edit(self):
        cur_indexs = self.ocr.key_cp.curselection()
        if cur_indexs:
            cur_index = int(cur_indexs[0])
            self.choose_checkpoint = self.ocr.key_list[cur_index]
            self.edit_frame_widget_get_origin_value(self.file_watch.file_dict, self.choose_checkpoint)

    # 清空控件值
    def clear_widget(self):
        self.ocr.point_entry.delete(0, END)
        self.ocr.target_text.delete("1.0", END)
        # 选择为空项
        self.ocr.filter_combox.current(4)
        self.ocr.count_entry.delete(0, END)
        self.ocr.lang_entry.delete(0, END)
        self.ocr.nice_entry.delete(0, END)
        indexs = self.ocr.text_cmp_method_listbox.curselection()
        if indexs:
            for index in indexs:
                self.ocr.text_cmp_method_listbox.select_clear(index)
        self.ocr.inherit_entry.delete(0, END)
        self.ocr.config_box.delete(0, END)
        self.ocr.check_text.delete("1.0", END)
        self.ocr.check_text.configure(background="white")

    # 获取值
    def edit_frame_widget_get_origin_value(self, file_dict, cur_cp_name):
        text_compare_method_value = tk.StringVar()
        text_compare_method_value.set(self.text_compare_method)
        index = 0
        cmp_method_index = {}
        for text_method in self.text_compare_method:
            cmp_method_index[text_method] = index
            index += 1
        self.ocr.text_cmp_method_listbox.config(listvariable=text_compare_method_value)
        self.clear_widget()
        self.file_dict = file_dict
        self.cur_cp_name = cur_cp_name
        self.origin_cp_value_dict = {}
        self.origin_cp_value_dict = self.file_dict[cur_cp_name]

        for key in self.origin_cp_value_dict:
            if key == "x1y1_x2y2":
                self.ocr.point_entry.insert(0, str(self.origin_cp_value_dict[key]))
            elif key == "target_text":
                self.ocr.target_text.insert("1.0", self.origin_cp_value_dict[key])
            elif key == "img_filter":
                img_filter = self.origin_cp_value_dict[key]
                self.ocr.filter_combox.current(self.filter_index[img_filter])
            elif key == "max_check_count":
                self.ocr.count_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "lang":
                self.ocr.lang_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "nice":
                self.ocr.nice_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "text_compare_method":
                text_method = re.split("\|", self.origin_cp_value_dict[key])
                for method in text_method:
                    self.ocr.text_cmp_method_listbox.select_set(cmp_method_index[method])
            elif key == "inherit":
                self.ocr.inherit_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "config":
                config = self.origin_cp_value_dict[key].strip()
                self.ocr.config_box.insert(0, config)
            else:
                messagebox.showerror("key error", key + " no exist")

    def new_edit_cp_dict(self):
        self.cp_value_dict = {}
        point = self.ocr.point_entry.get()
        self.cp_value_dict["x1y1_x2y2"] = eval(point)
        text = self.ocr.target_text.get("1.0", END)
        text_without_br = text.replace("\n", "")
        if text_without_br:
            self.cp_value_dict["target_text"] = self.ocr.target_text.get("1.0", END)[:-1]
        if self.ocr.filter_combox.get():
            self.cp_value_dict["img_filter"] = self.ocr.filter_combox.get()
        if self.ocr.count_entry.get():
            self.cp_value_dict["max_check_count"] = int(self.ocr.count_entry.get())
        if self.ocr.lang_entry.get():
            self.cp_value_dict["lang"] = self.ocr.lang_entry.get()
        if self.ocr.nice_entry.get():
            self.cp_value_dict["nice"] = self.ocr.nice_entry.get()
        if self.ocr.config_box.get():
            self.cp_value_dict["config"] = self.ocr.config_box.get()

        method_indexs = self.ocr.text_cmp_method_listbox.curselection()
        str_temp = ""
        if method_indexs:
            for i in method_indexs:
                if i == len(method_indexs) - 1:
                    str_temp = str_temp + self.ocr.text_cmp_method_listbox.get(i)
                else:
                    str_temp = str_temp + self.ocr.text_cmp_method_listbox.get(i) + "|"

            self.cp_value_dict["text_compare_method"] = str_temp

        if self.ocr.inherit_entry.get():
            self.cp_value_dict["inherit"] = self.ocr.inherit_entry.get()

    def judge_conflict(self, event):
        if not self.select_method_index:
            select_indexs = self.ocr.text_cmp_method_listbox.curselection()
            self.select_method_index = list(select_indexs)
        else:
            select_indexs = self.ocr.text_cmp_method_listbox.curselection()
            # 求出不同的那一项
            diff_list = list(set(select_indexs).difference(set(self.select_method_index)))
            self.select_method_index = list(select_indexs)

        select_values = [None]*len(self.text_compare_method)
        if select_indexs:
            for index in select_indexs:
                select_values.append(self.ocr.text_cmp_method_listbox.get(index))
            for i in range(len(self.conflict_table)):
                if self.conflict_table[i][0] in select_values and self.conflict_table[i][1] in select_values:
                    messagebox.showerror("error", "conflict with previous method")
                    self.ocr.text_cmp_method_listbox.select_clear(diff_list[0])
                    break

    def save_edit(self, events):
        ret = self.control_button_click()
        if ret:
            self.new_edit_cp_dict()
            self.file_watch.change_value(self.choose_checkpoint, self.cp_value_dict)
            self.save()
        else:
            messagebox.showerror("error", "no select checkpoint")

    def save(self):
        value = self.ocr.file_entry.get().strip()
        if value:
            json_str = json.dumps(self.file_watch.file_dict, indent=4)
            with open(value, "w") as json_file:
                json_file.write(json_str)
        else:
            self.save_as()

    def save_as(self):
        file_types = [
            ("Json Files", "*.json", 'TEXT')]
        json_str = json.dumps(self.file_watch.file_dict, indent=4)
        if json_str:
            f_obj = asksaveasfile(filetypes=file_types)
            if f_obj:
                f_obj.write(json_str)
                self.ocr.file_entry.insert(0, f_obj.name)

    def new_camera_window(self):
        self.picture_win = Tk()
        self.edit_point = CaptureWindow(self.picture_win)
        self.edit_point.capture_widget()
        self.edit_point.port_entry.bind("<Destroy>", self.get_camera_port)

    def auto_camera_capture_point(self, events):
        ret = self.control_button_click()
        if ret:
            if self.camera_port == 999:
                self.new_camera_window()
            else:
                self.camera_get_point(self.camera_port)
        else:
            messagebox.showerror("error", "no select checkpoint")

    def reinput_auto_camera_capture(self, events):
        ret = self.control_button_click()
        if ret:
            if self.ocr.re_choose_camera_button.instate(['!disabled']):
                self.new_camera_window()
            else:
                messagebox.showinfo("info", "this is a button to reinput camera port, "
                                            "please press Cam button first")
        else:
            messagebox.showerror("error", "no select checkpoint")

    def get_camera_port(self, events):
        # 获取是否有打开填写过camera
        self.camera_port = self.edit_point.port
        if self.edit_point.port == 999:
            pass
        else:
            self.ocr.re_choose_camera_button.state(['!disabled'])
            self.camera_get_point(self.edit_point.port)

    def choose_picture_get_point(self, events):
        """choose_picture_get_point.
        打开图片，获取图片坐标.
        """
        ret = self.control_button_click()
        if ret:
            file_types = [
                ("JPG", "*.jpg"), ("JPEG", "*.jpeg")]
            file_obj = askopenfile(filetypes=file_types)
            if file_obj:
                self.picture_path = file_obj.name
                self.picture_path_watch.picture_path = self.picture_path
                DrawPoint(self.ocr.picture_canvas, self.ocr.point_entry, self.picture_path)
        else:
            messagebox.showerror("error", "no select checkpoint")

    # 获取图片坐标
    def camera_get_point(self, picture_path):
        camera = CameraPicture(picture_path)
        self.picture_path = camera.get_camera()
        if self.picture_path:
            self.picture_path_watch.picture_path = self.picture_path
            DrawPoint(self.ocr.picture_canvas, self.ocr.point_entry, self.picture_path)
        else:
            choose = messagebox.askokcancel("choose", "camera port no exist, reinput or not?")
            if choose:
                self.new_camera_window()

    def ocr_check(self, events):
        ret = self.control_button_click()
        load_picture_flag = self.check_button_click_state()
        if ret:
            if load_picture_flag:
                self.ocr.check_text.delete("1.0", END)
                self.ocr.check_text.configure(background="white")
                self.new_edit_cp_dict()
                if self.picture_path:
                    self.ocr_compare()
            else:
                messagebox.showerror("error", "no capture or choose picture")
        else:
            messagebox.showerror("error", "no select checkpoint")

    def ocr_compare(self):
        ocr_check = OCRCheck()
        ocr_check.create_checkpoint(self.choose_checkpoint, self.cp_value_dict)
        ret, ratio = ocr_check.ocr_checkpoint(self.choose_checkpoint)
        self.ocr.check_text.delete("1.0", END)
        self.ocr.check_text.insert("1.0", ocr_check.ocr_checkpoint_text(self.choose_checkpoint))
        if ret:
            self.ocr.check_text.configure(background="green")
        else:
            self.ocr.check_text.configure(backgroun="red")

    def check_button_click_state(self):
        if self.camera_port != 999 or self.picture_path:
            return True
        else:
            return False

    def control_button_click(self):
        index = self.ocr.key_cp.curselection()
        if index:
            return True
        else:
            return False

