import os
import cv2
import time
import pytesseract
import numpy as np

from scraping.utils import itemsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    mouseScroll, leftClick, presskey
)
from properties.config import cfg, basePATH

# Constants
ROWS, COLS = 4, 6

class Coordinates:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class ROI_Info:
    def __init__(self, width: int, height: int, coords: dict[str, Coordinates]):
        self.width = width
        self.height = height
        self.coords = coords

def scaleCoordinates(coords: dict[str, tuple[int, int, int, int]], width: int, height: int) -> dict[str, Coordinates]:
    return {
        key: Coordinates(
            scaleWidth(x, width),
            scaleHeight(y, height),
            scaleWidth(w, width),
            scaleHeight(h, height)
        )
        for key, (x, y, w, h) in coords.items()
    }

def getROI(width: int, height: int) -> ROI_Info:
    unscaled_coords = {
        'name': (1305, 116, 545, 55),
        'value': (1655, 320, 190, 40),
        'description': (1296, 114, 558, 820),
        'start': (205, 122, 151, 181),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))


def processItem(path: str, image: np.ndarray, roiInfo: ROI_Info) -> tuple[dict[str, int], list[dict]]:
    inventory = {}
    failed = []
    coords = roiInfo.coords

    name = pytesseract.image_to_string(image[coords['name'].y:coords['name'].y + coords['name'].h, coords['name'].x:coords['name'].x + coords['name'].w]).strip()
    value_text = pytesseract.image_to_string(image[coords['value'].y:coords['value'].y + coords['value'].h, coords['value'].x:coords['value'].x + coords['value'].w]).strip().split(' ', 1)[1]

    try:
        value = int(value_text)
    except ValueError:
        value = 1

    itemID = itemsID.get(name, {'id': None})['id']
    if itemID is not None:
        inventory[itemID] = value
    else:
        os.makedirs(path, exist_ok=True)
        descImage = image[coords['description'].y:coords['description'].y + coords['description'].h, coords['description'].x:coords['description'].x + coords['description'].w]

        imagePath = os.path.join(path, f'_{name}-{time.time()}.png')
        cv2.imwrite(imagePath, descImage)

        failed.append({
            'image': imagePath,
            'owned': value
        })

    return inventory, failed, name

def itemsScraper(START_DATE: str, x: int, y: int, WIDTH: int, HEIGHT: int):
    path = os.path.join(basePATH, 'logs', 'fail', START_DATE)
    
    inventory = {}
    failed = []
    encounters = {}
    roiInfo = getROI(WIDTH, HEIGHT)

    presskey(cfg.get(cfg.inventoryKeybind), 2, False)
    leftClick(x, y)

    isDouble = False
    last = ""

    while not isDouble:
        for row in range(ROWS):
            for col in range(COLS):
                startCoords = roiInfo.coords['start']
                center_x = startCoords.x + (col * (startCoords.w + scaleWidth(16, WIDTH))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + scaleHeight(24, HEIGHT))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(0, 0, WIDTH, HEIGHT)
                
                item_inventory, item_failed, name = processItem(path, image, roiInfo)
                inventory.update(item_inventory)
                failed.extend(item_failed)

                value = inventory.get(itemsID.get(name, {'id': None})['id'], 1)
                maxEncounters = np.ceil(value / 999)
                encounters[name] = encounters.get(name, 0) + 1

                if encounters[name] > maxEncounters:
                    last = name
                    isDouble = True
                    break
            if isDouble:
                break
        
        if not isDouble:
            mouseScroll(-31.25, 1.2)

    # Process last page
    isDouble = False
    for row in range(ROWS - 1, -1, -1):
        for col in range(COLS - 1, -1, -1):
            startCoords = roiInfo.coords['start']
            center_x = startCoords.x + (col * (startCoords.w + scaleWidth(16, WIDTH))) + startCoords.w // 2
            center_y = startCoords.y + (row * (startCoords.h + scaleHeight(24, HEIGHT))) + startCoords.h // 2
            
            leftClick(center_x, center_y)
            image = screenshot(0, 0, WIDTH, HEIGHT)
            
            item_inventory, item_failed, name = processItem(path, image, roiInfo)
            
            if name == last:
                continue

            inventory.update(item_inventory)
            failed.extend(item_failed)

            value = inventory.get(itemsID.get(name, {'id': None})['id'], 1)
            maxEncounters = np.ceil(value / 999)
            encounters[name] = encounters.get(name, 0) + 1

            if encounters[name] > maxEncounters:
                isDouble = True
                break
        if isDouble:
            break

    return inventory, failed