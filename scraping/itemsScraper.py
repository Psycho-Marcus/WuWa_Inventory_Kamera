import re
import cv2
import time
import numpy as np
from pathlib import Path
from difflib import get_close_matches as getMatches

from scraping.utils import itemsID
from scraping.utils import (
    screenshot, imageToString, convertToBlackWhite,
    WindowsInputController
)
from game.screenInfo import ScreenInfo
from properties.config import cfg, basePATH

# Constants
ROWS, COLS = 4, 6

def processItem(path: Path, image: np.ndarray, screenInfo: ScreenInfo, _cache: dict) -> tuple[dict[str, int], list[dict]]:
    inventory = {}
    failed = []

    infoImage = image[screenInfo.items.info.y:screenInfo.items.info.y + screenInfo.items.info.h, screenInfo.items.info.x:screenInfo.items.info.x + screenInfo.items.info.w]
    infoImage = convertToBlackWhite(infoImage)
    infoHash = hash(infoImage.tobytes())

    if infoHash in _cache:
        info = _cache[infoHash]
    else:
        info = imageToString(infoImage, bannedChars=' ').lower().split('\n')
        _cache[infoHash] = info
    name = info[0]
    result = getMatches(name, itemsID, 1, 0.9)
    if result: name = result[0]
    
    try: value = re.sub(r'[^0-9]', '', info[2])
    except: value = 1

    try: value = int(value)
    except ValueError: value = 1

    itemID = itemsID.get(name, {'id': None})['id']
    if itemID is not None:
        inventory[itemID] = value
    else:
        path.mkdir(parents=True, exist_ok=True)
        descImage = image[screenInfo.items.description.y:screenInfo.items.description.y + screenInfo.items.description.h, screenInfo.items.description.x:screenInfo.items.description.x + screenInfo.items.description.w]

        imagePath = path / f'_{name}-{time.time()}.png'
        cv2.imwrite(imagePath, descImage)

        failed.append({
            'image': imagePath,
            'owned': value
        })

    return inventory, failed, name

def itemsScraper(START_DATE: str, controller: WindowsInputController, x: int, y: int, screenInfo: ScreenInfo):
    path: Path = basePATH / 'logs' / 'fail' / START_DATE
    
    inventory = dict()
    failed = list()
    encounters = dict()
    _cache = dict()

    controller.pressKey(cfg.get(cfg.inventoryKeybind), 2, False)
    controller.leftClick(x, y)

    isDouble = False
    last = ""

    while not isDouble:
        for row in range(ROWS):
            for col in range(COLS):
                center_x = screenInfo.items.start.x + (col * (screenInfo.items.start.w + screenInfo.offsets.page.x)) + screenInfo.items.start.w // 2
                center_y = screenInfo.items.start.y + (row * (screenInfo.items.start.h + screenInfo.offsets.page.y)) + screenInfo.items.start.h // 2
                
                controller.leftClick(center_x, center_y)
                image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor)
                
                item_inventory, item_failed, name = processItem(path, image, screenInfo, _cache)
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
            controller.mouseScroll(screenInfo.scroll.page.y, 1.2)

    # Process last page
    isDouble = False
    for row in range(ROWS - 1, -1, -1):
        for col in range(COLS - 1, -1, -1):
            center_x = screenInfo.items.start.x + (col * (screenInfo.items.start.w + screenInfo.offsets.page.x)) + screenInfo.items.start.w // 2
            center_y = screenInfo.items.start.y + (row * (screenInfo.items.start.h + screenInfo.offsets.page.y)) + screenInfo.items.start.h // 2
            
            controller.leftClick(center_x, center_y)
            image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor)
            
            item_inventory, item_failed, name = processItem(path, image, screenInfo, _cache)
            
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