import time
from ctypes import WinDLL
from tkinter import Frame, Label, Entry, StringVar, Toplevel, Tk
from tkinter.ttk import Separator
import tkinter as tk
from keyboard import add_hotkey, remove_hotkey, read_event
import webbrowser

VK_SPACE = 0x20
KEYEVENTF_KEYDOWN = 0x0  # 空格键模拟按下但未松开
KEYEVENTF_KEYUP = 0x2  # 空格键模拟仅松开，无按下
DISALLOWED_KEYS = ["left windows", "right windows", "left alt", "right alt", "f12"]

user32 = WinDLL("user32.dll")


def press_key(key):
    user32.keybd_event(key, 0, KEYEVENTF_KEYDOWN, 0)
    time.sleep(0.1)
    user32.keybd_event(key, 0, KEYEVENTF_KEYUP, 0)


def start_press_key(direction_var):
    press_key(VK_SPACE)
    direction = direction_var.get()
    if direction == "从下到上":
        press_key(ord("W"))
    elif direction == "从上到下":
        press_key(ord("S"))


def set_hotkey(hotkey_var, direction_var):
    hotkey = hotkey_var.get()
    try:
        remove_hotkey(hotkey)
    except KeyError:
        pass
    except Exception as e:
        print(f"Error removing hotkey: {e}")
    try:
        add_hotkey(
            hotkey,
            lambda: start_press_key(direction_var),
            suppress=True,
            trigger_on_release=True,
        )
    except Exception as e:
        print(f"Error adding hotkey: {e}")


def capture_key(hotkey_var, direction_var):
    key_event = read_event(suppress=True)
    if key_event.event_type == "down" and key_event.name.lower() not in DISALLOWED_KEYS:
        hotkey_var.set(key_event.name)
        set_hotkey(hotkey_var, direction_var)
    else:
        print(f"{key_event.name} 不可以作为快捷键。")


def remove_all_hotkeys(hotkey_var):
    try:
        remove_hotkey(hotkey_var.get())
    except KeyError:
        pass
    except Exception as e:
        print(f"Error removing hotkey: {e}")
    hotkey_var.set("未绑定")


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
        )
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tutorial_hyperlink(window, url, display_text):
    text = tk.Text(
        window, height=1, wrap="word", padx=10, pady=10, bg="#f0f0f0", relief="flat"
    )

    # 根据链接文本长度来调整宽度
    text_width = len(display_text) + 6
    text.config(width=text_width)
    text.pack(side="top", anchor="center")

    # 插入超链接文本
    text.insert(tk.INSERT, display_text, "link")
    text.tag_config("link", foreground="blue", underline=1)
    text.tag_bind("link", "<Enter>", lambda e: text.config(cursor="hand2"))
    text.tag_bind("link", "<Leave>", lambda e: text.config(cursor="arrow"))
    text.tag_bind("link", "<Button-1>", lambda e: webbrowser.open(url))
    text.configure(state="disabled")


def open_toplevel():
    top = Toplevel(root)
    root.withdraw()

    root.overrideredirect(True)

    top.focus_set()
    top.bind("<Escape>", lambda event: top.destroy())
    top.grab_set()
    top.title("洗三星词条")

    frame_top = Frame(top)
    frame_top.pack(side="top", pady=10, padx=20)

    label = Label(
        frame_top,
        text="此脚本可以用两个而不是四个传奇模块来洗装备三星词条\n\n点击后按下键盘任意键重新绑定, f12清空绑定\n目前不支持win键和alt键绑定",
    )
    label.pack(pady=10)

    frame_top_center = Frame(top)
    frame_top_center.pack(side="top")

    add_tutorial_hyperlink(
        frame_top_center,
        "https://www.bilibili.com/video/BV1aw41117v6/?vd_source=20b5913deef23faecfc0ec708f4e708c",
        "视频示例",
    )

    frame_center = Frame(top)
    frame_center.pack(side="top", pady=5)

    # 快捷键默认按键
    hotkey_var = StringVar(value="f2")

    capture_button = tk.Button(
        frame_center,
        text="绑定快捷键",
        command=lambda: capture_key(hotkey_var, direction_var),
    )
    capture_button.pack(side="left", padx=15, pady=5)

    entry = Entry(
        frame_center,
        textvariable=hotkey_var,
        state="readonly",
        justify="center",
        width=15,
    )
    entry.pack(side="right", padx=5, pady=5)

    separator = Separator(top, orient="horizontal")
    separator.pack(fill="x")

    frame_bottom = tk.Frame(top)
    frame_bottom.pack(side="bottom", padx=10, pady=10)

    direction_var = tk.StringVar(value="从下到上")
    radio_button_up = tk.Radiobutton(
        frame_bottom, text="从下到上", variable=direction_var, value="从下到上"
    )
    radio_button_down = tk.Radiobutton(
        frame_bottom, text="从上到下", variable=direction_var, value="从上到下"
    )

    radio_button_up.pack(side="left", padx=5, pady=5)
    radio_button_down.pack(side="right", padx=5, pady=5)

    tooltip_up = Tooltip(radio_button_up, "一星词条在最下面的时候选择此项")
    tooltip_down = Tooltip(radio_button_down, "一星词条在最上面的时候选择此项")

    try:
        add_hotkey("f12", remove_all_hotkeys, suppress=True, trigger_on_release=True)
    except Exception as e:
        print(f"Error adding hotkey: {e}")

    set_hotkey(hotkey_var, direction_var)

    top.update_idletasks()
    width = top.winfo_width()
    height = top.winfo_height()
    x = (top.winfo_screenwidth() // 2) - (width // 2)
    y = (top.winfo_screenheight() // 2) - (height // 2)
    top.geometry(f"{width}x{height}+{x}+{y}")

    top.protocol("WM_DELETE_WINDOW", exit_program)


def exit_program():
    root.quit()


if __name__ == "__main__":
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"+{x}+{y}")

    open_toplevel()
    root.mainloop()