import tkinter as tk

from OCREditTools.Control import Control

if __name__ == "__main__":
    win = tk.Tk()
    win.minsize(width=1540, height=720)
    win.maxsize(width=1540, height=720)
    Control(win)
