"""
iogp.win: ctypes-based wrappers over useful Windows APIs.

Example usage: iterating all windows

    import iogp.win as win
    def callback(hwnd, lparam):
        size = 512
        buf = win.unicode_buffer(size)
        win.GetWindowText(hwnd, buf, size)
        print(f'[-] Handle: {hwnd}, title: {buf.value}')
        return 1  # 0 to stop
    win.EnumWindows(win.WNDENUMPROC(callback), 0)

Author: Vlad Ioan Topan (vtopan/gmail).
"""

import ctypes
from ctypes import (byref, cast, windll, get_last_error, FormatError, c_void_p, c_int,
    c_int64, Structure, POINTER, WINFUNCTYPE, GetLastError, WinError)
from ctypes.wintypes import (BOOL, BYTE, WORD, DWORD, HANDLE, HMODULE, HINSTANCE, HWND, LPWSTR,
        WPARAM, LPARAM, HDC, RECT, POINT, UINT, LPCSTR, LPCWSTR)


user32 = windll.user32
kernel32 = windll.kernel32
gdi32 = windll.gdi32

INVALID_HANDLE_VALUE = c_void_p(-1).value
LRESULT = c_int64
PDWORD = POINTER(DWORD)
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PVOID = c_void_p
NULL = None

DIB_RGB_COLORS = 0
ICON_BIG = 1
ICON_SMALL = 0
IMAGE_ICON = 1
LR_CREATEDIBSECTION = 0x20001
LR_DEFAULTSIZE = 0x40
LR_LOADFROMFILE = 0x10
MAX_PATH = 260
SRCCOPY = 0xCC0020
WM_SETICON = 0x0080


# Structures

class RGBQUAD(Structure):
    _fields_ = [
        ("rgbBlue", BYTE),
        ("rgbGreen", BYTE),
        ("rgbRed", BYTE),
        ("rgbReserved", BYTE),
    ]
PRGBQUAD = POINTER(RGBQUAD)     # NOQA


class BITMAPINFOHEADER(Structure):
    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", DWORD),
        ("biHeight", DWORD),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", DWORD),
        ("biYPelsPerMeter", DWORD),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD),
    ]
PBITMAPINFOHEADER = POINTER(BITMAPINFOHEADER)   # NOQA


class BITMAPINFO(Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", RGBQUAD * 1),
    ]
PBITMAPINFO = POINTER(BITMAPINFO)   # NOQA


### Windows APIs

## kernel32

# GetModuleHandle(lpModuleName)
GetModuleHandle = WINFUNCTYPE(HMODULE, LPCWSTR)(("GetModuleHandleW", kernel32))
# OpenProcess(hProcess, dwFlags, lpExeName, lpdwSize)
OpenProcess = WINFUNCTYPE(HANDLE, DWORD, BOOL, DWORD)(("OpenProcess", kernel32)) 
# QueryFullProcessImageName(hObject)
QueryFullProcessImageName = WINFUNCTYPE(BOOL, HANDLE, DWORD, LPWSTR,
        PDWORD)(("QueryFullProcessImageNameW", kernel32))
# CloseHandle(hWnd)
CloseHandle = WINFUNCTYPE(BOOL, HANDLE)(("CloseHandle", kernel32))

## user32

# GetActiveWindow()
GetActiveWindow = WINFUNCTYPE(HWND)(("GetActiveWindow", user32))
# SetActiveWindow(hWnd)
SetActiveWindow = WINFUNCTYPE(HWND, HWND)(("SetActiveWindow", user32))
GetForegroundWindow = WINFUNCTYPE(HWND)(("GetForegroundWindow", user32))
# SetForegroundWindow(hWnd)
SetForegroundWindow = WINFUNCTYPE(BOOL, HWND)(("SetForegroundWindow", user32))
# SetFocus(hWnd)
SetFocus = WINFUNCTYPE(HWND, HWND)(("SetFocus", user32))
# FindWindow(lpClassName, lpWindowName)
FindWindow = WINFUNCTYPE(HWND, LPWSTR, LPWSTR)(("FindWindowW", user32))
# WNDENUMPROC(hwnd, lParam) - callback for EnumWindows
WNDENUMPROC = WINFUNCTYPE(BOOL, HWND, LPARAM) # (lpEnumFunc, lParam)
# EnumWindows(hWnd, lpString, nMaxCount)
EnumWindows = WINFUNCTYPE(BOOL, WNDENUMPROC, LPARAM)(("EnumWindows", user32))
# GetWindowText(hWnd, lpdwProcessId)
GetWindowText = WINFUNCTYPE(c_int, HWND, LPWSTR, c_int)(("GetWindowTextW", user32))
# GetWindowThreadProcessId(dwDesiredAccess, bInheritHandle, dwProcessId)
GetWindowThreadProcessId = WINFUNCTYPE(DWORD, HWND, PDWORD)(("GetWindowThreadProcessId", user32))
GetWindowDC = WINFUNCTYPE(HDC, HWND)(("GetWindowDC", user32))
# GetWindowRect(hWnd, lpRect)
GetWindowRect = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))(("GetWindowRect", user32))
# GetClientRect(hWnd, lpRect)
GetClientRect = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))(("GetClientRect", user32))
ReleaseDC = WINFUNCTYPE(c_int, HWND, HDC)(("ReleaseDC", user32))
# ClientToScreen(hWnd, lpPoint)
ClientToScreen = WINFUNCTYPE(BOOL, HWND, POINTER(POINT))(("ClientToScreen", user32))
# PrintWindow(hwnd, hdcBlt, nFlags)
PrintWindow = WINFUNCTYPE(BOOL, HWND, HDC, UINT)(("PrintWindow", user32))
# FlashWindow(hWnd, bInvert)
FlashWindow = WINFUNCTYPE(BOOL, HWND, BOOL)(("FlashWindow", user32))

## gdi32

# BitBlt(hdc, cx, cy)
BitBlt = WINFUNCTYPE(BOOL, HDC, c_int, c_int, c_int, c_int, HDC, c_int, c_int, DWORD)(("BitBlt", gdi32))
# CreateCompatibleDC(hdc)
CreateCompatibleDC = WINFUNCTYPE(HDC, HDC)(("CreateCompatibleDC", gdi32))
# GetDIBits(hdc, hbm, start, cLines, lpvBits, lpbmi, usage)
GetDIBits = WINFUNCTYPE(c_int, HDC, HANDLE, UINT, UINT, PVOID, PBITMAPINFO, UINT)(("GetDIBits", gdi32))
# SelectObject(hdc, h)
SelectObject = WINFUNCTYPE(HANDLE, HDC, HANDLE)(("SelectObject", gdi32))
# DeleteDC(hDC)
DeleteDC = WINFUNCTYPE(BOOL, HDC)(("DeleteDC", gdi32))
# DeleteObject(ho)
DeleteObject = WINFUNCTYPE(BOOL, HANDLE)(("DeleteObject", gdi32))
# LoadImageW(hInst, name, type, cx, cy, fuLoad)
LoadImage = WINFUNCTYPE(HANDLE, HINSTANCE, LPCWSTR, UINT, c_int, c_int, UINT)(("LoadImageW", user32))
# SendMessage(hWnd, Msg, wParam, lParam)
SendMessage = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)(("SendMessageA", user32))


### Useful wrappers

def last_error():
    err = get_last_error()
    return "0x%08X: %s" % (err, FormatError(err))


def unicode_buffer(size):
    """
    Create a WSTR buffer of `size` characters.
    """
    return ctypes.create_unicode_buffer(size)


def get_window_rect(title=None):
    """
    Get the coordinates of the window given by title (default: the top window).

    :return: tuple(x1, y1, x2, y2) or None (if window not found)
    """
    if title:
        hwnd = FindWindow(None, title)
        if not hwnd:
            return None
    else:
        hwnd = GetForegroundWindow()
    rect = RECT()
    GetWindowRect(hwnd, byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


def get_window_size(title=None):
    """
    Get the coordinates of the window given by title (default: the top window).

    :return: tuple(width, height) or None (if window not found)
    """
    if title:
        hwnd = FindWindow(None, title)
        if not hwnd:
            return None
    else:
        hwnd = GetForegroundWindow()
    rect = RECT()
    GetClientRect(hwnd, byref(rect))
    return (rect.right, rect.bottom)


def screenshot(hwnd=None, include_titlebar=True, as_rgb=True):
    """
    Take a screenshot of the given window (if None, use the current active window).

    :param hwnd: Window handle (or None).
    :param include_titlebar: Include the window's title bar in the screenshot.
    :param as_rgb: Return the raw bytes as 'RGB' instead of 'BGRX'.
    :return: tuple(width, height, raw_bmp_data)
    """
    if hwnd is None:
        hwnd = GetForegroundWindow()
    dc = GetWindowDC(hwnd)
    if not hwnd:
        raise OSError(f'GetForegroundWindow failed: {last_error()}')
    cdc = CreateCompatibleDC(dc)
    if not cdc:
        raise OSError(f'CreateCompatibleDC failed: {last_error()}')
    rect = RECT()
    fun = GetWindowRect if include_titlebar else GetClientRect
    if not fun(hwnd, byref(rect)):
        raise OSError(f'GetClient/WindowRect failed: {last_error()}')
    left, right, top, bottom = rect.left, rect.right, rect.top, rect.bottom
    width = right - left
    height = bottom - top
    bmp = CreateCompatibleBitmap(dc, width, height)
    if not bmp:
        raise OSError(f'CreateCompatibleBitmap failed: {last_error()}')
    if not SelectObject(cdc, bmp):
        raise OSError(f'SelectObject failed: {last_error()}')
    if not PrintWindow(hwnd, cdc, 0 if include_titlebar else 1):
        raise OSError(f'PrintWindow failed: {last_error()}')
    bmph = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), width, height, 1, 32, 0)
    buffer = ctypes.create_string_buffer(width * height * 4)
    cnt = GetDIBits(cdc, bmp, 0, height, buffer, cast(byref(bmph), PBITMAPINFO), DIB_RGB_COLORS)
    if not cnt:
        raise OSError(f'GetDIBits failed: {last_error()}')
    DeleteDC(cdc)
    ReleaseDC(hwnd, dc)
    DeleteObject(bmp)
    if as_rgb:
        rgb = ctypes.create_string_buffer(width * height * 3)
        rgb[0::3] = buffer[2::4]
        rgb[1::3] = buffer[1::4]
        rgb[2::3] = buffer[0::4]
        buffer = rgb
    return (width, height, buffer)


def set_window_icon(icon_filename, hwnd=None):
    """
    Set the icon for a window (default: foreground window).
    """
    h_icon = LoadImage(None, icon_filename, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
    if not h_icon:
        raise OSError(f'Failed loading icon from file {icon_filename}: {WinError(GetLastError())}')
    if hwnd is None:
        hwnd = GetForegroundWindow()
    SendMessage(hwnd, WM_SETICON, ICON_BIG, h_icon)
    SendMessage(hwnd, WM_SETICON, ICON_SMALL, h_icon)
