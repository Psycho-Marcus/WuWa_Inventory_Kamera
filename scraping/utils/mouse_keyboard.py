import time
import win32api
import win32con
from typing import Union
from mss import mss

class WindowsInputController:
    """
    A class to handle Windows input simulation including keyboard and mouse controls.
    """
    
    def __init__(self, monitor: int = 1):
        """
        Initialize WindowsInputController with monitor index.
        
        Args:
            monitor (int): Monitor index to use for mouse operations
        """
        self.sct = mss()
        self.monitor = self.sct.monitors[monitor]
    
    # Class-level constants
    KEYEVENTF_KEYDOWN = 0x0000
    KEYEVENTF_KEYUP = 0x0002
    MAPVK_VSC_TO_VK = 1
    
    _OFFSET_EXTENDEDKEY = 0x0100
    _OFFSET_SHIFTKEY = 0x0200
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
        "0": 0x0B, "1": 0x02, "2": 0x03, "3": 0x04, "4": 0x05,
        "5": 0x06, "6": 0x07, "7": 0x08, "8": 0x09, "9": 0x0A,
        "a": 0x1E, "b": 0x30, "c": 0x2E, "d": 0x20, "e": 0x12,
        "f": 0x21, "g": 0x22, "h": 0x23, "i": 0x17, "j": 0x24,
        "k": 0x25, "l": 0x26, "m": 0x32, "n": 0x31, "o": 0x18,
        "p": 0x19, "q": 0x10, "r": 0x13, "s": 0x1F, "t": 0x14,
        "u": 0x16, "v": 0x2F, "w": 0x11, "x": 0x2D, "y": 0x15,
        "z": 0x2C,
        
        # Punctuation and symbols
        "`": 0x29, "-": 0x0C, "=": 0x0D, "[": 0x1A, "]": 0x1B,
        "\\": 0x2B, ";": 0x27, "'": 0x28, ",": 0x33, ".": 0x34,
        "/": 0x35,
        
        # Special characters
        "~": 0x29 + _OFFSET_SHIFTKEY, "!": 0x02 + _OFFSET_SHIFTKEY,
        "@": 0x03 + _OFFSET_SHIFTKEY, "#": 0x04 + _OFFSET_SHIFTKEY,
        "$": 0x05 + _OFFSET_SHIFTKEY, "%": 0x06 + _OFFSET_SHIFTKEY,
        "^": 0x07 + _OFFSET_SHIFTKEY, "&": 0x08 + _OFFSET_SHIFTKEY,
        "*": 0x09 + _OFFSET_SHIFTKEY, "(": 0x0A + _OFFSET_SHIFTKEY,
        ")": 0x0B + _OFFSET_SHIFTKEY, "_": 0x0C + _OFFSET_SHIFTKEY,
        "+": 0x0D + _OFFSET_SHIFTKEY, "{": 0x1A + _OFFSET_SHIFTKEY,
        "}": 0x1B + _OFFSET_SHIFTKEY, "|": 0x2B + _OFFSET_SHIFTKEY,
        "\"": 0x28 + _OFFSET_SHIFTKEY, "<": 0x33 + _OFFSET_SHIFTKEY,
        ">": 0x34 + _OFFSET_SHIFTKEY, "?": 0x35 + _OFFSET_SHIFTKEY,
        
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
    
    def mouseScroll(self, amount: Union[int, float], waitTime: float = 0.1) -> None:
        """
        Simulate mouse wheel scrolling.
        
        Args:
            amount (Union[int, float]): Scroll amount, positive for down, negative for up.
            waitTime (float, optional): Time to wait after scrolling. Defaults to 0.1.
        """
        scaledAmount = int(amount * 120)
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, scaledAmount, 0)
        time.sleep(waitTime)
    
    def moveMouse(self, x: Union[int, float], y: Union[int, float], waitTime: float = 0.1) -> None:
        """
        Move the mouse cursor to specified coordinates relative to the monitor.
        
        Args:
            x (Union[int, float]): X-coordinate relative to monitor
            y (Union[int, float]): Y-coordinate relative to monitor
            waitTime (float, optional): Time to wait after moving. Defaults to 0.1.
        """
        x = int(x) + self.monitor["left"]
        y = int(y) + self.monitor["top"]
        win32api.SetCursorPos((x, y))
        time.sleep(waitTime)
    
    def leftClick(self, x: Union[int, float], y: Union[int, float], waitTime: float = 0.1) -> None:
        """
        Move mouse and perform a left mouse click at specified coordinates relative to the monitor.
        
        Args:
            x (Union[int, float]): X-coordinate relative to monitor
            y (Union[int, float]): Y-coordinate relative to monitor
            waitTime (float, optional): Time to wait after clicking. Defaults to 0.1.
        """
        self.moveMouse(x, y)
        x, y = win32api.GetCursorPos()
        
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(waitTime)
    
    @classmethod
    def pressKey(cls, keyName: str, waitTime: float = 0.1, useShift: bool = True) -> None:
        """
        Simulate pressing a specific key with improved text input support.
        
        Args:
            keyName (str): Name of the key to press.
            waitTime (float, optional): Time to wait after key press. Defaults to 0.1.
            useShift (bool, optional): Whether to use shift for uppercase. Defaults to True.
        """
        original_keyName = keyName
        keyName = keyName.lower()
        keyCode = cls.KEY_MAPPING.get(keyName)
        
        if keyCode is not None:
            isExtended = keyCode & cls._OFFSET_EXTENDEDKEY
            isShift = (keyCode & cls._OFFSET_SHIFTKEY or original_keyName.isupper()) and useShift
            scanCode = keyCode & 0xFF
            
            vk = win32api.MapVirtualKey(scanCode, cls.MAPVK_VSC_TO_VK)
            
            if isShift:
                win32api.keybd_event(win32con.VK_SHIFT, cls._SHIFT_SCANCODE, 0, 0)
            
            flags = win32con.KEYEVENTF_SCANCODE
            if isExtended:
                flags |= win32con.KEYEVENTF_EXTENDEDKEY
            
            win32api.keybd_event(vk, scanCode, flags, 0)
            win32api.keybd_event(vk, scanCode, flags | win32con.KEYEVENTF_KEYUP, 0)
            
            if isShift:
                win32api.keybd_event(win32con.VK_SHIFT, cls._SHIFT_SCANCODE, win32con.KEYEVENTF_KEYUP, 0)
            
            time.sleep(waitTime)
    
    @classmethod
    def hotKey(cls, *args: str, delay: float = 0.05, waitTime: float = 0.1) -> None:
        """
        Perform a hotkey combination.
        
        Args:
            *args (str): Keys to press in the hotkey combination.
            delay (float, optional): Delay between key presses. Defaults to 0.05.
            waitTime (float, optional): Time to wait after completing hotkey. Defaults to 0.1.
            
        Example:
            WindowsInputController.hotKey('ctrl', 'v')  # Performs Ctrl+V
        """
        # Press all keys in sequence
        for key in args:
            if key.lower() in cls.MODIFIER_KEYS:
                scancode = cls.MODIFIER_KEYS[key.lower()]
            else:
                scancode = cls.KEY_MAPPING.get(key.lower())
            
            if scancode is not None:
                vk = win32api.MapVirtualKey(scancode & 0xFF, cls.MAPVK_VSC_TO_VK)
                flags = win32con.KEYEVENTF_SCANCODE
                if scancode & cls._OFFSET_EXTENDEDKEY:
                    flags |= win32con.KEYEVENTF_EXTENDEDKEY
                
                win32api.keybd_event(vk, scancode & 0xFF, flags, 0)
                time.sleep(delay)
        
        # Release all keys in reverse sequence
        for key in reversed(args):
            if key.lower() in cls.MODIFIER_KEYS:
                scancode = cls.MODIFIER_KEYS[key.lower()]
            else:
                scancode = cls.KEY_MAPPING.get(key.lower())
            
            if scancode is not None:
                vk = win32api.MapVirtualKey(scancode & 0xFF, cls.MAPVK_VSC_TO_VK)
                flags = win32con.KEYEVENTF_SCANCODE | win32con.KEYEVENTF_KEYUP
                if scancode & cls._OFFSET_EXTENDEDKEY:
                    flags |= win32con.KEYEVENTF_EXTENDEDKEY
                
                win32api.keybd_event(vk, scancode & 0xFF, flags, 0)
                time.sleep(delay)
        
        time.sleep(waitTime)