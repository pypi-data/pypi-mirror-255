import Xlib
from Xlib import display, Xatom

display_obj = display.Display()
root = display_obj.screen().root


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
