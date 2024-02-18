import keyboard
import tkinter as tk
from typing import Literal
import Xlib
from Xlib import display, Xatom

display_obj = display.Display()
root = display_obj.screen().root

key_map = {
    # key:window_id
}
windows_map = {
    # window_id:key
}


# 当前窗口列表id
def get_window_ids():
    global display_obj, root
    window_ids = root.get_full_property(display_obj.intern_atom('_NET_CLIENT_LIST'), Xlib.X.AnyPropertyType).value
    window_ids = list(window_ids)
    return window_ids


# 窗口信息
def get_window_info(window_id):
    global display_obj
    window = display_obj.create_resource_object('window', window_id)
    name = window.get_full_property(display_obj.intern_atom('_NET_WM_NAME'), 0)
    name = name.value.decode() if name else None
    # desktop = window.get_full_property(display_obj.intern_atom('_NET_WM_DESKTOP'), 0)
    # desktop = desktop.value[0] if desktop else None
    # return name, desktop
    return name


# 切换到窗口
def focus_window(window_id):
    global display_obj
    window = display_obj.create_resource_object('window', window_id)
    window.set_input_focus(Xlib.X.RevertToParent, Xlib.X.CurrentTime)
    window.raise_window()

    net_wm_state = display_obj.intern_atom('_NET_WM_STATE')
    window.change_property(net_wm_state, Xatom.ATOM, 32, [Xatom.ATOM], Xlib.X.PropModeReplace)
    display_obj.sync()


def on_click(tk_obj, key, window_id):
    global key_map, windows_map
    key_map[key] = window_id
    windows_map[window_id] = key
    tk_obj.destroy()


def key2window_id(key):
    global key_map, windows_map
    windows_id = key_map.get(key, None)
    if windows_id:
        return windows_id

    tk_obj = tk.Tk()
    tk_obj.title("定义快捷窗口")
    windows_ids = utils.get_window_ids()
    for windows_id in windows_ids:
        name = utils.get_window_info(windows_id)

        if windows_id in windows_map:
            now_key = windows_map[windows_id]
            name = f'{now_key}:{name}'
            state: Literal["normal", "active", "disabled"] = 'disabled'
        else:
            state: Literal["normal", "active", "disabled"] = 'normal'
        button_obj = tk.Button(
            tk_obj,
            text=name,
            command=lambda win_id=windows_id: on_click(tk_obj, key, win_id),
            state=state,
        )
        button_obj.pack(pady=10)
    tk_obj.mainloop()

    windows_id = key_map[key]
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
