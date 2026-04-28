import time

try:
    import win32gui
except ImportError:
    win32gui = None

import win32api
import win32con


def press_once(hwnd: int, key: str) -> None:
    if win32gui is None:
        return

    if key.lower() == "esc":
        vk_code = win32con.VK_ESCAPE
    elif len(key) == 1:
        vk_code = win32api.VkKeyScan(key) & 0xFF
    else:
        return

    scan_code = win32api.MapVirtualKey(vk_code, 0)

    lparam_down = 1 | (scan_code << 16)
    lparam_up = 1 | (scan_code << 16) | (1 << 30) | (1 << 31)

    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, lparam_down)
    time.sleep(0.05)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, lparam_up)


def click_at(hwnd: int, x: int, y: int) -> bool:
    if win32gui is None:
        return True

    try:
        screen_pos = win32gui.ClientToScreen(hwnd, (x, y))
        win32api.SetCursorPos(screen_pos)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        return True
    except Exception:
        return False
