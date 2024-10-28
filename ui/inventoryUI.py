import json
import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIntValidator
from PySide6.QtWidgets import (
	QWidget, QFileDialog, QGridLayout,
	QVBoxLayout
)

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
	SettingCardGroup, ScrollArea, CardWidget,
	StrongBodyLabel, BodyLabel, LineEdit
)

from ui.custom_widgets.widget import MultiplePushSettingCard
from properties.config import cfg
from scraping.utils.common import itemsID

logger = logging.getLogger('InventoryInterface')

class ItemCard(CardWidget):
	"""A widget representing an item with an image, name, and quantity input field."""
	
	def __init__(self, image_path, name, quantity, parent=None):
		super().__init__(parent)
		self.itemName = name
		self.quantity = quantity

		self.imageLabel = BodyLabel(self)
		self.nameLabel = StrongBodyLabel(name if len(name) < 19 else name[:16] + '...', self)
		self.quantityLineEdit = LineEdit(self)
		
		self.setupQuantityLineEdit(quantity)
		self.setupImage(image_path)
		self.setupLayout()

	def setupQuantityLineEdit(self, quantity):
		"""Configure the quantity input field."""
		self.quantityLineEdit.setText(str(quantity))
		self.quantityLineEdit.setValidator(QIntValidator(0, 999999999, self))
		self.quantityLineEdit.setAlignment(Qt.AlignCenter)

	def setupImage(self, image_path):
		"""Load and display the item's image."""
		pixmap = QPixmap(image_path)
		scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.imageLabel.setPixmap(scaled_pixmap)
		self.imageLabel.setFixedSize(64, 64)
		self.imageLabel.setAlignment(Qt.AlignCenter)

	def setupLayout(self):
		"""Arrange widgets within the layout."""
		vBoxLayout = QVBoxLayout(self)
		vBoxLayout.addWidget(self.imageLabel, alignment=Qt.AlignCenter)
		vBoxLayout.addWidget(self.nameLabel, alignment=Qt.AlignCenter)
		vBoxLayout.addWidget(self.quantityLineEdit, alignment=Qt.AlignCenter)
		vBoxLayout.setSpacing(5)
		vBoxLayout.setContentsMargins(5, 5, 5, 5)
		self.setToolTip(f"{self.itemName}")

	def getItemName(self):
		"""Return the name of the item."""
		return self.itemName

	def getQuantity(self):
		"""Return the quantity from the input field, or 0 if there's an error."""
		try:
			return int(self.quantityLineEdit.text())
		except ValueError:
			return 0

class InventoryInterface(ScrollArea):
	"""A scrollable area displaying and managing an inventory of items."""
	
	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.setObjectName("inventoryUI")
		self.setStyleSheet("""
			QScrollArea { background: transparent; }
			QScrollArea > QWidget > QWidget { background: transparent; }
			QScrollArea > QScrollBar { background: transparent; }
		""")

		self.scrollWidget = QWidget()
		self.scrollWidget.setStyleSheet("background: transparent;")
		self.mainLayout = QVBoxLayout(self.scrollWidget)

		self.inventoryGroup = SettingCardGroup(self.tr("Inventory"), self.scrollWidget)
		self.inventoryFileCard = MultiplePushSettingCard(
			[self.tr('Load file'), self.tr('Save file')],
			FIF.DOWNLOAD,
			self.tr("Inventory file"),
			parent=self.inventoryGroup
		)

		self.gridWidget = QWidget(self)
		self.gridLayout = QGridLayout(self.gridWidget)

		self.__initWidget()

	def __initWidget(self):
		"""Initialize the widget and set up layout and signals."""
		self.setWidget(self.scrollWidget)
		self.setWidgetResizable(True)
		self.__initLayout()
		self.__connectSignalToSlot()

	def __initLayout(self):
		"""Set up the layout for the inventory interface."""
		self.inventoryGroup.addSettingCard(self.inventoryFileCard)
		self.mainLayout.setSpacing(28)
		self.mainLayout.setContentsMargins(60, 10, 60, 0)
		self.mainLayout.addWidget(self.inventoryGroup)
		self.mainLayout.addWidget(self.gridWidget)
		self.mainLayout.addStretch(1)
		self.gridLayout.setSpacing(10)

	def __connectSignalToSlot(self):
		"""Connect signals from the file card to the appropriate slot."""
		self.inventoryFileCard.buttonClicked.connect(self.__onInventoryFileCardClicked)

	def __onInventoryFileCardClicked(self, index):
		"""Handle button clicks on the inventory file card."""
		if index == 0:  # Load file
			self.__loadInventoryFile()
		elif index == 1:  # Save file
			self.__saveInventoryFile()

	def __loadInventoryFile(self):
		"""Load inventory data from a JSON file and populate the grid."""
		file_path, _ = QFileDialog.getOpenFileName(
			self,
			self.tr("Choose file to load"),
			cfg.get(cfg.exportFolder),
			"JSON Files (*.json)"
		)

		if file_path:
			self.inventoryFileCard.setContent(file_path)
			with open(file_path, 'r', encoding='utf-8') as file:
				try:
					data = json.load(file)
					self.__populateGrid(data)
				except json.JSONDecodeError as e:
					logger.error(f"Error loading JSON file: {e}")

	def __saveInventoryFile(self):
		"""Save current inventory data to a JSON file."""
		file_path = self.inventoryFileCard.getContent()
		if file_path:
			inventory_data = {}
			for i in range(self.gridLayout.count()):
				widget = self.gridLayout.itemAt(i).widget()
				if isinstance(widget, ItemCard):
					item_name = widget.getItemName()
					quantity = widget.getQuantity()
					item_id = itemsID.get(item_name, {}).get('id', None)
					if item_id is not None:
						inventory_data[item_id] = quantity
			
			with open(file_path, 'w', encoding='utf-8') as file:
				json.dump(inventory_data, file, ensure_ascii=False, indent=4)

	def __populateGrid(self, inventory_file):
		"""Populate the grid layout with ItemCard widgets based on the inventory data."""
		columns = 6
		# Clear existing items from the grid
		for i in reversed(range(self.gridLayout.count())): 
			widget = self.gridLayout.itemAt(i).widget()
			if widget:
				widget.setParent(None)

		for index, item_id in enumerate(inventory_file):
			image, name = self._getItemInfoByID(item_id)
			card = ItemCard(image, name, inventory_file[item_id])
			self.gridLayout.addWidget(card, index // columns, index % columns)

	def _getItemInfoByID(self, item_id: int):
		"""Retrieve item image and name by its ID."""
		for _, info in itemsID.items():
			if info['id'] == int(item_id):
				return info['image'], info['name']
		return 'None', 'None'
