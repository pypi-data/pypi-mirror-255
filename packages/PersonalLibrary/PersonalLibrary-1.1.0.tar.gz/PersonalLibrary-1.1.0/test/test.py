import tkinter as tk
from PIL import ImageTk, Image


def submit_text():
    input_text = entry.get()
    print("Input text:", input_text)


root = tk.Tk()
canvas = tk.Canvas(root, width=1920, height=1080)
canvas.grid(column=0, row=0)

# 加载图像并存储为全局变量
image = Image.open(r"E:\Python\PersonalLibrary\PersonalLibrary\EasyTkinter\resource\assets\img\test.jpg")
image_tk = ImageTk.PhotoImage(image)

canvas.create_image(960, 540, image=image_tk)

frame = tk.Frame(canvas)
entry = tk.Entry(frame)
submit_button = tk.Button(frame, text="Submit", command=submit_text)

frame_id = canvas.create_window(100, 10, window=frame)
entry.grid(row=0, column=0)
submit_button.grid(row=0, column=1)

root.mainloop()
