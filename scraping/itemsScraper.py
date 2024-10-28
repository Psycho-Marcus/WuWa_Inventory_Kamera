import os
import re
import cv2
import time
import numpy as np
from difflib import get_close_matches

from scraping.utils import itemsID
from scraping.utils import (
    screenshot, mouseScroll, leftClick,
    presskey, imageToString, convertToBlackWhite
)
from game.screenInfo import ScreenInfo
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

def scaleCoordinates(coords: dict[str, tuple[int, int, int, int]], screenInfo: ScreenInfo) -> dict[str, Coordinates]:
    return {
        key: Coordinates(
            screenInfo.scaleWidth(x),
            screenInfo.scaleHeight(y),
            screenInfo.scaleWidth(w),
            screenInfo.scaleHeight(h)
        )
        for key, (x, y, w, h) in coords.items()
    }

def getROI(screenInfo: ScreenInfo) -> ROI_Info:
    unscaled_coords = {
        'info': ((1296, 1136), (114, 154), (558, 485), (278, 240)),
        'description': ((1296, 1136), (114, 154), (558, 485), (820, 715)),
        'start': ((205, 180), (122, 104), (151, 130), (181, 162)),
    }
    return ROI_Info(screenInfo.width, screenInfo.height, scaleCoordinates(unscaled_coords, screenInfo))


def processItem(path: str, image: np.ndarray, roiInfo: ROI_Info, _cache: dict) -> tuple[dict[str, int], list[dict]]:
    inventory = {}
    failed = []
    coords = roiInfo.coords

    infoImage = image[coords['info'].y:coords['info'].y + coords['info'].h, coords['info'].x:coords['info'].x + coords['info'].w]
    infoImage = convertToBlackWhite(infoImage)
    infoHash = hash(infoImage.tobytes())

    if infoHash in _cache:
        info = _cache[infoHash]
    else:
        info = imageToString(infoImage, bannedChars=' ').lower().split('\n')
        _cache[infoHash] = info
    name = info[0]
    result = get_close_matches(name, itemsID, 1, 0.9)
    if result: name = result[0]
    
    value = re.sub(r'[^0-9]', '', info[2])

    try:
        value = int(value)
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

def itemsScraper(START_DATE: str, x: int, y: int, screenInfo: ScreenInfo):
    path = os.path.join(basePATH, 'logs', 'fail', START_DATE)
    
    inventory = dict()
    failed = list()
    encounters = dict()
    _cache = dict()
    roiInfo = getROI(screenInfo)

    presskey(cfg.get(cfg.inventoryKeybind), 2, False)
    leftClick(x, y)

    isDouble = False
    last = ""

    while not isDouble:
        for row in range(ROWS):
            for col in range(COLS):
                startCoords = roiInfo.coords['start']
                center_x = startCoords.x + (col * (startCoords.w + screenInfo.scaleWidth(16))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + screenInfo.scaleHeight(24))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(width=screenInfo.width, height=screenInfo.height)
                
                item_inventory, item_failed, name = processItem(path, image, roiInfo, _cache)
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
            mouseScroll(screenInfo.scaleHeight((-31.25, -31.75)), 1.2)

    # Process last page
    isDouble = False
    for row in range(ROWS - 1, -1, -1):
        for col in range(COLS - 1, -1, -1):
            startCoords = roiInfo.coords['start']
            center_x = startCoords.x + (col * (startCoords.w + screenInfo.scaleWidth(16))) + startCoords.w // 2
            center_y = startCoords.y + (row * (startCoords.h + screenInfo.scaleHeight(24))) + startCoords.h // 2
            
            leftClick(center_x, center_y)
            image = screenshot(width=screenInfo.width, height=screenInfo.height)
            
            item_inventory, item_failed, name = processItem(path, image, roiInfo, _cache)
            
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
    
    del _cache
    return inventory, failed