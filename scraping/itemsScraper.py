import time
import pytesseract
import pydirectinput
import numpy as np

from scraping.utils import itemsID
from scraping.utils import scaleWidth, scaleHeight, screenshot
from properties.config import cfg

def itemsScraper(
	x: int,
	y: int,
	WIDTH: int,
	HEIGHT: int
):
	inventory = dict()
	failed = list()

	pydirectinput.press(cfg.get(cfg.inventoryKeybind))
	time.sleep(2)
	
	pydirectinput.leftClick(x=x, y=y)
	time.sleep(.5)

	xName, yName, wName, hName = (
		scaleWidth(1305, WIDTH),
		scaleHeight(116, HEIGHT),
		scaleWidth(545, WIDTH),
		scaleHeight(55, HEIGHT)
	)
	xValue, yValue, wValue, hValue = (
		scaleWidth(1655, WIDTH),
		scaleHeight(320, HEIGHT),
		scaleWidth(190, WIDTH),
		scaleHeight(40, HEIGHT)
	)

	xDescription, yDescription, wDescription, hDescription = (
		scaleWidth(1296, WIDTH),
		scaleHeight(114, HEIGHT),
		scaleWidth(558, WIDTH),
		scaleHeight(820, HEIGHT)
	)

	x_start, y_start = (
		scaleWidth(205, WIDTH),
		scaleHeight(122, HEIGHT)
	)
	w, h = (
		scaleWidth(151, WIDTH),
		scaleHeight(181, HEIGHT)
	)

	# Space between rows and columns
	dx = w + scaleWidth(16, WIDTH) # columns
	dy = h + scaleHeight(24, HEIGHT) # rows

	isDouble = False
	encounters = dict()
	last = str()

	while not isDouble:
		for row in range(4):
			for col in range(6):
				x = np.ceil(x_start + (col*dx) - (col/2))
				y = np.ceil(y_start + (row*dy) - (row/2))

				# Calculate center of rectangle
				center_x = x + w // 2
				center_y = y + h // 2
				pydirectinput.leftClick(center_x, center_y)
				time.sleep(.2)
				
				image = screenshot(0, 0, WIDTH, HEIGHT)
		
				name = pytesseract.image_to_string(image[yName:yName+hName, xName:xName+wName]).strip()
				value = pytesseract.image_to_string(image[yValue:yValue+hValue, xValue:xValue+wValue]).strip().split(' ', 1)[1]

				try: value = int(value)
				except: value = 1

				maxEncounters = np.ceil(value/999)
				
				encounters[name] = encounters.get(name, 0) + 1
				itemID = itemsID.get(name, {'id': None})['id']
				if itemID is not None:
					inventory[itemID] = value
				else:
					failed.append({
						'image': np.ascontiguousarray(image[yDescription:yDescription+hDescription, xDescription:xDescription+wDescription]),
						'owned': value
					})
				
				if encounters[name] > maxEncounters:
					last = name
					isDouble = True
					break
			if isDouble: break
		
		if not isDouble:
			pydirectinput.scroll(-31)
			time.sleep(1.2)

	isDouble = False

	## LAST PAGE
	for row in range(4 - 1, -1, -1):
		for col in range(6 - 1, -1, -1):
			y = np.ceil(y_start + (row*dy) - (row/2))
			x = np.ceil(x_start + (col*dx) - (col/2))

			# Calculate center of rectangle
			center_x = x + w // 2
			center_y = y + h // 2
			pydirectinput.leftClick(center_x, center_y)
			time.sleep(.2)
			
			image = screenshot(0, 0, WIDTH, HEIGHT)
			
			name = pytesseract.image_to_string(image[yName:yName+hName, xName:xName+wName]).strip()
			value = pytesseract.image_to_string(image[yValue:yValue+hValue, xValue:xValue+wValue]).strip().split(' ', 1)[1]

			if name == last: continue

			try: value = int(value)
			except: value = 1

			maxEncounters = np.ceil(value/999)
			
			encounters[name] = encounters.get(name, 0) + 1
			itemID = itemsID.get(name, {'id': None})['id']

			if itemID is not None: inventory[itemID] = value
			else:
				failed.append({
					'image': np.ascontiguousarray(image[yDescription:yDescription+hDescription, xDescription:xDescription+wDescription]),
					'owned': value
				})
			
			if encounters[name] > maxEncounters:
				isDouble = True
				break
		if isDouble: break
	
	return (inventory, failed)