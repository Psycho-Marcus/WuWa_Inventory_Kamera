import string
import numpy as np
from difflib import get_close_matches

from scraping.utils import weaponsID, itemsID
from scraping.utils import (
    screenshot, convertToBlackWhite, imageToString,
    mouseScroll, leftClick, presskey
)
from game.screenInfo import ScreenInfo
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
        'page': ((200, 175), (50, 40), 130, 40),
        'name': ((1305, 1140), (116, 152), (545, 480), (55, 50)),
        'value': (1655, 320, 190, 40),
        'level': ((1660, 1435), (235, 255), 180, 45),
        'rank': ((1300, 1135), (530, 510), (115, 100), 50),
        'start': ((205, 180), (122, 104), (151, 130), (181, 162)),
    }
    return ROI_Info(screenInfo.width, screenInfo.height, scaleCoordinates(unscaled_coords, screenInfo))

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
            # levelImage = convertToBlackWhite(levelImage)
            import cv2
            cv2.imwrite('./_level.png', levelImage)
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

def weaponScraper(x: float, y: float, screenInfo: ScreenInfo) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    inventory = dict()
    weapons = list()
    _cache = dict()
    roiInfo = getROI(screenInfo)

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
                center_x = startCoords.x + (col * (startCoords.w + screenInfo.scaleWidth(16))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + screenInfo.scaleHeight(24))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(width=screenInfo.width, height=screenInfo.height)
                
                continueScraping = processGridItem(inventory, weapons, image, roiInfo, _cache)
                if not continueScraping:
                    del _cache
                    return inventory, weapons

        if page < pages - 1 and continueScraping:
            mouseScroll(screenInfo.scaleHeight(-31.25, -31.75), 1.2)

    del _cache
    return inventory, weapons