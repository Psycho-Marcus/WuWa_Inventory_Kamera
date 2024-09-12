import cv2
import string
import pytesseract
import numpy as np
from collections import defaultdict

from scraping.utils import echoesID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    convertToBlackWhite, mouseScroll, leftClick,
    presskey
)
from properties.config import cfg

# Constants
ROWS, COLS = 4, 6
STATS_NAME = {
    'hp': 'hp',
    'atk': 'atk',
    'def': 'def',
    'aerodmg': 'aero',
    'glaciodmg': 'glacio',
    'fusiondmg': 'fusion',
    'electrodmg': 'electro',
    'havocdmg': 'havoc',
    'spectrodmg': 'spectro',
    'energyregen': 'er',
    'critrate': 'cr',
    'critdmg': 'cd',
    'healingbonus': 'healing',
    'basicattackdmgbonus': 'basic_attack',
    'heavyattackdmgbonus': 'heavy_attack',
    'resonanceskilldmgbonus': 'skill_dmg',
    'resonanceliberationdmgbonus': 'liberation_dmg',
}

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
        'page': (205, 55, 125, 30),
        'name': (1305, 116, 545, 55),
        'level': (1770, 250, 65, 30),
        'start': (205, 122, 151, 181),
        'mainStatName': (1380, 430, 360, 35),
        'mainStatValue': (1740, 430, 100, 35),
        'subStatName': (1380, 510, 360, 280),
        'subStatValue': (1740, 510, 100, 280),

        'fullStatsName': (1380, 430, 360, 380),
        'fullStatsValue': (1740, 430, 100, 380),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

def setupRarityDetection():
    rarityColors = {
        5: np.array([255, 230, 90]),
        4: np.array([202, 109, 255]),
        3: np.array([89, 180, 211]),
        2: np.array([92, 195, 94]),
        1: np.array([239, 236, 225])
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
    img = convertToBlackWhite(screenshot(0, 0, roiInfo.width, roiInfo.height)[coords.y:coords.y + coords.h, coords.x:coords.x + coords.w])
    echoCount = pytesseract.image_to_string(img, config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/').split('/')[0]
    
    try: return int(echoCount), int(np.ceil(int(echoCount) / 24))
    except ValueError: return 24, 1

def processEcho(name: str, level: int, tuneLv: int, rarity: int, stats: dict) -> dict[str, dict[int, int, dict]]:
    echoID = str(echoesID.get(name, name))
    return {
        echoID: {
            'level': level,
            'tuneLv': tuneLv,
            'rarity': rarity,
            'stats': stats
        }
    }

def processStats(image: np.ndarray, roiInfo: ROI_Info) -> dict[str:int]:
    stats = defaultdict(dict)
    coords = roiInfo.coords
    tuneLv = 0

    nameImage = image[
        coords['fullStatsName'].y:coords['fullStatsName'].y + coords['fullStatsName'].h,
        coords['fullStatsName'].x:coords['fullStatsName'].x + coords['fullStatsName'].w
    ]
    valueImage = image[
        coords['fullStatsValue'].y:coords['fullStatsValue'].y + coords['fullStatsValue'].h,
        coords['fullStatsValue'].x:coords['fullStatsValue'].x + coords['fullStatsValue'].w
    ]
    
    names = pytesseract.image_to_string(nameImage, config=f'--psm 4').split('Echo Skill')[0].split('Skill')[0].lower().replace('\n\n', '\n').strip()
    values = pytesseract.image_to_string(valueImage, config=f'--psm 4 tessedit_char_whitelist={string.digits}.,%').strip()

    for stat in ['Resonance Liberation\nDMG Bonus', 'Resonance Skill DMG\nBonus']:
        names = names.replace(stat.lower(), stat.lower().replace('\n', ' '))

    values = values.replace(')', '').replace(',', '.').replace('\n\n', '\n')

    names_list = names.split('\n')
    values_list = values.split('\n')
    values_list = [x for x in values_list if len(x) > 1 and x.translate(str.maketrans('', '', string.ascii_letters))]
    tuneLv = len(values_list)
    
    for index, (statName, statValue) in enumerate(zip(names_list, values_list)):
        statName = STATS_NAME.get(statName.replace(' ', '').replace('.', ''), statName)
        
        if index < 2: stat = 'main'
        else: stat = 'sub'
        
        if statValue.endswith('%'):
            stats[stat].update({f"{statName}%": float(statValue[:-1])})
        else:
            stats[stat].update({statName: int(statValue)})

    return tuneLv, dict(stats)

def processGridEcho(image: np.ndarray, roiInfo: ROI_Info) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    echoes = []
    coords = roiInfo.coords

    imageName = image[coords['name'].y:coords['name'].y + coords['name'].h, coords['name'].x:coords['name'].x + coords['name'].w]
    name = pytesseract.image_to_string(imageName).strip()
    
    if name in echoesID:
        rarity = getRarity(imageName)
        if rarity >= cfg.get(cfg.echoMinRarity):
            levelText = pytesseract.image_to_string(image[coords['level'].y:coords['level'].y + coords['level'].h, coords['level'].x:coords['level'].x + coords['level'].w], config=f'--psm 7 -c tessedit_char_whitelist={string.digits}')
            
            try: level = int(levelText)
            except ValueError: level = 0
            level = min(25, level)

            if level >= cfg.get(cfg.echoMinLevel):
                tuneLv, stats = processStats(image, roiInfo)
                echoes.append(processEcho(name, level, tuneLv, rarity, stats))
                return echoes, True
        else:
            return echoes, False

    return echoes, True

def echoScraper(x: float, y: float, width: int, height: int) -> tuple[dict[str, int], list[dict[str, dict[str, int]]]]:
    echoes = []
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
                    continueScraping = False
                    break

                startCoords = roiInfo.coords['start']
                center_x = startCoords.x + (col * (startCoords.w + scaleWidth(16, width))) + startCoords.w // 2
                center_y = startCoords.y + (row * (startCoords.h + scaleHeight(24, height))) + startCoords.h // 2
                
                leftClick(center_x, center_y)
                image = screenshot(0, 0, width, height)
                
                echo, continueScraping = processGridEcho(image, roiInfo)
                echoes.extend(echo)
            if not continueScraping:
                return echoes

        if page < pages - 1 and continueScraping:
            mouseScroll(scrollValue, 1.2)

    return echoes
