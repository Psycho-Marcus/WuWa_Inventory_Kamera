import json
import os
import pydirectinput

from properties.config import cfg, INVENTORY, START_DATE

try: itemsID: dict = json.load(open('./data/items.json'))
except: itemsID: dict = dict()

def pressEscape():
	"""Simulates pressing the ESC key."""
	pydirectinput.press('ESC')

def savingScraped():
	global INVENTORY

	json.dump(INVENTORY, open(os.path.join(cfg.get(cfg.exportFolder), f'wuwainventorykamera_{START_DATE}.json'), 'w', encoding='UTF-8'))