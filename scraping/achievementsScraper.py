import string
import pyperclip
import pytesseract
import numpy as np

from scraping.utils import achievementsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    leftClick, presskey, hotkey
)
from properties.config import cfg

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

def processAchievement(image: np.ndarray, roiInfo: ROI_Info, achievementName: str) -> str | None:
    coords = roiInfo.coords
    notFoundText = pytesseract.image_to_string(
        image[coords['notFound'].y:coords['notFound'].y + coords['notFound'].h, 
              coords['notFound'].x:coords['notFound'].x + coords['notFound'].w],
        config='--psm 7'
    ).translate(str.maketrans('', '', string.digits + string.punctuation)).strip().lower()

    if notFoundText != 'no search result':
        statusText = pytesseract.image_to_string(
            image[coords['status'].y:coords['status'].y + coords['status'].h, 
                  coords['status'].x:coords['status'].x + coords['status'].w],
            config=f'--psm 7 -c tessedit_char_whitelist={string.ascii_letters}'
        ).strip().lower()

        if statusText != 'ongoing':
            return achievementsID[achievementName]
    
    return None

def achievementScraper(WIDTH: int, HEIGHT: int) -> list[str]:
    achievements = []
    roiInfo = getROI(WIDTH, HEIGHT)

    presskey('esc', 1)
    leftClick(roiInfo.coords['achievementsButton'].x, roiInfo.coords['achievementsButton'].y, 1.2)
    leftClick(roiInfo.coords['achievementsTab'].x, roiInfo.coords['achievementsTab'].y, 1)

    for achievementName in achievementsID:
        pyperclip.copy(achievementName)
        leftClick(roiInfo.coords['searchBar'].x, roiInfo.coords['searchBar'].y, .3)
        hotkey('ctrl', 'v', waitTime=.3)
        leftClick(roiInfo.coords['searchButton'].x, roiInfo.coords['searchButton'].y, .3)

        image = screenshot(width=WIDTH, height=HEIGHT)
        achievement = processAchievement(image, roiInfo, achievementName)
        if achievement:
            achievements.append(achievement)
        
        leftClick(roiInfo.coords['searchButton'].x, roiInfo.coords['searchButton'].y, .3)
    
    presskey('esc', .5)
    return achievements