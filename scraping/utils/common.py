import os
import json
import mss
import cv2
import pydirectinput
import numpy as np

from properties.config import cfg, INVENTORY, CHARACTERS, START_DATE

try: itemsID: dict = json.load(open('./data/items.json'))
except: itemsID: dict = dict()

try: charactersID: dict = json.load(open('./data/characters.json'))
except: charactersID: dict = dict()

try: weaponsID: dict = json.load(open('./data/weapons.json'))
except: weaponsID: dict = dict()

def pressEscape():
	"""Simulates pressing the ESC key."""
	pydirectinput.press('ESC')

def savingScraped():

	savePATH = os.path.join(cfg.get(cfg.exportFolder), START_DATE)

	if INVENTORY or CHARACTERS:
		os.makedirs(savePATH, exist_ok=True)

	if INVENTORY != dict():
		json.dump(INVENTORY, open(os.path.join(savePATH, f'inventory_wuwainventorykamera.json'), 'w', encoding='UTF-8'))
	
	if CHARACTERS != dict():
		json.dump(CHARACTERS, open(os.path.join(savePATH, f'characters_wuwainventorykamera.json'), 'w', encoding='UTF-8'))


def scaleWidth(value, width):
    return int(value / 1920 * width)

def scaleHeight(value, height):
    return int(value / 1080 * height)


def screenshot(left: int = 0, top: int = 0, width: int = 0, height: int = 0, bw: bool = False):
	with mss.mss() as sct:
		image = np.array(sct.grab((left, top, width, height)))
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	
	if bw:
		image = convertToBlackWhite(image)

	return image

def convertToBlackWhite(image):
	gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	contrasted = clahe.apply(gray)
	
	blurred = cv2.GaussianBlur(contrasted, (3, 3), 0)
	
	_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	
	if np.mean(thresh) > 127: thresh = cv2.bitwise_not(thresh)
	
	kernel = np.ones((2,2), np.uint8)
	morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
	
	sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
	sharpened = cv2.filter2D(morph, -1, sharpen_kernel)

	return sharpened