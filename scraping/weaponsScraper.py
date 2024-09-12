import string
import pytesseract
import numpy as np

from scraping.utils import weaponsID, itemsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    convertToBlackWhite, mouseScroll, leftClick,
    presskey
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
        'page': (230, 55, 125, 30),
        'name': (1305, 116, 545, 55),
        'value': (1655, 320, 190, 40),
        'level': (1660, 240, 175, 35),
        'rank': (1305, 540, 105, 30),
        'start': (205, 122, 151, 181),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

def getWeaponPages(roiInfo: ROI_Info) -> int:
    coords = roiInfo.coords['page']
    img = convertToBlackWhite(screenshot(0, 0, roiInfo.width, roiInfo.height)[coords.y:coords.y + coords.h, coords.x:coords.x + coords.w])
    weaponCount = pytesseract.image_to_string(img, config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/').split('/')[0]
    try:
        return int(weaponCount), int(np.ceil(int(weaponCount) / 24))
    except ValueError:
        return 24, 1

def processItem(name: str, value_text: str) -> tuple[str, int]:
    itemID = itemsID[name]['id']
    try:
        value = int(value_text.split(' ', 1)[1])
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

def processGridItem(image: np.ndarray, roiInfo: ROI_Info) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    inventory = {}
    weapons = []
    coords = roiInfo.coords

    name = pytesseract.image_to_string(image[coords['name'].y:coords['name'].y + coords['name'].h, coords['name'].x:coords['name'].x + coords['name'].w]).strip()
    
    if name in itemsID:
        value_text = pytesseract.image_to_string(image[coords['value'].y:coords['value'].y + coords['value'].h, coords['value'].x:coords['value'].x + coords['value'].w]).strip()
        itemID, value = processItem(name, value_text)
        inventory[itemID] = value
    elif name in weaponsID:
        if weaponsID[name]['rarity'] >= cfg.get(cfg.weaponsMinRarity):
            levelText = pytesseract.image_to_string(image[coords['level'].y:coords['level'].y + coords['level'].h, coords['level'].x:coords['level'].x + coords['level'].w], config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/')
            
            if int(levelText.split('/')[0]) >= cfg.get(cfg.weaponsMinLevel):
                rankText = pytesseract.image_to_string(image[coords['rank'].y:coords['rank'].y + coords['rank'].h, coords['rank'].x:coords['rank'].x + coords['rank'].w], config=f'--psm 7 -c tessedit_char_whitelist={string.digits}')
                weapons.append(processWeapon(name, levelText, rankText))
                return inventory, weapons, True
        else:
            return inventory, weapons, False

    return inventory, weapons, True

def weaponScraper(x: float, y: float, width: int, height: int) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    inventory = {}
    weapons = []
    roiInfo = getROI(width, height)

    presskey(cfg.get(cfg.inventoryKeybind), 2, False)
    leftClick(x, y)

    weaponCount, pages = getWeaponPages(roiInfo)
    continueScraping = False

    for page in range(pages):
        for row in range(ROWS):
            for col in range(COLS):
                if page == pages - 1 and (page * (ROWS * COLS) + row * COLS + col) > (page * 24) + (weaponCount % 24):
                    continueScraping = False
                    break

                startCoords = roiInfo.coords['start']
                center_x = startCoords.x + (col * (startCoords.w + scaleWidth(16, width))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + scaleHeight(24, height))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(0, 0, width, height)
                
                itemInventory, itemWeapons, continueScraping = processGridItem(image, roiInfo)
                inventory.update(itemInventory)
                weapons.extend(itemWeapons)
            if not continueScraping:
                return inventory, weapons

        if page < pages - 1 and continueScraping:
            mouseScroll(-31.25, 1.2)

    return inventory, weapons