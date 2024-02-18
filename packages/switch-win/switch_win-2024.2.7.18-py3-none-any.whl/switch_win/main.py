import keyboard
import utils
import tkinter as tk

windows_map = {
    # key:window_id
}


def on_click(tk_obj, key, window_id):
    windows_map[key] = window_id
    tk_obj.destroy()


def key2window_id(key):
    windows_id = windows_map.get(key, None)
    if windows_id:
        return windows_id

    tk_obj = tk.Tk()
    tk_obj.title("定义快捷窗口")
    windows_ids = utils.get_window_ids()
    for windows_id in windows_ids:
        name = utils.get_window_info(windows_id)
        if windows_map.get(key, None):
            name = f'{name} 已映射为{key}'
        button_obj = tk.Button(tk_obj, text=name, command=lambda win_id=windows_id: on_click(tk_obj, key, win_id))
        button_obj.pack(pady=10)
    tk_obj.mainloop()

    windows_id = windows_map[key]
    return windows_id


# 切换到窗口
def switch_to_window(key):
    windows_id = key2window_id(key)
    # print(windows_id)
    utils.focus_window(windows_id)
    print(f'切换到{windows_id}')


# 检测ctrl+shift+num
def on_key_event(event):
    if event.event_type != keyboard.KEY_DOWN:
        return
    hotkey = keyboard.get_hotkey_name()
    sign = 'ctrl+shift+'
    if not hotkey.startswith(sign):
        return
    key = hotkey[len(sign):]
    if not key:
        return
    try:
        key = int(key)
    except ValueError:
        return
    switch_to_window(key)


def main():
    keyboard.hook(on_key_event)
    keyboard.wait('ctrl+shift+esc')


main()
