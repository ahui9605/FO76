import tkinter as tk
from tkinter import Toplevel, Button, Label
from PIL import Image, ImageTk
import scrip_glitch
import webbrowser
import content_refresh
import sys
import json


class ScalableImageWindow:
    def __init__(self, master, image_path, title, isTopmost):
        self.window = Toplevel(master)
        self.window.title(title)
        self.window.iconbitmap("imgs/logo.ico")

        self.original_image = Image.open(image_path)
        self.aspect_ratio = self.original_image.width / self.original_image.height

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # 设置窗口的初始大小为图片的大小，但是不超过屏幕的大小
        init_width = min(self.original_image.width, screen_width - 100)
        init_height = int(init_width / self.aspect_ratio)

        if init_height > screen_height - 100:
            init_height = screen_height - 100
            init_width = int(init_height * self.aspect_ratio)

        self.window.geometry(f"{init_width}x{init_height}")
        self.center_window()
        self.window.update_idletasks()

        self.canvas = tk.Canvas(self.window, cursor="cross")
        self.canvas.pack(fill="both", expand="yes")
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # 滚轮缩放
        self.canvas.bind("<Double-Button-1>", self.on_double_click)  # 双击放大

        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)  # 滑轮拖拽
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)

        self.photo = ImageTk.PhotoImage(self.original_image)
        self.image_on_canvas = self.canvas.create_image(
            0, 0, anchor="nw", image=self.photo
        )

        self.window.bind("<Configure>", self.on_resize)
        self.window.bind("<Escape>", self.close_window)
        self.window.attributes("-topmost", isTopmost)
        self.window.focus_set()

    def close_window(self, event=None):
        self.window.destroy()

    def center_window(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        self.window.update_idletasks()

        x = (screen_width // 2) - (self.window.winfo_width() // 2)
        y = (screen_height // 2) - (self.window.winfo_height() // 2)

        self.window.geometry(f"+{x}+{y}")

    def on_resize(self, event):
        width, height = (
            event.width - 4,
            event.height - 4,
        )
        new_width = min(width, int(height * self.aspect_ratio))
        new_height = int(new_width / self.aspect_ratio)

        resized_image = self.original_image.resize(
            (new_width, new_height), Image.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(resized_image)

        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_zoom(self, event, factor=None):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if factor is None:  # 如果没有传入 factor，根据滚轮事件来设置 factor
            factor = 1.1  # 默认的缩放因子
            if event.delta < 0:  # 向下滚动时缩小图像
                factor = 0.9

        new_width = int(self.photo.width() * factor)
        new_height = int(self.photo.height() * factor)

        resized_image = self.original_image.resize(
            (new_width, new_height), Image.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(resized_image)

        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.scale(tk.ALL, x, y, factor, factor)

    def on_double_click(self, event):
        self.on_zoom(event, factor=2)  # 双击时放大2倍

    def on_drag_start(self, event):
        # 记录鼠标按下时的坐标
        self.drag_data = {"x": event.x, "y": event.y}

    def on_drag_motion(self, event):
        # 计算鼠标移动的距离
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]

        # 移动 Canvas 上的所有对象
        self.canvas.move(tk.ALL, dx, dy)

        # 更新 drag_data 数据
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, str_):
        self.widget.insert("end", str_)
        self.widget.see("end")
        self.widget.update_idletasks()

    def flush(self):
        pass


def show_scalable_image(image_path, title, isTopmost):
    ScalableImageWindow(root, image_path, title, isTopmost)


def open_webpage(url):
    webbrowser.open(url)


def open_window_with_content(file_path, title, is_topMost, justify="left"):
    new_window = Toplevel(root)
    new_window.iconbitmap("imgs\logo.ico")
    new_window.title(title)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    label = tk.Label(new_window, text=content, justify=justify)
    label.pack(padx=25, pady=25)

    new_window.update_idletasks()
    
    # 暂时解决弹出窗口在topmost为true的情况下使窗口居中在屏幕中间
    new_window.after(10, lambda: new_window.geometry(f"+{x}+{y}"))  

    # 计算弹出窗口的位置并将其居中放置
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = new_window.winfo_width()
    window_height = new_window.winfo_height()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    new_window.geometry(f"+{x}+{y}")

    new_window.focus_set()
    new_window.bind("<Escape>", lambda event: new_window.destroy())
    new_window.attributes("-topmost", is_topMost)


def center_window(window):
    window.update_idletasks()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    window_width = window.winfo_width()
    window_height = window.winfo_height()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    window.geometry(f"+{x}+{y}")


def close_on_event(event, window):
    window.destroy()


def create_button(root, text, action):
    btn = Button(root, text=text, width=btn_width, height=btn_height, command=action)
    return btn


def refresh_content():
    refresh_window = tk.Toplevel(root)
    refresh_window.iconbitmap("imgs\logo.ico")
    refresh_window.title("刷新内容")

    text_widget = tk.Text(refresh_window, wrap="word")
    text_widget.pack(fill="both", expand="yes")

    sys.stdout = TextRedirector(text_widget)

    refresh_window.bind("<Key>", lambda event: close_on_event(event, refresh_window))
    refresh_window.bind(
        "<Button-1>", lambda event: close_on_event(event, refresh_window)
    )

    refresh_window.update_idletasks()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = refresh_window.winfo_width()
    window_height = refresh_window.winfo_height()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    refresh_window.geometry(f"+{x}+{y}")

    root.update()

    refresh_window.focus_set()

    #命令台打印内容移动到该窗口显示, debugger不显示
    try:
        root.update()
        content_refresh.run()
        print("鼠标单击或键盘任意键退出该窗口")
    finally:
        sys.stdout = sys.__stdout__


def show_simple_tutorial():
    tutorial_window = tk.Toplevel()
    tutorial_window.iconbitmap("imgs\logo.ico")
    tutorial_window.title("简单教程")

    text_widget = tk.Text(tutorial_window, wrap="word", state="disabled")
    text_widget.pack(fill="both", expand="yes")

    with open("txt\简单教程.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    processed_content = []
    for line in lines:
        processed_content.append("● " + line)

    tutorial_window.focus_set()

    # 将处理后的文本内容插入到 Text 小部件中以供显示，并在设置为 DISABLED 前设置为 NORMAL
    text_widget.config(state="normal")
    text_widget.insert("1.0", "\n".join(processed_content))
    text_widget.config(state="disabled")

    center_window(tutorial_window)

    tutorial_window.bind(
        "<Escape>", lambda event: close_tutorial_window(event, tutorial_window)
    )


def close_tutorial_window(event, window):
    window.destroy()


def show_about():
    about_window = tk.Toplevel()
    about_window.iconbitmap("imgs\logo.ico")
    about_window.title("关于")

    with open("config.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    current_version_data = data.get("current_version", {})
    version = current_version_data.get("version", "")
    last_refreshed = current_version_data.get("last_refreshed", "")
    _id = current_version_data.get("id", "")

    label = tk.Label(
        about_window,
        text=f"版本：{version}\n上次刷新时间：{last_refreshed}\nID：{_id}\n作者：阿辉",
        padx=30,
        pady=30,
    )
    label.pack()

    center_window(about_window)
    about_window.focus_set() 
    about_window.grab_set()

    about_window.bind("<Escape>", lambda e: about_window.destroy())


def create_menu(root):
    menu_bar = tk.Menu(root)

    operation_menu = tk.Menu(menu_bar, tearoff=0)
    operation_menu.add_checkbutton(
        label="弹出窗口始终置顶", variable=topmost_status_var
    )
    operation_menu.add_command(label="刷新内容", command=refresh_content)
    operation_menu.add_command(label="关闭程序", command=root.quit)
    menu_bar.add_cascade(label="操作", menu=operation_menu)


    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="简单教程", command=show_simple_tutorial)
    help_menu.add_command(label="关于", command=show_about)
    menu_bar.add_cascade(label="帮助", menu=help_menu)

    root.config(menu=menu_bar)


with open("config.json", "r", encoding="utf-8") as file:
    data = json.load(file)

buttons_info_external = data["buttons_config"]

buttons_info = []
for btn_info in buttons_info_external:
    action = None
    if btn_info["type"] == "image":
        action = lambda bi=btn_info: show_scalable_image(
            bi["image"], bi["title"], topmost_status_var.get()
        )
    elif btn_info["type"] == "webpage":
        action = lambda bi=btn_info: open_webpage(bi["url"])
    elif btn_info["type"] == "txt":
        action = lambda bi=btn_info: open_window_with_content(
            bi["filepath"], bi["title"], topmost_status_var.get()
        )
    elif btn_info["type"] == "custom":
        action = lambda: scrip_glitch.open_toplevel(root)

    if action:
        buttons_info.append({"text": btn_info["text"], "action": action})


if __name__ == "__main__":
    root = tk.Tk()
    root.title("骑士的口令")
    root.iconbitmap("imgs/logo.ico")

    topmost_status_var = tk.BooleanVar(value=False)

    create_menu(root)

    btn_width, btn_height = 12, 1

    for row in range(8):
        for col in range(3):
            index = row * 3 + col
            if index < len(buttons_info):
                btn_info = buttons_info[index]
                text, action = btn_info["text"], btn_info.get("action", lambda: None)
                btn = create_button(root, text, action)
            else:
                btn = create_button(root, "", lambda: None)
            btn.grid(row=row, column=col, ipadx=1, ipady=1)

    center_window(root)
    root.mainloop()
