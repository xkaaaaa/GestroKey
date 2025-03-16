"""
窗口操作模块
提供窗口切换、最小化、恢复等基本操作
"""

import pyautogui
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32process

try:
    from .log import log
except ImportError:
    from log import log

def minimize_all():
    """最小化所有窗口"""
    log("passapp", "最小化所有窗口")
    pyautogui.hotkey('win', 'd')

def restore_all():
    """恢复所有窗口"""
    log("passapp", "恢复所有窗口")
    pyautogui.hotkey('win', 'd')

def next_window():
    """切换到下一个窗口"""
    log("passapp", "切换到下一个窗口")
    pyautogui.hotkey('alt', 'tab')

def prev_window():
    """切换到上一个窗口"""
    log("passapp", "切换到上一个窗口")
    pyautogui.hotkey('alt', 'shift', 'tab')

def minimize_current_window():
    """最小化当前窗口"""
    log("passapp", "最小化当前窗口")
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

def maximize_current_window():
    """最大化当前窗口"""
    log("passapp", "最大化当前窗口")
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

if __name__ == "__main__":
    print("窗口操作模块，不建议直接运行。") 