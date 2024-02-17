from tkinter import *


class CanvasFunction:
    def __init__(self, master: Tk, size: tuple[int, int], **options):
        self.master = master
        self.size = size
        self.options = options
        self.canvas = Canvas(self.master, width=size[0], height=size[1], **options)

        self.canvasFuncDict = {
            "create": {
                "line": lambda x1, y1, x2, y2: self.canvas.create_line(x1, y1, x2, y2),
                "rectangle": lambda x1, y1, x2, y2: self.canvas.create_rectangle(x1, y1, x2, y2),
                "oval": lambda x1, y1, x2, y2: self.canvas.create_oval(x1, y1, x2, y2),
                "text": lambda *args, **kwargs: self.canvas.create_text(*args, **kwargs),
                "image": lambda x, y, image: self.canvas.create_image(x, y, image=image)
            },
            "bind": lambda key, func: self.canvas.bind(key, func),
            "operate": {
                "move": lambda item, x, y: self.canvas.move(item, x, y),
                "itemConfig": lambda item, **option: self.canvas.itemconfig(item, **option),
                "delete": lambda item: self.canvas.delete(item)
            }
        }
