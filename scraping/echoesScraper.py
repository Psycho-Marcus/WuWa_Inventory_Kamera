import os
import cv2
import string
import numpy as np
from difflib import get_close_matches
from collections import defaultdict

from scraping.utils import (
    echoesID, echoStats, sonataName
)
from scraping.utils import (
    screenshot, imageToString, convertToBlackWhite,
    moveMouse, mouseScroll, leftClick,
    presskey
)
from game.screenInfo import ScreenInfo
from properties.config import cfg

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
        'page': ((200, 175), (50, 40), 130, 40),
        'start': ((205, 180), (122, 104), (151, 130), (181, 162)),
        'echoCard': ((1296, 1136), (114, 152), (558, 486), 170),
        'sonata': ((1298, 1135), (397, 400), (554, 486), (467, 408)),
        'fullStatsName': ((1380, 1200), (430, 420), (360, 320), 380),
        'fullStatsValue': ((1740, 1510), (430, 420), 100, 380),
    }
    return ROI_Info(screenInfo.width, screenInfo.height, scaleCoordinates(unscaled_coords, screenInfo))

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

def getEchoPages(roiInfo: ROI_Info) -> int:
    coords = roiInfo.coords['page']
    image = screenshot(width=roiInfo.width, height=roiInfo.height)[coords.y:coords.y + coords.h, coords.x:coords.x + coords.w]
    echoCount = imageToString(image, allowedChars=string.digits + '/').split('/')[0]
    
    try: return int(echoCount), int(np.ceil(int(echoCount) / 24))
    except ValueError: return 24, 1

def processEcho(name: str, level: int, tuneLv: int, sonata: str, rarity: int, stats: dict) -> dict[str, dict[int, int, dict]]:
    result = get_close_matches(name, echoesID, 1, 0.9)
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

def processStats(image: np.ndarray, roiInfo: ROI_Info, _cache: dict) -> dict[str:int]:
    stats = defaultdict(dict)
    coords = roiInfo.coords
    tuneLv = 0

    nameImage = image[
        coords['fullStatsName'].y:coords['fullStatsName'].y + coords['fullStatsName'].h,
        coords['fullStatsName'].x:coords['fullStatsName'].x + coords['fullStatsName'].w
    ]
    nameImage = convertToBlackWhite(nameImage)
    nameHash = hash(nameImage.tobytes())

    valueImage = image[
        coords['fullStatsValue'].y:coords['fullStatsValue'].y + coords['fullStatsValue'].h,
        coords['fullStatsValue'].x:coords['fullStatsValue'].x + coords['fullStatsValue'].w
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

def getSonata(screenInfo: ScreenInfo, coords: dict[str, Coordinates], _cache: dict):
    moveMouse(screenInfo.scaleWidth(1576.5), screenInfo.scaleHeight(665.5), .2)
    mouseScroll(-70, .3)
    image = screenshot(coords['sonata'].x, coords['sonata'].y, coords['sonata'].w, coords['sonata'].h)
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
    
    moveMouse(screenInfo.scaleWidth(1576.5), screenInfo.scaleHeight(665.5), .2)
    mouseScroll(70, .3)
    return sonata

def processGridEcho(screenInfo: ScreenInfo, echoes: list, image: np.ndarray, roiInfo: ROI_Info, _cache: dict[str, list]) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    coords = roiInfo.coords

    echoCard = image[coords['echoCard'].y:coords['echoCard'].y + coords['echoCard'].h, coords['echoCard'].x:coords['echoCard'].x + coords['echoCard'].w]
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
                tuneLv, stats = processStats(image, roiInfo, _cache)
                sonata = getSonata(screenInfo, coords, _cache)
                echoes.append(processEcho(name, level, tuneLv, sonata, rarity, stats))
                return True
        return False

    return True

def echoScraper(x: float, y: float, screenInfo: ScreenInfo) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    echoes = list()
    _cache = dict()
    roiInfo = getROI(screenInfo)
    scrollValue = -31.25

    presskey(cfg.get(cfg.inventoryKeybind), 2, False)
    leftClick(x, y)

    echoCount, pages = getEchoPages(roiInfo)
    continueScraping = False

    for page in range(pages):
        for row in range(ROWS):
            for col in range(COLS):
                if page == pages - 1 and (page * (ROWS * COLS) + row * COLS + col) > (page * 24) + (echoCount % 24):
                    del _cache
                    return echoes

                startCoords = roiInfo.coords['start']
                center_x = startCoords.x + (col * (startCoords.w + screenInfo.scaleWidth(16))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + screenInfo.scaleHeight(24))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(width=screenInfo.width, height=screenInfo.height)
                
                continueScraping = processGridEcho(screenInfo, echoes, image, roiInfo, _cache)
                if not continueScraping:
                    del _cache
                    return echoes

        if page < pages - 1 and continueScraping:
            mouseScroll(scrollValue, 1.2)

    del _cache
    return echoes
