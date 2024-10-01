import string
import numpy as np
from difflib import get_close_matches

from scraping.utils import weaponsID, itemsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    convertToBlackWhite, imageToString, mouseScroll,
    leftClick, presskey
)
from properties.config import cfg

# Constants
ROWS, COLS = 4, 6
WEAPON_ASCENSION_LEVELS = [20, 40, 50, 60, 70, 80, 90]

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
        'page': (230, 50, 125, 40),
        'name': (1305, 116, 545, 55),
        'value': (1655, 320, 190, 40),
        'level': (1660, 235, 180, 45),
        'rank': (1300, 530, 115, 50),
        'start': (205, 122, 151, 181),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

def getWeaponPages(roiInfo: ROI_Info) -> int:
    coords = roiInfo.coords['page']
    img = convertToBlackWhite(screenshot(width=roiInfo.width, height=roiInfo.height)[coords.y:coords.y + coords.h, coords.x:coords.x + coords.w])
    weaponCount = imageToString(img, '', allowedChars=string.digits + '/').split('/')[0]
    try:
        return int(weaponCount), int(np.ceil(int(weaponCount) / 24))
    except ValueError:
        return 24, 1

def processItem(name: str, valueText: str) -> tuple[str, int]:
    itemID = itemsID[name]['id']
    try:
        value = int(valueText)
    except ValueError:
        value = 1
    return itemID, value

def processWeapon(name: str, levelText: str, rankText: str) -> dict[str, dict[str, int]]:
    weaponID = weaponsID[name]['id']
    level = levelText.split('/')
    return {
        weaponID: {
            'level': int(level[0]),
            'ascension': WEAPON_ASCENSION_LEVELS.index(int(level[1])),
            'rank': int(rankText)
        }
    }

def processGridItem(inventory: dict, weapons: list, image: np.ndarray, roiInfo: ROI_Info, _cache: dict) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    coords = roiInfo.coords

    nameImage = image[coords['name'].y:coords['name'].y + coords['name'].h, coords['name'].x:coords['name'].x + coords['name'].w]
    nameImage = convertToBlackWhite(nameImage)
    nameHash = hash(nameImage.tobytes())

    if nameHash in _cache:
        name = _cache[nameHash]
    else:
        name = imageToString(nameImage, '', bannedChars=' ').lower()
        result = get_close_matches(name, weaponsID, 1, 0.9)
        if not result:
            result = get_close_matches(name, itemsID, 1, 0.9)
            if not result:
                result = [name]
        
        _cache[nameHash] = result[0]
        name = result[0]
    
    if name in itemsID:
        valueImage = image[coords['value'].y:coords['value'].y + coords['value'].h, coords['value'].x:coords['value'].x + coords['value'].w]
        valueImage = convertToBlackWhite(valueImage)
        valueHash = hash(valueImage.tobytes())

        if valueHash in _cache:
            valueText = _cache[valueHash]
        else:
            valueText = imageToString(valueImage, '', allowedChars=string.digits)
            _cache[valueHash] = valueText
        
        itemID, value = processItem(name, valueText)
        inventory[itemID] = value
        return True
    elif name in weaponsID:
        if weaponsID[name]['rarity'] >= cfg.get(cfg.weaponsMinRarity):
            levelImage = image[coords['level'].y:coords['level'].y + coords['level'].h, coords['level'].x:coords['level'].x + coords['level'].w]
            levelImage = convertToBlackWhite(levelImage)
            levelHash = hash(levelImage.tobytes())

            if levelHash in _cache:
                levelText = _cache[levelHash]
            else:
                levelText = imageToString(levelImage, '', allowedChars=string.digits + '/')
                _cache[levelHash] = levelText
            
            if int(levelText.split('/')[0]) >= cfg.get(cfg.weaponsMinLevel):
                rankImage = image[coords['rank'].y:coords['rank'].y + coords['rank'].h, coords['rank'].x:coords['rank'].x + coords['rank'].w]
                rankImage = convertToBlackWhite(rankImage)
                rankHash = hash(rankImage.tobytes())

                if rankHash in _cache:
                    rankText = _cache[rankHash]
                else:
                    rankText = imageToString(rankImage, '', allowedChars=string.digits)
                    _cache[rankHash] = rankText
                weapons.append(processWeapon(name, levelText, rankText))
                return True
        return False
    return True

def weaponScraper(x: float, y: float, width: int, height: int) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    inventory = dict()
    weapons = list()
    _cache = dict()
    roiInfo = getROI(width, height)

    presskey(cfg.get(cfg.inventoryKeybind), 2, False)
    leftClick(x, y)

    weaponCount, pages = getWeaponPages(roiInfo)
    continueScraping = False

    for page in range(pages):
        for row in range(ROWS):
            for col in range(COLS):
                if page == pages - 1 and (page * (ROWS * COLS) + row * COLS + col) > (page * 24) + (weaponCount % 24):
                    del _cache
                    return inventory, weapons

                startCoords = roiInfo.coords['start']
                center_x = startCoords.x + (col * (startCoords.w + scaleWidth(16, width))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + scaleHeight(24, height))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(width=width, height=height)
                
                continueScraping = processGridItem(inventory, weapons, image, roiInfo, _cache)
                if not continueScraping:
                    del _cache
                    return inventory, weapons

        if page < pages - 1 and continueScraping:
            mouseScroll(-31.25, 1.2)

    del _cache
    return inventory, weapons