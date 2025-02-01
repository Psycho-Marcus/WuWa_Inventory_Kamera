import logging
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
	NavigationItemPosition, MSFluentWindow, InfoBar,
	InfoBarPosition
)

from ui.homeUI import HomeInterface
from ui.settingsUI import SettingInterface
from ui.inventoryUI import InventoryInterface
from scraping.utils.common import isUserAdmin
from properties.config import basePATH

logger = logging.getLogger('WuWaInventoryKamera')

class WuWaInventoryKamera(MSFluentWindow):
	"""Main window class for the WuWa Inventory Kamera application."""

	def __init__(self):
		super().__init__()

		self.initInterface()
		self.initNavigation()
		self.initWindow()
		self.warningInfoBar()

	def initInterface(self):
		"""Initialize the different interfaces (Home, Inventory, Settings)."""
		self.homeInterface = HomeInterface(self)
		self.inventoryInterface = InventoryInterface(self)
		self.settingInterface = SettingInterface(self)

	def initNavigation(self):
		"""Set up the navigation bar with different interfaces."""
		self.addSubInterface(self.homeInterface, FIF.HOME, 'Home', FIF.HOME_FILL)
		self.addSubInterface(self.inventoryInterface, FIF.DICTIONARY, 'Inventory')
		self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', position=NavigationItemPosition.BOTTOM)

		self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

	def initWindow(self):
		"""Initialize window settings including size, icon, and title."""
		self.setFixedSize(1150, 700)
		self.setWindowIcon(QIcon(str(basePATH / 'assets' / 'icon.ico')))
		self.setWindowTitle('WuWa Inventory Kamera')
		self.titleBar.maxBtn.setHidden(True)
		self.titleBar.maxBtn.setDisabled(True)
		self.titleBar.setDoubleClickEnabled(False)
		self.setResizeEnabled(False)

		# Center the window on the screen
		desktop = QApplication.primaryScreen().availableGeometry()
		self.move(desktop.width() // 2 - self.width() // 2, desktop.height() // 2 - self.height() // 2)

	def warningInfoBar(self):
		"""Display a warning InfoBar if the application is not run as an administrator."""
		if not isUserAdmin():
			InfoBar.warning(
				title='Warning',
				content="Administrator privileges not granted.\nTo use the scanner, administrator rights must be granted.",
				orient=Qt.Vertical,
				isClosable=True,
				position=InfoBarPosition.TOP,
				duration=-1,
				parent=self
			)
			logger.warning("Administrator privileges not granted.")