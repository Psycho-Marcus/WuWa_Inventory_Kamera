import string
import numpy as np
from difflib import get_close_matches as getMatches

from scraping.utils import weaponsID, itemsID
from scraping.utils import (
    screenshot, convertToBlackWhite, imageToString,
    WindowsInputController
)
from game.screenInfo import ScreenInfo
from properties.config import cfg

# Constants
ROWS, COLS = 4, 6
WEAPON_ASCENSION_LEVELS = [20, 40, 50, 60, 70, 80, 90]

def getWeaponPages(screenInfo: ScreenInfo) -> int:
    image = convertToBlackWhite(screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor)[screenInfo.weapons.page.y:screenInfo.weapons.page.y + screenInfo.weapons.page.h, screenInfo.weapons.page.x:screenInfo.weapons.page.x + screenInfo.weapons.page.w])
    weaponCount = imageToString(image, '', allowedChars=string.digits + '/').split('/')[0]
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

def processGridItem(inventory: dict, weapons: list, image: np.ndarray, screenInfo: ScreenInfo, _cache: dict) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:

    nameImage = image[screenInfo.weapons.name.y:screenInfo.weapons.name.y + screenInfo.weapons.name.h, screenInfo.weapons.name.x:screenInfo.weapons.name.x + screenInfo.weapons.name.w]
    nameImage = convertToBlackWhite(nameImage)
    nameHash = hash(nameImage.tobytes())

    if nameHash in _cache:
        name = _cache[nameHash]
    else:
        name = imageToString(nameImage, '', bannedChars=' ').lower()
        result = getMatches(name, weaponsID, 1, 0.9)
        if not result:
            result = getMatches(name, itemsID, 1, 0.9)
            if not result:
                result = [name]
        
        _cache[nameHash] = result[0]
        name = result[0]
    
    if name in itemsID:
        valueImage = image[screenInfo.weapons.value.y:screenInfo.weapons.value.y + screenInfo.weapons.value.h, screenInfo.weapons.value.x:screenInfo.weapons.value.x + screenInfo.weapons.value.w]
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
            levelImage = image[screenInfo.weapons.level.y:screenInfo.weapons.level.y + screenInfo.weapons.level.h, screenInfo.weapons.level.x:screenInfo.weapons.level.x + screenInfo.weapons.level.w]
            # levelImage = convertToBlackWhite(levelImage)
            levelHash = hash(levelImage.tobytes())

            if levelHash in _cache:
                levelText = _cache[levelHash]
            else:
                levelText = imageToString(levelImage, '', allowedChars=string.digits + '/')
                _cache[levelHash] = levelText
            
            if int(levelText.split('/')[0]) >= cfg.get(cfg.weaponsMinLevel):
                rankImage = image[screenInfo.weapons.rank.y:screenInfo.weapons.rank.y + screenInfo.weapons.rank.h, screenInfo.weapons.rank.x:screenInfo.weapons.rank.x + screenInfo.weapons.rank.w]
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

def weaponScraper(controller: WindowsInputController, x: float, y: float, screenInfo: ScreenInfo) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    inventory = dict()
    weapons = list()
    _cache = dict()

    controller.pressKey(cfg.get(cfg.inventoryKeybind), 2, False)
    controller.leftClick(x, y)

    weaponCount, pages = getWeaponPages(screenInfo)
    continueScraping = False

    for page in range(pages):
        for row in range(ROWS):
            for col in range(COLS):
                if page == pages - 1 and (page * (ROWS * COLS) + row * COLS + col) > (page * 24) + (weaponCount % 24):
                    del _cache
                    return inventory, weapons

                center_x = screenInfo.weapons.start.x + (col * (screenInfo.weapons.start.w + screenInfo.offsets.page.x)) + screenInfo.weapons.start.w // 2
                center_y = screenInfo.weapons.start.y + (row * (screenInfo.weapons.start.h + screenInfo.offsets.page.y)) + screenInfo.weapons.start.h // 2
                
                controller.leftClick(center_x, center_y)
                image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor)
                
                continueScraping = processGridItem(inventory, weapons, image, screenInfo, _cache)
                if not continueScraping:
                    del _cache
                    return inventory, weapons

        if page < pages - 1 and continueScraping:
            controller.mouseScroll(screenInfo.scroll.page.y, 1.2)

    del _cache
    return inventory, weapons