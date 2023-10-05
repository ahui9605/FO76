import tkinter as tk

def toggle_topmost():
    is_topmost = root.attributes('-topmost')
    root.attributes('-topmost', not is_topmost)
    topmost_status_var.set(not is_topmost)

def create_menu(root):
    menu_bar = tk.Menu(root)

    operation_menu = tk.Menu(menu_bar, tearoff=0)
    operation_menu.add_command(label="刷新内容")
    operation_menu.add_command(label="关闭程序", command=root.quit)
    operation_menu.add_checkbutton(label="始终置顶", variable=topmost_status_var, command=toggle_topmost)
    
    menu_bar.add_cascade(label="操作", menu=operation_menu)
    
    root.config(menu=menu_bar)

root = tk.Tk()
root.title("我的应用")

topmost_status_var = tk.BooleanVar(value=False)
create_menu(root)

root.mainloop()
