import sys
import os
import string
import ctypes
from datetime import datetime
from typing import List

import pytesseract
from qfluentwidgets import (
	qconfig, QConfig, ConfigValidator,
	ConfigItem, OptionsConfigItem, BoolValidator,
	FolderValidator, OptionsValidator, RangeValidator,
	Signal
)

user32 = ctypes.windll.user32
basePATH = getattr(sys, 'frozen', False) and sys._MEIPASS or os.getcwd()

# Default paths and values
pytesseract.pytesseract.tesseract_cmd = os.path.join(basePATH, 'Tesseract-OCR', 'tesseract.exe')

PROCESS_NAME = 'Client-Win64-Shipping.exe'
WINDOW_NAME = 'Wuthering Waves'
START_DATE = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
DPI_SCALING = user32.GetDpiForWindow(user32.GetForegroundWindow()) / 96.0
INVENTORY = {"2": 0}
FAILED: List[str] = []
maxLength = 12


def alphabethList() -> List[str]:
	"""Generate a list of uppercase letters, digits, and punctuation."""
	return list(string.ascii_uppercase + string.digits + string.punctuation)

class TextValidator(ConfigValidator):
	"""Text validator with optional length constraint."""

	def __init__(self, max_length: int = None):
		"""
		Parameters
		----------
		max_length: int, optional
			Maximum allowed length for the text. If None, no length limit is applied.
		"""
		if max_length is not None and max_length <= 0:
			raise ValueError("The `max_length` must be a positive integer.")
		
		self.max_length = max_length

	def validate(self, value: str) -> bool:
		"""
		Validate the text against the criteria.

		Parameters
		----------
		value: str
			The text to validate.

		Returns
		-------
		bool
			True if the text is valid, False otherwise.
		"""
		if not value:
			return False

		if self.max_length is not None and len(value) > self.max_length:
			return False

		return True

	def correct(self, value: str) -> str:
		"""
		Correct the text if it does not meet the validation criteria.

		Parameters
		----------
		value: str
			The text to correct.

		Returns
		-------
		str
			The corrected text.
		"""
		if not value:
			value = 'Rover'

		if self.max_length is not None:
			value = value[:self.max_length]

		return value

class Config(QConfig):
	"""Configuration for the application."""

	configChanged = Signal()

	def save(self):
		"""Save configuration and emit change signal."""
		super().save()
		self.configChanged.emit()

	# Configuration items
	exportFolder = ConfigItem("Folders", "Export", "export", FolderValidator())
	checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())
	gameLanguages = OptionsConfigItem('InGame', 'Language', 'English', OptionsValidator(['English']))
	inventoryKeybind = OptionsConfigItem('InGame', 'InventoryKeybind', 'B', OptionsValidator(alphabethList()))
	resonatorKeybind = OptionsConfigItem('InGame', 'ResonatorKeybind', 'C', OptionsValidator(alphabethList()))
	roverName = ConfigItem('InGame', 'RoverName', 'Rover', TextValidator(max_length=maxLength))

	# LControlPanel settings
	scanCharacters = ConfigItem("Scanner", "ScanCharacters", False, BoolValidator())
	scanWeapons = ConfigItem("Scanner", "ScanWeapons", False, BoolValidator())
	scanEchoes = ConfigItem("Scanner", "ScanEchoes", False, BoolValidator())
	scanDevItems = ConfigItem("Scanner", "ScanDevItems", False, BoolValidator())
	scanResources = ConfigItem("Scanner", "ScanResources", False, BoolValidator())

	# TControlPanel settings
	echoMinRarity = ConfigItem("Scanner", "EchoMinRarity", 1, RangeValidator(1, 5))
	echoMinLevel = ConfigItem("Scanner", "EchoMinLevel", 0, RangeValidator(0, 90))
	weaponsMinRarity = ConfigItem("Scanner", "WeaponsMinRarity", 1, RangeValidator(1, 5))
	weaponsMinLevel = ConfigItem("Scanner", "WeaponsMinLevel", 0, RangeValidator(0, 90))

# Application metadata
HELP_URL = "https://t.me/psycho_marcus"
FEEDBACK_URL = "https://github.com/Psycho-Marcus/WuWa_Inventory_Kamera/issues"
RELEASE_URL = "https://github.com/Psycho-Marcus/WuWa_Inventory_Kamera/releases/latest"

# Load configuration
cfg = Config()
qconfig.load('config/config.json', cfg)
