import os
import logging

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy

from qfluentwidgets import (
	IndeterminateProgressRing, BodyLabel
)

from properties.config import basePATH
from ui.mainUI import WuWaInventoryKamera
from updater.databaseUpdater import DataUpdater

logger = logging.getLogger('LoadingScreen')

class DataUpdaterThread(QThread):
	update_finished = Signal()

	def __init__(self):
		super().__init__()
		self.data_updater = DataUpdater()

	def run(self):
		self.data_updater.run()
		self.update_finished.emit()

class LoadingScreen(QWidget):
	def __init__(self):
		super().__init__()
		self.initWindow()

		# Set up layout
		self.vBoxLayout = QVBoxLayout(self)

		# Add a spacer at the top to push content to the center
		self.vBoxLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

		# Add the spinner (progress ring)
		self.spinner = IndeterminateProgressRing(self)
		self.spinner.setFixedSize(200, 200)
		self.spinner.setStrokeWidth(8)
		self.vBoxLayout.addWidget(self.spinner, 0, Qt.AlignHCenter)

		# Add the label below the spinner
		self.label = BodyLabel("Loading, please wait...", self)
		self.label.setStyleSheet("color: white; font-size: 18px;")
		self.label.setAlignment(Qt.AlignCenter)
		self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter)

		# Add another spacer at the bottom to balance the layout
		self.vBoxLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

		# Start the data updater thread
		self.data_updater_thread = DataUpdaterThread()
		self.data_updater_thread.update_finished.connect(self.on_update_finished)
		self.data_updater_thread.start()

	def initWindow(self):
		"""Initialize window settings including size, icon, and title."""
		self.setFixedSize(1150, 700)
		self.setWindowIcon(QIcon(os.path.join(basePATH, 'assets', 'icon.ico')))
		self.setWindowTitle('WuWa Inventory Kamera')

		# Center the window on the screen
		desktop = QApplication.primaryScreen().availableGeometry()
		self.move(desktop.width() // 2 - self.width() // 2, desktop.height() // 2 - self.height() // 2)

	def on_update_finished(self):
		# Close the loading screen and open the main application
		self.close()
		self.main_window = WuWaInventoryKamera()
		self.main_window.show()