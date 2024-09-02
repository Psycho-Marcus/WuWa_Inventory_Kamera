import sys
from PySide6.QtWidgets import QApplication
from ui.loadingUI import LoadingScreen

def start():
    app = QApplication(sys.argv)
    
    loading_screen = LoadingScreen()
    loading_screen.show()
    
    app.exec()
