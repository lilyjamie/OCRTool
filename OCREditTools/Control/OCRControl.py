from tkinter.filedialog import *
from tkinter import messagebox
from collections import OrderedDict
import json

from OCREditTools.View.OCRView import OCREditTool
from OCREditTools.Func.FiledictObserver import *
from OCREditTools.Func.NewEditCPWindow import NewWindow
from OCREditTools.Func.NewAutoPointWindow import CaptureWindow
from OCREditTools.OCRCheck.PictureAutoGetPoint import PictureGetPoint
from OCREditTools.OCRCheck.ocr import *


class Control:
    def __init__(self, win):
        self.win = win
        self.origin_file_dict = {}
        self.camera_port = 999
        # 创建观察者
        self.file_watch = File({})
        self.ocr = OCREditTool(self.win)
        self.picture_path = ""
        # 添加被观察者
        self.file_watch.attach(self.ocr)
        self.ocr.open_button.bind("<Button-1>", self.open)
        self.ocr.add_button.bind("<Button-1>", self.add)
        self.ocr.rename_button.bind("<Button-1>", self.rename)
        self.ocr.delete_button.bind("<Button-1>", self.delete)
        self.ocr.key_cp.bind("<<ListboxSelect>>", self.send_cp_value_to_edit_event)
        self.ocr.save_button.bind("<Button-1>", self.save_edit)
        self.ocr.camera_picture_button.bind("<Button-1>", self.auto_camera_capture_point)
        self.ocr.re_choose_camera_button.config(state=DISABLED)
        self.ocr.re_choose_camera_button.bind("<Button-1>", self.reinput_auto_camera_capture)
        self.ocr.choose_picture_button.bind("<Button-1>", self.choose_picture_get_point)
        self.ocr.check_button.bind("<Button-1>", self.ocr_check)
        self.win.mainloop()

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
        # print(self.checkpoint_name)
        # 如果返回checkpoint name,则新增checkpoint
        if self.checkpoint_name:
            if self.checkpoint_name in self.file_watch.file_dict.keys():
                messagebox.showerror("error", "checkpoint name already exits")
            else:
                value = {
                    "x1y1_x2y2": [20, 50, 280, 130],
                    "img_filter": "binary-inv",
                    "config": "--psm 7"}
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
        self.ocr.filter_combox.delete(0, END)
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
        self.clear_widget()
        self.file_dict = file_dict
        self.cur_cp_name = cur_cp_name
        self.origin_cp_value_dict = {}
        self.origin_cp_value_dict = self.file_dict[cur_cp_name]
        filter_index = {"auto": 0, "gray": 1, "binary": 2, "binary-inv": 3}

        for key in self.origin_cp_value_dict:
            if key == "x1y1_x2y2":
                self.ocr.point_entry.insert(0, str(self.origin_cp_value_dict[key]))
            elif key == "target_text":
                self.ocr.target_text.insert("1.0", self.origin_cp_value_dict[key])
            elif key == "img_filter":
                img_filter = self.origin_cp_value_dict[key]
                self.ocr.filter_combox.current(filter_index[img_filter])
            elif key == "max_check_count":
                self.ocr.count_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "lang":
                self.ocr.lang_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "nice":
                self.ocr.nice_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "text_compare_method":
                text_method = re.split("\|", self.origin_cp_value_dict[key])
                for method in text_method:
                    self.ocr.text_cmp_method_listbox.select_set(self.ocr.cmp_method_index[method])
            elif key == "inherit":
                self.ocr.inherit_entry.insert(0, self.origin_cp_value_dict[key])
            elif key == "config":
                config = self.origin_cp_value_dict[key].strip()
                new_config = int(config[-2:])
                self.ocr.config_box.current(int(new_config))
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
            self.cp_value_dict["max_check_count"] = self.ocr.count_entry.get()
        if self.ocr.lang_entry.get():
            self.cp_value_dict["lang"] = self.ocr.lang_entry.get()
        if self.ocr.nice_entry.get():
            self.cp_value_dict["nice"] = self.ocr.nice_entry.get()
        if self.ocr.config_box.get():
            self.cp_value_dict["config"] = "--psm " + str(self.ocr.config_box.get())

        method_indexs = self.ocr.text_cmp_method_listbox.curselection()
        str_temp = ""
        cmp_method_index = {0: "br2auto-sp", 1: "br2sp", 2: "no-br", 3: "no-sp", 4: "substr", 5: "regular"}
        if method_indexs:
            for i in range(len(method_indexs)):
                if i == len(method_indexs) - 1:
                    str_temp = str_temp + cmp_method_index[method_indexs[i]]
                else:
                    str_temp = str_temp + cmp_method_index[method_indexs[i]] + "|"

            self.cp_value_dict["text_compare_method"] = str_temp

        if self.ocr.inherit_entry.get():
            self.cp_value_dict["inherit"] = self.ocr.inherit_entry.get()

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
                self.get_point(self.camera_port)
        else:
            messagebox.showerror("error", "no select checkpoint")

    def reinput_auto_camera_capture(self, events):
        ret = self.control_button_click()
        if ret:
            self.new_camera_window()
        else:
            messagebox.showerror("error", "no select checkpoint")

    def get_camera_port(self, events):
        # 获取是否有打开填写过camera
        self.camera_port = self.edit_point.port
        if self.edit_point.port == 999:
            pass
        else:
            self.ocr.re_choose_camera_button.config(state=NORMAL)
            self.get_point(self.edit_point.port)

    def choose_picture_get_point(self, events):
        """choose_picture_get_point.
        打开图片，并生成opencv窗口，获取图片坐标.
        """
        ret = self.control_button_click()
        if ret:
            file_types = [
                ("JPG", "*.jpg"), ("JPEG", "*.jpeg")]
            file_obj = askopenfile(filetypes=file_types)
            if file_obj:
                self.picture_path = file_obj.name
                self.get_point(self.picture_path)
        else:
            messagebox.showerror("error", "no select checkpoint")

    def get_point(self, picture_path):
        pic = PictureGetPoint(picture_path)
        pic.show()
        # 将picture point 输入到输入框
        if pic.point_list:
            print(pic.point_list)
            self.ocr.point_entry.delete(0, END)
            self.ocr.point_entry.insert(0, str(pic.point_list[0]))

    def ocr_check(self, events):
        ret = self.control_button_click()
        load_pictur_flag = self.check_button_click_state()
        if ret:
            if load_pictur_flag:
                self.ocr.check_text.delete("1.0", END)
                self.ocr.check_text.configure(background="white")
                self.new_edit_cp_dict()
                print("ocr_check")
                if self.picture_path:
                    self.ocr_compare(self.picture_path)
                else:
                    self.ocr_compare()
            else:
                messagebox.showerror("error", "no capture or choose picture")
        else:
            messagebox.showerror("error", "no select checkpoint")

    def ocr_compare(self, picture_path="pic.jpg"):
        if picture_path == "pic.jpg":
            ocr_check = OCR()
        else:
            ocr_check = OCR(picture_path)
        ocr_check.ocr_load_checkpoint_config(self.choose_checkpoint, self.cp_value_dict)
        ret, ratio = ocr_check.ocr_checkpoint(self.choose_checkpoint)
        if hasattr(ocr_check, 'return_str'):
            self.ocr.check_text.delete("1.0", END)
            self.ocr.check_text.insert("1.0", ocr_check.return_str)
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


if __name__ == "__main__":
    win = Tk()
    Control(win)


