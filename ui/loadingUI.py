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
		logger.debug("DataUpdaterThread initialized")

	def run(self):
		logger.info("Starting data update process")
		try:
			self.data_updater.run()
			logger.info("Data update process completed successfully")
		except Exception as e:
			logger.error(f"Error during data update: {str(e)}", exc_info=True)
		finally:
			self.update_finished.emit()
			logger.debug("Update finished signal emitted")

class LoadingScreen(QWidget):
	def __init__(self):
		super().__init__()
		logger.debug("Initializing LoadingScreen")
		self.initWindow()
		self.setupUI()
		self.startDataUpdate()

	def initWindow(self):
		logger.debug("Setting up window properties")
		self.setFixedSize(1150, 700)
		self.setWindowIcon(QIcon(os.path.join(basePATH, 'assets', 'icon.ico')))
		self.setWindowTitle('WuWa Inventory Kamera')

		desktop = QApplication.primaryScreen().availableGeometry()
		self.move(desktop.width() // 2 - self.width() // 2, desktop.height() // 2 - self.height() // 2)
		logger.info(f"Window positioned at {self.pos().x()}, {self.pos().y()}")

	def setupUI(self):
		logger.debug("Setting up UI components")
		self.vBoxLayout = QVBoxLayout(self)
		self.vBoxLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

		self.spinner = IndeterminateProgressRing(self)
		self.spinner.setFixedSize(200, 200)
		self.spinner.setStrokeWidth(8)
		self.vBoxLayout.addWidget(self.spinner, 0, Qt.AlignHCenter)

		self.label = BodyLabel("Loading, please wait...", self)
		self.label.setStyleSheet("color: white; font-size: 18px;")
		self.label.setAlignment(Qt.AlignCenter)
		self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter)

		self.vBoxLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
		logger.info("UI setup completed")

	def startDataUpdate(self):
		logger.info("Initializing and starting data update thread")
		self.data_updater_thread = DataUpdaterThread()
		self.data_updater_thread.update_finished.connect(self.on_update_finished)
		self.data_updater_thread.start()

	def on_update_finished(self):
		logger.info("Data update finished, transitioning to main window")
		self.close()
		try:
			self.main_window = WuWaInventoryKamera()
			self.main_window.show()
			logger.info("Main window displayed successfully")
		except Exception as e:
			logger.error(f"Error initializing main window: {str(e)}", exc_info=True)