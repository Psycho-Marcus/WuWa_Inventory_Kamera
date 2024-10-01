import cv2
import string
import numpy as np
from difflib import get_close_matches
from collections import defaultdict

from scraping.utils import echoesID, echoStats
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    imageToString, convertToBlackWhite, mouseScroll,
    leftClick, presskey
)
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
        'page': (200, 50, 130, 40),
        'start': (205, 122, 151, 181),
        'echoCard': (1296, 114, 558, 170),
        'fullStatsName': (1380, 430, 360, 380),
        'fullStatsValue': (1740, 430, 100, 380),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

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

def processEcho(name: str, level: int, tuneLv: int, rarity: int, stats: dict) -> dict[str, dict[int, int, dict]]:
    result = get_close_matches(name, echoesID, 1, 0.9)
    if result: name = result[0]
    
    echoID = str(echoesID.get(name, name))
    return {
        echoID: {
            'level': level,
            'tuneLv': tuneLv,
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
        
        if statValue.endswith('%'):
            stats[stat].update({f"{statName}%": float(statValue[:-1])})
        else:
            stats[stat].update({statName: int(statValue)})

    return tuneLv, dict(stats)

def processGridEcho(echoes: list, image: np.ndarray, roiInfo: ROI_Info, _cache: dict) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
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
        if echoHash in _cache:
            try:
                rarity = info[1][0]
            except:
                rarity = getRarity(echoCard)
                _cache[echoHash].append(rarity)
        else:
            rarity = getRarity(echoCard)
            _cache[echoHash].append(rarity)
        
        if rarity >= cfg.get(cfg.echoMinRarity):
            levelText = info[0][2]
            
            try: level = int(levelText)
            except ValueError: level = 0
            level = min(25, level)

            if level >= cfg.get(cfg.echoMinLevel):
                tuneLv, stats = processStats(image, roiInfo, _cache)
                echoes.append(processEcho(name, level, tuneLv, rarity, stats))
                return True
        return False

    return True

def echoScraper(x: float, y: float, width: int, height: int) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    echoes = list()
    _cache = dict()
    roiInfo = getROI(width, height)
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
                center_x = startCoords.x + (col * (startCoords.w + scaleWidth(16, width))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + scaleHeight(24, height))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(width=width, height=height)
                
                continueScraping = processGridEcho(echoes, image, roiInfo, _cache)
                if not continueScraping:
                    del _cache
                    return echoes

        if page < pages - 1 and continueScraping:
            mouseScroll(scrollValue, 1.2)

    del _cache
    return echoes
