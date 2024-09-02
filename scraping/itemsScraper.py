import time
import mss
import cv2
import pytesseract
import pydirectinput
import numpy as np

from scraping.utils import itemsID
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
		int(1305 / 1920 * WIDTH),
		int(116 / 1080 * HEIGHT),
		int(545 / 1920 * WIDTH),
		int(55 / 1080 * HEIGHT)
	)
	xValue, yValue, wValue, hValue = (
		int(1655 / 1920 * WIDTH),
		int(320 / 1080 * HEIGHT),
		int(190 / 1920 * WIDTH),
		int(40 / 1080 * HEIGHT)
	)

	xDescription, yDescription, wDescription, hDescription = (
		int(1296 / 1920 * WIDTH),
		int(114 / 1080 * HEIGHT),
		int(558 / 1920 * WIDTH),
		int(820 / 1080 * HEIGHT)
	)

	x_start, y_start = (
		int(205 / 1920 * WIDTH),
		int(122 / 1080 * HEIGHT)
	)
	w, h = (
		int(151 / 1920 * WIDTH),
		int(181 / 1080 * HEIGHT)
	)

	# Space between rows and columns
	dx = w + int(16 / 1920 * WIDTH) # columns
	dy = h + int(24 / 1080 * HEIGHT) # rows

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
				time.sleep(0.2)
				
				with mss.mss() as sct:
					image = np.array(sct.grab((0, 0, WIDTH, HEIGHT)))
					image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		
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
			time.sleep(0.2)
			
			with mss.mss() as sct:
				image = np.array(sct.grab((0, 0, WIDTH, HEIGHT)))
				image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			
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