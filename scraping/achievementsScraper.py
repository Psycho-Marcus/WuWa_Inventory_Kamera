import pyperclip
import numpy as np

from scraping.utils import achievementsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    imageToString, convertToBlackWhite, leftClick,
    presskey, hotkey
)

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
        'status': (1579, 230, 256, 65),
        'notFound': (855, 550, 280, 35),
        'searchBar': (388, 149, 1, 1),
        'searchButton': (629, 149, 1, 1),
        'achievementsButton': (1674, 790, 1, 1),
        'achievementsTab': (835, 570, 1, 1),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

def processAchievement(image: np.ndarray, roiInfo: ROI_Info, achievementName: str, _cache: dict) -> str | None:
    coords = roiInfo.coords
    statusImage = image[coords['status'].y:coords['status'].y + coords['status'].h, coords['status'].x:coords['status'].x + coords['status'].w]
    statusImage = convertToBlackWhite(statusImage)
    statusHash = hash(statusImage.tobytes())
    if statusHash in _cache: statusText = _cache[statusHash]
    else:
        statusText = imageToString(statusImage).lower()
        _cache[statusHash] = statusText

    if statusText == 'claim' or '/' in statusText: # MULTILANG
        return achievementsID[achievementName]
    
    return None

def achievementScraper(WIDTH: int, HEIGHT: int) -> list[str]:
    achievements = []
    _cache = dict()
    roiInfo = getROI(WIDTH, HEIGHT)

    presskey('esc', 1)
    leftClick(roiInfo.coords['achievementsButton'].x, roiInfo.coords['achievementsButton'].y, 1.2)
    leftClick(roiInfo.coords['achievementsTab'].x, roiInfo.coords['achievementsTab'].y, 1)

    for achievementName in achievementsID:
        pyperclip.copy(achievementName)
        leftClick(roiInfo.coords['searchBar'].x, roiInfo.coords['searchBar'].y, .3)
        hotkey('ctrl', 'v', waitTime=.3)
        leftClick(roiInfo.coords['searchButton'].x, roiInfo.coords['searchButton'].y, .6)

        image = screenshot(width=WIDTH, height=HEIGHT)
        achievement = processAchievement(image, roiInfo, achievementName, _cache)
        if achievement:
            achievements.append(achievement)
        
        leftClick(roiInfo.coords['searchButton'].x, roiInfo.coords['searchButton'].y)
    
    presskey('esc', .5)
    del _cache
    return achievements