import logging

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QWidget, QFileDialog

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
	SettingCardGroup, SwitchSettingCard, PushSettingCard,
	HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
	ExpandLayout, InfoBar, ComboBoxSettingCard, BodyLabel,
	OptionsSettingCard, Theme, setTheme
)

from ui.custom_widgets import FieldSettingCard
from properties.config import (
	cfg, alphabethList, maxLength,
	HELP_URL, FEEDBACK_URL
)

logger = logging.getLogger('SettingInterface')

class SettingInterface(ScrollArea):
	"""Settings interface for application configuration."""

	checkUpdateSig = Signal()
	exportFolderChanged = Signal(str)

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.setObjectName("settingsUI")
		self.setStyleSheet("""
			QScrollArea { background: transparent; }
			QScrollArea > QWidget > QWidget { background: transparent; }
			QScrollArea > QScrollBar { background: transparent; }
		""")

		self.scrollWidget = QWidget()
		self.scrollWidget.setStyleSheet("background: transparent;")
		self.expandLayout = ExpandLayout(self.scrollWidget)

		self.__initializeWidgets()
		self.__initializeLayout()
		self.__connectSignals()

	def __initializeWidgets(self):
		"""Initialize all widgets for the settings interface."""
		# "Title"
		self.settingLabel = BodyLabel(self.tr("Settings"), self)
		self.settingLabel.setFont(QFont('Microsoft YaHei Light', 30, QFont.Weight.Bold))

		# Personalization
		self.personalizationGroup = SettingCardGroup(self.tr("Personalization"), self.scrollWidget)
		self.themeCard = OptionsSettingCard(
			cfg.themeMode,
			FIF.BRUSH,
			self.tr('Application theme'),
			self.tr("Change the appearance of your application"),
			texts=[
				self.tr('Light'), self.tr('Dark'),
				self.tr('Use system setting')
			],
			parent=self.personalizationGroup
		)
		self.exportFolderCard = PushSettingCard(
			self.tr('Choose folder'),
			FIF.DOWNLOAD,
			self.tr("Export directory"),
			cfg.get(cfg.exportFolder),
			self.personalizationGroup
		)

		# In-Game settings
		self.inGameGroup = SettingCardGroup(self.tr("In-Game settings"), self.scrollWidget)
		self.roverName = FieldSettingCard(
			cfg.roverName,
			FIF.FONT_SIZE,
			self.tr('Rover Name'),
			self.tr('Insert your rover name'),
			max_length=maxLength,
			parent=self.inGameGroup
		)
		self.languageGame = ComboBoxSettingCard(
			cfg.gameLanguages,
			FIF.LANGUAGE,
			self.tr('Language'),
			self.tr('Set the language you use in game'),
			['English'],
			self.inGameGroup
		)
		self.inventoryKey = ComboBoxSettingCard(
			cfg.inventoryKeybind,
			FIF.FONT_SIZE,
			self.tr('Inventory Keybind'),
			self.tr('Select the keybind you use in game to open the inventory'),
			alphabethList(),
			self.inGameGroup
		)
		self.resonatorKey = ComboBoxSettingCard(
			cfg.resonatorKeybind,
			FIF.FONT_SIZE,
			self.tr('Characters Keybind'),
			self.tr('Select the keybind you use in game to open the resonators'),
			alphabethList(),
			self.inGameGroup
		)

		# Software update
		self.updateSoftwareGroup = SettingCardGroup(self.tr("Software update"), self.scrollWidget)
		self.updateOnStartUpCard = SwitchSettingCard(
			FIF.UPDATE,
			self.tr('Check for updates when the application starts'),
			self.tr('The new version will be more stable and have more features'),
			configItem=cfg.checkUpdateAtStartUp,
			parent=self.updateSoftwareGroup
		)

		# About
		self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
		self.helpCard = HyperlinkCard(
			HELP_URL,
			self.tr('Open help page'),
			FIF.HELP,
			self.tr('Help'),
			self.tr('Ask something'),
			self.aboutGroup
		)
		self.feedbackCard = PrimaryPushSettingCard(
			self.tr('Provide feedback'),
			FIF.FEEDBACK,
			self.tr('Provide feedback'),
			self.tr('Report bug and issues'),
			self.aboutGroup
		)

	def __initializeLayout(self):
		"""Set up the layout for all widgets."""
		self.resize(1000, 800)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setViewportMargins(0, 120, 0, 20)
		self.setWidget(self.scrollWidget)
		self.setWidgetResizable(True)

		# Layout arrangement
		self.settingLabel.move(60, 63)

		# Add widgets to their respective groups
		self.personalizationGroup.addSettingCard(self.themeCard)
		self.personalizationGroup.addSettingCard(self.exportFolderCard)
		self.inGameGroup.addSettingCard(self.roverName)
		self.inGameGroup.addSettingCard(self.languageGame)
		self.inGameGroup.addSettingCard(self.inventoryKey)
		self.inGameGroup.addSettingCard(self.resonatorKey)
		self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)
		self.aboutGroup.addSettingCard(self.helpCard)
		self.aboutGroup.addSettingCard(self.feedbackCard)

		# Add setting card groups to the main layout
		self.expandLayout.setSpacing(28)
		self.expandLayout.setContentsMargins(60, 10, 60, 0)
		self.expandLayout.addWidget(self.personalizationGroup)
		self.expandLayout.addWidget(self.inGameGroup)
		self.expandLayout.addWidget(self.updateSoftwareGroup)
		self.expandLayout.addWidget(self.aboutGroup)

	def __showRestartTooltip(self):
		"""Display a tooltip indicating a restart is required for changes to take effect."""
		InfoBar.warning(
			'',
			self.tr('Configuration takes effect after restart'),
			parent=self.window()
		)

	def __onExportFolderCardClicked(self):
		"""Handle the event when the export folder card is clicked."""
		folder = QFileDialog.getExistingDirectory(
			self, self.tr("Choose folder"), "./")
		if folder and cfg.get(cfg.exportFolder) != folder:
			cfg.set(cfg.exportFolder, folder)
			self.exportFolderCard.setContent(folder)

	def __onThemeChanged(self, theme: Theme):
		"""Handle theme change events."""
		setTheme(theme)

	def __connectSignals(self):
		"""Connect signals to their respective slots."""
		cfg.appRestartSig.connect(self.__showRestartTooltip)
		cfg.themeChanged.connect(self.__onThemeChanged)
		self.exportFolderCard.clicked.connect(self.__onExportFolderCardClicked)
		self.feedbackCard.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
