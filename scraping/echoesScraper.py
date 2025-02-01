import os
import cv2
import string
import numpy as np
from difflib import get_close_matches as getMatches
from collections import defaultdict

from scraping.utils import (
    echoesID, echoStats, sonataName
)
from scraping.utils import (
    screenshot, imageToString, convertToBlackWhite,
    WindowsInputController
)
from game.screenInfo import ScreenInfo
from properties.config import cfg

# Constants
ROWS, COLS = 4, 6

def matchStats(text):
    stats = set(echoStats)
    results = []
    i = 0
    while i < len(text):
        if i < len(text) - 1:
            combinedWord = text[i] + text[i + 1]
            if combinedWord in stats:
                results.append(combinedWord)
                i += 2
                continue
        if text[i] in stats:
            results.append(text[i])
        i += 1
    return results

def setupRarityDetection():
    rarityColors = {
        5: np.array([90, 230, 255]),
        4: np.array([255, 109, 202]),
        3: np.array([211, 180, 89]),
        2: np.array([94, 195, 92]),
        1: np.array([225, 236, 239])
    }

    tolerance = 10
    bounds = {rarity: (color - tolerance, color + tolerance) for rarity, color in rarityColors.items()}

    return bounds

RARITY_BOUNDS = setupRarityDetection()

def getRarity(image: np.ndarray):
    for rarity, (lower, upper) in RARITY_BOUNDS.items():
        if np.any(cv2.inRange(image, lower, upper)):
            return rarity
    return 1

def getEchoPages(screenInfo: ScreenInfo) -> int:
    image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor)[screenInfo.echoes.page.y:screenInfo.echoes.page.y + screenInfo.echoes.page.h, screenInfo.echoes.page.x:screenInfo.echoes.page.x + screenInfo.echoes.page.w]
    echoCount = imageToString(image, allowedChars=string.digits + '/').split('/')[0]
    
    try: return int(echoCount), int(np.ceil(int(echoCount) / 24))
    except ValueError: return 24, 1

def processEcho(name: str, level: int, tuneLv: int, sonata: str, rarity: int, stats: dict) -> dict[str, dict[int, int, dict]]:
    result = getMatches(name, echoesID, 1, 0.9)
    if result: name = result[0]
    
    echoID = str(echoesID.get(name, name))
    return {
        echoID: {
            'level': level,
            'tuneLv': tuneLv,
            'sonata': sonata,
            'rarity': rarity,
            'stats': stats
        }
    }

def processStats(image: np.ndarray, screenInfo: ScreenInfo, _cache: dict) -> dict[str:int]:
    stats = defaultdict(dict)
    tuneLv = 0

    nameImage = image[
        screenInfo.echoes.fullStatsName.y:screenInfo.echoes.fullStatsName.y + screenInfo.echoes.fullStatsName.h,
        screenInfo.echoes.fullStatsName.x:screenInfo.echoes.fullStatsName.x + screenInfo.echoes.fullStatsName.w
    ]
    nameImage = convertToBlackWhite(nameImage)
    nameHash = hash(nameImage.tobytes())

    valueImage = image[
        screenInfo.echoes.fullStatsValue.y:screenInfo.echoes.fullStatsValue.y + screenInfo.echoes.fullStatsValue.h,
        screenInfo.echoes.fullStatsValue.x:screenInfo.echoes.fullStatsValue.x + screenInfo.echoes.fullStatsValue.w
    ]
    valueImage = convertToBlackWhite(valueImage)
    valueHash = hash(valueImage.tobytes())

    if nameHash in _cache:
        names = _cache[nameHash]
    else:
        names = imageToString(nameImage, allowedChars=string.ascii_letters).lower().split('\n')
        names = matchStats(names)
        _cache[nameHash] = names

    if valueHash in _cache:
        values = _cache[valueHash]
    else:
        values = imageToString(valueImage, allowedChars=string.digits + '.%').split()
        _cache[valueHash] = values
    tuneLv = max(0, len(values) - 2)


    for index, (statName, statValue) in enumerate(zip(names, values)):
        statName = echoStats.get(statName, statName)

        if index < 2: stat = 'main'
        else: stat = 'sub'
        
        try:
            if statValue.endswith('%'):
                stats[stat].update({f"{statName}%": float(statValue[:-1])})
            else:
                stats[stat].update({statName: int(statValue)})
        except:
            stats[stat].update({statName: statValue})

    return tuneLv, dict(stats)

def getSonata(controller: WindowsInputController, screenInfo: ScreenInfo, _cache: dict):
    controller.moveMouse(screenInfo.echoes.mouseMovement.x, screenInfo.echoes.mouseMovement.y, .2)
    controller.mouseScroll(-screenInfo.scroll.sonata.y, .3)
    image = screenshot(screenInfo.echoes.sonata.x, screenInfo.echoes.sonata.y, screenInfo.echoes.sonata.w, screenInfo.echoes.sonata.h, monitor=screenInfo.monitor)
    sonataHash = hash(image.tobytes())

    if sonataHash in _cache:
        sonata = _cache[sonataHash]
    else:
        sonata = imageToString(image, '', bannedChars=' ').lower()
        for name in sonataName:
            if name in sonata:
                _cache[sonataHash] = name
                sonata = name
                break
    
    controller.moveMouse(screenInfo.echoes.mouseMovement.x, screenInfo.echoes.mouseMovement.y, .2)
    controller.mouseScroll(screenInfo.scroll.sonata.y, .3)
    return sonata

def processGridEcho(controller: WindowsInputController, screenInfo: ScreenInfo, echoes: list, image: np.ndarray, _cache: dict[str, list]) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:

    echoCard = image[screenInfo.echoes.echoCard.y:screenInfo.echoes.echoCard.y + screenInfo.echoes.echoCard.h, screenInfo.echoes.echoCard.x:screenInfo.echoes.echoCard.x + screenInfo.echoes.echoCard.w]
    echoHash = hash(echoCard.tobytes())
    if echoHash in _cache:
        info = _cache[echoHash]
    else:
        info = [imageToString(echoCard, '', bannedChars=' +').lower().split('\n')]
        _cache[echoHash] = info
    name = info[0][0]
    
    if name in echoesID:
        try:
            rarity = info[1][0]
        except:
            rarity = getRarity(echoCard)
            _cache[echoHash].append(rarity)
        
        if rarity >= cfg.get(cfg.echoMinRarity):
            levelText = info[0][2]
            
            try: level = int(levelText)
            except ValueError: level = 0
            level = min(25, level)

            if level >= cfg.get(cfg.echoMinLevel):
                tuneLv, stats = processStats(image, screenInfo, _cache)
                sonata = getSonata(controller, screenInfo, _cache)
                echoes.append(processEcho(name, level, tuneLv, sonata, rarity, stats))
                return True
        return False

    return True

def echoScraper(controller: WindowsInputController, x: float, y: float, screenInfo: ScreenInfo) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    echoes = list()
    _cache = dict()

    controller.pressKey(cfg.get(cfg.inventoryKeybind), 2, False)
    controller.leftClick(x, y)

    echoCount, pages = getEchoPages(screenInfo)
    continueScraping = False

    for page in range(pages):
        for row in range(ROWS):
            for col in range(COLS):
                if page == pages - 1 and (page * (ROWS * COLS) + row * COLS + col) > (page * 24) + (echoCount % 24):
                    del _cache
                    return echoes
                center_x = screenInfo.echoes.start.x + (col * (screenInfo.echoes.start.w + screenInfo.offsets.page.x)) + screenInfo.echoes.start.w // 2
                center_y = screenInfo.echoes.start.y + (row * (screenInfo.echoes.start.h + screenInfo.offsets.page.y)) + screenInfo.echoes.start.h // 2
                
                controller.leftClick(center_x, center_y)
                image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor)
                
                continueScraping = processGridEcho(controller, screenInfo, echoes, image, _cache)
                if not continueScraping:
                    del _cache
                    return echoes

        if page < pages - 1 and continueScraping:
            controller.mouseScroll(screenInfo.scroll.page.y, 1.2)

    del _cache
    return echoes
