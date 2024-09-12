import time
import ctypes

from properties.config import user32

# Constants for key events
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
MAPVK_VSC_TO_VK = 1

# Constants for mouse events
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

# Key codes and scan codes
_OFFSET_EXTENDEDKEY = 0xE000
_OFFSET_SHIFTKEY = 0x10000
_SHIFT_SCANCODE = 0x2A

MODIFIER_KEYS = {
    'ctrl': 0x1D,
    'alt': 0x38,
    'shift': _SHIFT_SCANCODE,
    'win': 0x5B + _OFFSET_EXTENDEDKEY,
}

KEY_MAPPING = {
    # Function keys
    "f1": 0x3B,
    "f2": 0x3C,
    "f3": 0x3D,
    "f4": 0x3E,
    "f5": 0x3F,
    "f6": 0x40,
    "f7": 0x41,
    "f8": 0x42,
    "f9": 0x43,
    "f10": 0x44,
    "f11": 0x57,
    "f12": 0x58,
    
    # Escape and special keys
    "escape": 0x01,
    "esc": 0x01,
    "enter": 0x1C,
    "return": 0x1C,
    "tab": 0x0F,
    "shift": _SHIFT_SCANCODE,
    "ctrl": 0x1D,
    "alt": 0x38,
    "space": 0x39,
    "capslock": 0x3A,
    "delete": 0x53 + _OFFSET_EXTENDEDKEY,
    "end": 0x4F + _OFFSET_EXTENDEDKEY,
    "win": 0x5B + _OFFSET_EXTENDEDKEY,
    
    # Alphanumeric keys
    "0": 0x0B,
    "1": 0x02,
    "2": 0x03,
    "3": 0x04,
    "4": 0x05,
    "5": 0x06,
    "6": 0x07,
    "7": 0x08,
    "8": 0x09,
    "9": 0x0A,
    "a": 0x1E,
    "b": 0x30,
    "c": 0x2E,
    "d": 0x20,
    "e": 0x12,
    "f": 0x21,
    "g": 0x22,
    "h": 0x23,
    "i": 0x17,
    "j": 0x24,
    "k": 0x25,
    "l": 0x26,
    "m": 0x32,
    "n": 0x31,
    "o": 0x18,
    "p": 0x19,
    "q": 0x10,
    "r": 0x13,
    "s": 0x1F,
    "t": 0x14,
    "u": 0x16,
    "v": 0x2F,
    "w": 0x11,
    "x": 0x2D,
    "y": 0x15,
    "z": 0x2C,
    
    # Punctuation and symbols
    "`": 0x29,
    "-": 0x0C,
    "=": 0x0D,
    "[": 0x1A,
    "]": 0x1B,
    "\\": 0x2B,
    ";": 0x27,
    "'": 0x28,
    ",": 0x33,
    ".": 0x34,
    "/": 0x35,
    
    # Special characters
    "~": 0x29 + _OFFSET_SHIFTKEY,
    "!": 0x02 + _OFFSET_SHIFTKEY,
    "@": 0x03 + _OFFSET_SHIFTKEY,
    "#": 0x04 + _OFFSET_SHIFTKEY,
    "$": 0x05 + _OFFSET_SHIFTKEY,
    "%": 0x06 + _OFFSET_SHIFTKEY,
    "^": 0x07 + _OFFSET_SHIFTKEY,
    "&": 0x08 + _OFFSET_SHIFTKEY,
    "*": 0x09 + _OFFSET_SHIFTKEY,
    "(": 0x0A + _OFFSET_SHIFTKEY,
    ")": 0x0B + _OFFSET_SHIFTKEY,
    "_": 0x0C + _OFFSET_SHIFTKEY,
    "+": 0x0D + _OFFSET_SHIFTKEY,
    "{": 0x1A + _OFFSET_SHIFTKEY,
    "}": 0x1B + _OFFSET_SHIFTKEY,
    "|": 0x2B + _OFFSET_SHIFTKEY,
    "\"": 0x28 + _OFFSET_SHIFTKEY,
    "<": 0x33 + _OFFSET_SHIFTKEY,
    ">": 0x34 + _OFFSET_SHIFTKEY,
    "?": 0x35 + _OFFSET_SHIFTKEY,
    
    # Miscellaneous
    "backspace": 0x0E,
    "del": 0x53 + _OFFSET_EXTENDEDKEY,
    "shiftleft": 0x2A,
    "shiftright": 0x36,
    "ctrlleft": 0x1D,
    "winleft": 0x5B + _OFFSET_EXTENDEDKEY,
    "altleft": 0x38,
    " ": 0x39,
}

# Functions
def mouseScroll(amount: int|float, waitTime: float = .1):
    scaledAmount = int(amount * 120)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, scaledAmount, 0)

    time.sleep(waitTime)

def moveMouse(x: int|float, y: int|float, waitTime: float = .1):
    ctypes.windll.user32.SetCursorPos(x, y)

def leftClick(x: int|float, y: int|float, waitTime: float = .1):
    moveMouse(x, y)
    
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    time.sleep(waitTime)

def presskey(keyName, waitTime: float = 0.1, useShift: bool = True):
    original_keyName = keyName
    keyName = keyName.lower()
    keyCode = KEY_MAPPING.get(keyName)
    
    if keyCode is not None:
        isExtended = keyCode & _OFFSET_EXTENDEDKEY
        isShift = (keyCode & _OFFSET_SHIFTKEY or original_keyName.isupper()) and useShift
        scanCode = keyCode & 0xFF

        vk = user32.MapVirtualKeyExA(scanCode, MAPVK_VSC_TO_VK, 0)

        if isShift:
            user32.keybd_event(0x10, 0x2A, 0, 0)

        flags = 0
        if isExtended:
            flags |= 0x0001

        user32.keybd_event(vk, scanCode, flags, 0)
        user32.keybd_event(vk, scanCode, flags | KEYEVENTF_KEYUP, 0)

        if isShift:
            user32.keybd_event(0x10, 0x2A, KEYEVENTF_KEYUP, 0)

        time.sleep(waitTime)

def hotkey(*args: str, delay: float = .05, waitTime: float = .1):
    """
    Perform a hotkey combination.
    Example usage: hotkey('ctrl', 'v') for Ctrl+V
    """
    for key in args:
        if key.lower() in MODIFIER_KEYS:
            scancode = MODIFIER_KEYS[key.lower()]
        else:
            scancode = KEY_MAPPING.get(key.lower())
        
        if scancode is not None:
            vk = user32.MapVirtualKeyExA(scancode & 0xFF, MAPVK_VSC_TO_VK, 0)
            flags = KEYEVENTF_KEYDOWN
            if scancode & _OFFSET_EXTENDEDKEY:
                flags |= MOUSEEVENTF_MOVE
            
            # Send key down event
            user32.keybd_event(vk, scancode & 0xFF, flags, 0)
            time.sleep(delay)

    for key in reversed(args):
        if key.lower() in MODIFIER_KEYS:
            scancode = MODIFIER_KEYS[key.lower()]
        else:
            scancode = KEY_MAPPING.get(key.lower())

        if scancode is not None:
            vk = user32.MapVirtualKeyExA(scancode & 0xFF, MAPVK_VSC_TO_VK, 0)
            flags = KEYEVENTF_KEYUP
            if scancode & _OFFSET_EXTENDEDKEY:
                flags |= MOUSEEVENTF_MOVE
            
            # Send key up event
            user32.keybd_event(vk, scancode & 0xFF, flags, 0)
            time.sleep(delay)
    
    time.sleep(waitTime)