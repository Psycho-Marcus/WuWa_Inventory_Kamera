import ctypes
import ctypes.wintypes as wintypes
import logging

logger = logging.getLogger('isGameForeground')


# Constants
WINDOW_RESTORE = 9  # Restore window if minimized or maximized

# Type definitions
HWND = wintypes.HWND
DWORD = wintypes.DWORD
BOOL = wintypes.BOOL
LPARAM = wintypes.LPARAM

class isGameForeground:
    """Encapsulates functionality to check if a specific process ID owns the foreground window."""
    
    def __init__(self):
        try:
            self.user32 = ctypes.WinDLL('user32', use_last_error=True)
            
            # Define API functions
            self.GetForegroundWindow = self.user32.GetForegroundWindow
            self.GetForegroundWindow.restype = HWND

            self.GetWindowThreadProcessId = self.user32.GetWindowThreadProcessId
            self.GetWindowThreadProcessId.restype = DWORD
            self.GetWindowThreadProcessId.argtypes = [HWND, ctypes.POINTER(DWORD)]
        except Exception as e:
            logger.error(f"Failed to initialize isGameForeground: {e}")
            raise

    def isForeground(self, target_pid):
        """Checks if the foreground window is owned by the specified process ID."""
        try:
            hwnd_foreground = self.GetForegroundWindow()
            if not hwnd_foreground:
                raise ctypes.WinError(ctypes.get_last_error())

            foreground_pid = DWORD()
            self.GetWindowThreadProcessId(hwnd_foreground, ctypes.byref(foreground_pid))
            
            is_foreground = foreground_pid.value == target_pid
            return is_foreground
        except Exception as e:
            logger.error(f"Error checking foreground window: {e}")
            return False
