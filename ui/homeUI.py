import os
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
	QHBoxLayout, QVBoxLayout, QFrame,
	QWidget
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
	PushButton, PrimaryPushButton, CheckBox,
	BodyLabel, LineEdit, SpinBox,
	Signal, InfoBar, InfoBarPosition,
	ListWidget, PixmapLabel
)

from properties.config import cfg, FAILED, INVENTORY
from scraping.scraperExectuter import startScraper
from scraping.utils import itemsID, savingScraped

logger = logging.getLogger('HomeInterface')

class HomeInterface(QWidget):
	"""Main Widget with Control Panel on the left and other widgets on the right."""
	updateUISignal = Signal()

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.setObjectName("homeUI")

		self.lControlPanel = LControlPanel(self)
		self.lControlPanel.signalNotifier.connect(self.showNotification)

		self.tControlPanel = TControlPanel(self)
		self.rightWidget = QWidget(self)

		self.rightSide = QVBoxLayout()
		self.rightSide.addWidget(self.tControlPanel)
		self.rightSide.addWidget(self.rightWidget)

		self.hBoxLayout = QHBoxLayout(self)
		self.hBoxLayout.addWidget(self.lControlPanel, 0)
		self.hBoxLayout.addLayout(self.rightSide, 1)

		self.updateUISignal.connect(self.itemsManualRecognition)
		self.itemsManualRecognition()

	def itemsManualRecognition(self):
		"""Update the UI with manual recognition information if any failures exist."""
		if self.rightWidget.layout():
			QWidget().setLayout(self.rightWidget.layout())

		container = QVBoxLayout()
		if FAILED:
			container.setContentsMargins(0, 0, 0, 0)
			container.addWidget(BodyLabel('Recognition failed, manual update:'))

			mainLayout = QHBoxLayout()

			image_label = PixmapLabel()
			image = QImage(FAILED[0]['image'])
			pixmap = QPixmap.fromImage(image)
			image_label.setPixmap(pixmap)
			image_label.setScaledContents(True)
			image_label.setFixedSize(279, 407)
			mainLayout.addWidget(image_label)

			middle_layout = QVBoxLayout()
			middle_layout.addStretch(1)

			owned_layout = QVBoxLayout()
			owned_label = BodyLabel("Owned")
			self.owned_spinbox = SpinBox()
			self.owned_spinbox.setRange(1, 9999)
			self.owned_spinbox.setValue(FAILED[0]['owned'])
			owned_layout.addWidget(owned_label)
			owned_layout.addWidget(self.owned_spinbox)
			middle_layout.addLayout(owned_layout)

			skip_button = PushButton("Skip")
			change_button = PushButton("Update")
			skip_button.clicked.connect(self.onSkipButtonClicked)
			change_button.clicked.connect(self.onChangeButtonClicked)
			middle_layout.addWidget(skip_button)
			middle_layout.addWidget(change_button)
			middle_layout.addStretch(1)
			mainLayout.addLayout(middle_layout)

			right_layout = QVBoxLayout()
			self.search_bar = LineEdit()
			self.search_bar.setPlaceholderText("Search...")
			self.search_bar.textChanged.connect(self.filter_list)

			self.list_widget = ListWidget()
			self.list_widget.addItems([itemsID[item]['name'] for item in sorted(itemsID)])

			right_layout.addWidget(self.search_bar)
			right_layout.addWidget(self.list_widget)

			mainLayout.addLayout(right_layout)
			mainLayout.setStretch(0, 1)
			mainLayout.setStretch(1, 1)
			mainLayout.setStretch(2, 3)

			container.addLayout(mainLayout)
		else:
			container.addWidget(BodyLabel(''))
		container.setStretch(0, 1)

		self.rightWidget.setLayout(container)
		self.rightWidget.setVisible(True)
		self.rightWidget.update()

	def onSkipButtonClicked(self):
		"""Handle the Skip button click event."""
		global FAILED

		if FAILED:
			try: os.remove(FAILED[0]['image'])
			except: pass
			
			FAILED.pop(0)
			self.updateUISignal.emit()

	def onChangeButtonClicked(self):
		"""Handle the Update button click event."""
		global INVENTORY, FAILED

		selected_item = self.list_widget.currentItem()
		if selected_item:
			item_id = itemsID.get(selected_item.text().lower().replace(' ', ''))['id']
			INVENTORY['items'][item_id] = self.owned_spinbox.value()
			savingScraped(START_DATE=INVENTORY['date'])
		
			if FAILED:
				FAILED.pop(0)
			
			self.updateUISignal.emit()
		else:
			self.showNotification('warning', 'Warning', 'Select the item name from the list on the right side.')

	def filter_list(self, text):
		"""Filter the list_widget items based on the search query."""
		for i in range(self.list_widget.count()):
			item = self.list_widget.item(i)
			item.setHidden(text.lower() not in item.text().lower())

	def showNotification(self, _type: str, title: str, content: str):
		"""Display notifications based on type."""
		if _type == 'success':
			InfoBar.success(
				title=title,
				content=content,
				orient=Qt.Orientation.Vertical,
				isClosable=True,
				position=InfoBarPosition.TOP,
				duration=-1,
				parent=self
			)
		elif _type == 'warning':
			InfoBar.warning(
				title=title,
				content=content,
				orient=Qt.Orientation.Vertical,
				isClosable=True,
				position=InfoBarPosition.TOP,
				duration=-1,
				parent=self
			)
		elif _type == 'error':
			InfoBar.error(
				title=title,
				content=content,
				orient=Qt.Orientation.Vertical,
				isClosable=True,
				position=InfoBarPosition.TOP,
				duration=-1,
				parent=self
			)
		elif _type == 'failed':
			InfoBar.warning(
				title=title,
				content=content,
				orient=Qt.Orientation.Vertical,
				isClosable=True,
				position=InfoBarPosition.TOP,
				duration=-1,
				parent=self
			)
			self.updateUISignal.emit()

class LControlPanel(QFrame):
	"""Left Control Panel Interface."""
	signalNotifier = Signal(str, str, str)

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.__initUI()

	def __initUI(self):
		"""Initialize UI components and layout."""
		self.scannerLabel = BodyLabel('Scanner', self)
		self.scanCharacters = CheckBox('Characters', self)
		self.scanWeapons = CheckBox('Weapons', self)
		self.scanEchoes = CheckBox('Echoes', self)
		self.scanDevItems = CheckBox('Development Items', self)
		self.scanResources = CheckBox('Resources', self)
		self.scanAchievements = CheckBox('Achievements', self)

		self.closeLabel = BodyLabel("Press 'ENTER' to cancel the scan.")

		self.openExportFolder = PushButton('Export Folder', icon=FIF.FOLDER, parent=self)
		self.openExportFolder.clicked.connect(self.openFolder)

		self.startScanning = PrimaryPushButton(FIF.PLAY, 'Start Scanning', self)
		self.startScanning.clicked.connect(self.runScraper)

		self.panelLayout = QVBoxLayout(self)
		self.__setupLayout()
		self.__connectSignals()

	def __setupLayout(self):
		"""Setup the layout of the control panel."""

		self.panelLayout.setSpacing(8)
		self.panelLayout.setContentsMargins(14, 16, 14, 14)
		self.panelLayout.setAlignment(Qt.AlignTop)

		self.panelLayout.addWidget(self.scannerLabel)
		self.panelLayout.addWidget(self.scanCharacters)
		self.panelLayout.addWidget(self.scanWeapons)
		self.panelLayout.addWidget(self.scanEchoes)
		self.panelLayout.addWidget(self.scanDevItems)
		self.panelLayout.addWidget(self.scanResources)
		self.panelLayout.addWidget(self.scanAchievements)

		self.panelLayout.addStretch()
		self.panelLayout.addWidget(self.closeLabel)
		self.panelLayout.addWidget(self.openExportFolder)
		self.panelLayout.addWidget(self.startScanning)
		
		self.__setInitialValues()

	def __setInitialValues(self):
		"""Set initial values from the configuration."""
		self.scanCharacters.setChecked(cfg.scanCharacters.value)
		self.scanWeapons.setChecked(cfg.scanWeapons.value)
		self.scanEchoes.setChecked(cfg.scanEchoes.value)
		self.scanDevItems.setChecked(cfg.scanDevItems.value)
		self.scanResources.setChecked(cfg.scanResources.value)
		self.scanAchievements.setChecked(cfg.scanAchievements.value)

	def __connectSignals(self):
		"""Connect signals to slots."""
		self.scanResources.stateChanged.connect(self.onValueChanged)
		self.scanDevItems.stateChanged.connect(self.onValueChanged)
		self.scanEchoes.stateChanged.connect(self.onValueChanged)
		self.scanCharacters.stateChanged.connect(self.onValueChanged)
		self.scanWeapons.stateChanged.connect(self.onValueChanged)
		self.scanAchievements.stateChanged.connect(self.onAchievementsToggled)

	def onValueChanged(self):
		"""Handle value changes in checkboxes."""
		cfg.scanResources.value = self.scanResources.isChecked()
		cfg.scanDevItems.value = self.scanDevItems.isChecked()
		cfg.scanEchoes.value = self.scanEchoes.isChecked()
		cfg.scanCharacters.value = self.scanCharacters.isChecked()
		cfg.scanWeapons.value = self.scanWeapons.isChecked()

		if self.scanCharacters.isChecked() or self.scanWeapons.isChecked() or \
		   self.scanEchoes.isChecked() or self.scanDevItems.isChecked() or \
		   self.scanResources.isChecked():
			self.scanAchievements.setChecked(False)
			self.scanAchievements.setDisabled(True)
		else:
			self.scanAchievements.setDisabled(False)

		cfg.save()

	def onAchievementsToggled(self):
		"""Handle Achievements checkbox toggle event."""
		if self.scanAchievements.isChecked():
			self.setOtherCheckboxesEnabled(False)
		else:
			self.setOtherCheckboxesEnabled(True)

		cfg.scanAchievements.value = self.scanAchievements.isChecked()
		cfg.save()

	def setOtherCheckboxesEnabled(self, enabled):
		"""Enable or disable other checkboxes based on the state of Achievements."""
		self.scanCharacters.setDisabled(not enabled)
		self.scanWeapons.setDisabled(not enabled)
		self.scanEchoes.setDisabled(not enabled)
		self.scanDevItems.setDisabled(not enabled)
		self.scanResources.setDisabled(not enabled)

	def runScraper(self):
		"""Run the scraper and emit notifications if needed."""

		notification = startScraper()
		if notification:
			logger.debug(f"Notification: {notification}")
			self.signalNotifier.emit(notification[0], notification[1], notification[2])

	def openFolder(self):
		"""Open the export folder."""
		os.makedirs(cfg.get(cfg.exportFolder), exist_ok=True)
		os.startfile(cfg.get(cfg.exportFolder))

class TControlPanel(QFrame):
	"""Top Control Panel Interface."""

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.__initUI()

	def __initUI(self):
		"""Initialize UI components and layout."""
		self.echoMinimumLabel = BodyLabel('Echoes minimum:', self)
		self.echoMinRarity = SpinBox(self)
		self.echoMinLevel = SpinBox(self)

		self.weaponsMinimumLabel = BodyLabel('Weapons minimum:', self)
		self.weaponsMinRarity = SpinBox(self)
		self.weaponsMinLevel = SpinBox(self)

		self.panelLayout = QHBoxLayout(self)
		self.__setupLayout()
		self.__connectSignals()

	def __setupLayout(self):
		"""Setup the layout of the top control panel."""
		self.weaponsMinRarity.setRange(1, 5)
		self.echoMinRarity.setRange(1, 5)
		self.weaponsMinLevel.setRange(1, 90)
		self.echoMinLevel.setRange(0, 25)

		echoRarityLayout = QVBoxLayout()
		echoRarityLabel = BodyLabel('Rarity', self)
		echoRarityLayout.addWidget(echoRarityLabel)
		echoRarityLayout.addWidget(self.echoMinRarity)
		
		echoLevelLayout = QVBoxLayout()
		echoLevelLabel = BodyLabel('Level', self)
		echoLevelLayout.addWidget(echoLevelLabel)
		echoLevelLayout.addWidget(self.echoMinLevel)

		echoControlLayout = QVBoxLayout()
		echoControlLayout.addWidget(self.echoMinimumLabel)
		echoControlLayout.addLayout(echoRarityLayout)
		echoControlLayout.addLayout(echoLevelLayout)

		weaponsRarityLayout = QVBoxLayout()
		weaponsRarityLabel = BodyLabel('Rarity', self)
		weaponsRarityLayout.addWidget(weaponsRarityLabel)
		weaponsRarityLayout.addWidget(self.weaponsMinRarity)

		weaponsLevelLayout = QVBoxLayout()
		weaponsLevelLabel = BodyLabel('Level', self)
		weaponsLevelLayout.addWidget(weaponsLevelLabel)
		weaponsLevelLayout.addWidget(self.weaponsMinLevel)

		weaponsControlLayout = QVBoxLayout()
		weaponsControlLayout.addWidget(self.weaponsMinimumLabel)
		weaponsControlLayout.addLayout(weaponsRarityLayout)
		weaponsControlLayout.addLayout(weaponsLevelLayout)

		self.panelLayout.addSpacing(4)
		self.panelLayout.addLayout(echoControlLayout)
		self.panelLayout.addSpacing(10)
		self.panelLayout.addLayout(weaponsControlLayout)

		self.__setInitialValues()

	def __setInitialValues(self):
		"""Set initial values from the configuration."""
		self.echoMinRarity.setValue(cfg.echoMinRarity.value)
		self.echoMinLevel.setValue(cfg.echoMinLevel.value)
		self.weaponsMinRarity.setValue(cfg.weaponsMinRarity.value)
		self.weaponsMinLevel.setValue(cfg.weaponsMinLevel.value)

	def __connectSignals(self):
		"""Connect signals to slots."""
		self.echoMinLevel.valueChanged.connect(self.onValueChanged)
		self.echoMinRarity.valueChanged.connect(self.onValueChanged)
		self.weaponsMinLevel.valueChanged.connect(self.onValueChanged)
		self.weaponsMinRarity.valueChanged.connect(self.onValueChanged)

	def onValueChanged(self):
		"""Handle value changes in spinboxes."""
		cfg.echoMinLevel.value = self.echoMinLevel.value()
		cfg.echoMinRarity.value = self.echoMinRarity.value()
		cfg.weaponsMinLevel.value = self.weaponsMinLevel.value()
		cfg.weaponsMinRarity.value = self.weaponsMinRarity.value()
		cfg.save()
