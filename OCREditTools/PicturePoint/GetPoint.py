from tkinter import *
from PIL import Image, ImageTk


class DrawPoint:
    def __init__(self, canvas, show_point_entry, picture_path):
        self.canvas = canvas
        self.canvas.grid(column=2, row=0)
        self.show_point_entry = show_point_entry
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        image = Image.open(picture_path)
        width = int(image.size[0]*0.5)
        height = int(image.size[1]*0.5)
        self.canvas.config(width=width, height=height)
        img = image.resize((width, height))
        self.im = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.im)
        self.canvas.update()
        self.canvas.bind("<Button-1>", self.get_start_point)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.send_rect_point)

    def get_start_point(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(0, 0, 1, 1, outline="red")

    def draw_rect(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def send_rect_point(self, event):
        self.end_x = event.x
        self.end_y = event.y
        if self.start_y == self.end_y:
            pass
        else:
            point = (self.start_x*2, self.start_y*2, self.end_x*2, self.end_y * 2)
            self.show_point_entry.delete(0, END)
            self.show_point_entry.insert(0, str(list(point)))
