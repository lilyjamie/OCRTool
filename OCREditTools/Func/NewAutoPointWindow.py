import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import *
from tkinter import messagebox


class CaptureWindow:
    def __init__(self, win):
        """CaptureWindow类.
        生成选择打开图片或连接照相机的窗口.
        Args:
            win(window): 活动窗口
        """
        self.win = win
        port_var = tk.IntVar()
        port_var.set(999)
        self.camera_frame = ttk.LabelFrame(self.win, text="camera section")
        self.port_entry = ttk.Entry(self.camera_frame, width=10, textvariable=port_var)
        self.port = port_var.get()

    def capture_widget(self):
        """capture_widget.
        CaptureWindow类的UI控件生成，以及检测button的点击事件.
        """
        self.win.resizable(0, 0)
        self.win.geometry("250x100")
        # camera 获取图像
        port_label = Label(self.camera_frame, fg="red", text="Enter Camera Port:")
        port_label.grid(column=0, row=0, sticky="W")
        self.port_entry.grid(column=1, row=0)
        self.port_entry.bind("<Return>", self.event_get_port)
        ok_button = ttk.Button(self.win, text="OK", command=self.get_port)
        ok_button.grid(column=0, row=1)
        cancel_button = ttk.Button(self.win, text="Cancel", command=self.cancel)
        cancel_button.grid(column=1, row=1)
        self.camera_frame.grid(column=0, row=0, columnspan=2, pady=10, padx=10)

    def event_get_port(self, event):
        self.get_port()

    def get_port(self):
        if self.port_entry.get():
            self.port = int(self.port_entry.get())
            self.win.destroy()
        else:
            messagebox.showerror("error", "no enter camera port")

    def cancel(self):
        self.win.destroy()

