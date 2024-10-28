import os
import logging

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy

from qfluentwidgets import (
	ProgressRing, BodyLabel
)

from properties.config import basePATH
from ui.mainUI import WuWaInventoryKamera
from updater.databaseUpdater import DataUpdater
from updater.assetsUpdater import AssetsUpdater

logger = logging.getLogger('LoadingScreen')

class DataUpdaterThread(QThread):
	updateProgress = Signal(int, str)
	updateFinished = Signal()

	def __init__(self):
		super().__init__()
		self.dataUpdater = DataUpdater()
		self.dataUpdater.updateProgress.connect(self.updateProgress.emit)
		self.dataUpdater.updateFinished.connect(self.updateFinished.emit)
		logger.debug("DataUpdaterThread initialized")

	def run(self):
		logger.info("Starting data update process")
		try:
			self.dataUpdater.run()
			logger.info("Data update process completed successfully")
		except Exception as e:
			logger.error(f"Error during data update: {str(e)}", exc_info=True)

class AssetsUpdaterThread(QThread):
	updateProgress = Signal(int, str)
	updateFinished = Signal()

	def __init__(self):
		super().__init__()
		self.assetsUpdater = AssetsUpdater()
		self.assetsUpdater.updateProgress.connect(self.updateProgress.emit)
		self.assetsUpdater.updateFinished.connect(self.updateFinished.emit)
		logger.debug("AssetsUpdaterThread initialized")

	def run(self):
		logger.info("Starting assets update process")
		try:
			self.assetsUpdater.run()
			logger.info("Assets update process completed successfully")
		except Exception as e:
			logger.error(f"Error during assets update: {str(e)}", exc_info=True)

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

		self.progress_ring = ProgressRing(self)
		self.progress_ring.setFixedSize(200, 200)
		self.progress_ring.setTextVisible(True)
		self.progress_ring.setValue(0)
		self.vBoxLayout.addWidget(self.progress_ring, 0, Qt.AlignHCenter)

		self.label = BodyLabel("Loading, please wait...", self)
		self.label.setStyleSheet("color: white; font-size: 18px;")
		self.label.setAlignment(Qt.AlignCenter)
		self.vBoxLayout.addWidget(self.label, 0, Qt.AlignHCenter)

		self.file_label = BodyLabel("", self)
		self.file_label.setStyleSheet("color: white; font-size: 14px;")
		self.file_label.setAlignment(Qt.AlignCenter)
		self.vBoxLayout.addWidget(self.file_label, 0, Qt.AlignHCenter)

		self.vBoxLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
		logger.info("UI setup completed")

	def startDataUpdate(self):
		logger.info("Initializing and starting data update thread")
		self.dataUpdater_thread = DataUpdaterThread()
		self.dataUpdater_thread.updateProgress.connect(self.updateProgress)
		self.dataUpdater_thread.updateFinished.connect(self.startAssetsUpdate)
		self.dataUpdater_thread.start()

	def startAssetsUpdate(self):
		logger.info("Initializing and starting data assets thread")
		self.assetsUpdater_thread = AssetsUpdaterThread()
		self.assetsUpdater_thread.updateProgress.connect(self.updateProgress)
		self.assetsUpdater_thread.updateFinished.connect(self.on_updateFinished)
		self.assetsUpdater_thread.start()

	def updateProgress(self, value, file_name):
		self.progress_ring.setValue(value)
		self.label.setText(f"Downloading {file_name}...")

	def on_updateFinished(self):
		logger.info("Data update finished, transitioning to main window")
		self.close()
		try:
			self.main_window = WuWaInventoryKamera()
			self.main_window.show()
			logger.info("Main window displayed successfully")
		except Exception as e:
			logger.error(f"Error initializing main window: {str(e)}", exc_info=True)