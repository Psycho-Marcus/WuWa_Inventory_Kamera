import time
import string
import pytesseract
import numpy as np
from collections import defaultdict

from scraping.utils import charactersID, weaponsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    moveMouse, mouseScroll, leftClick,
    presskey
)
from properties.config import cfg

# Constants
SKILL_POSITIONS = [
    (755, 905),
    (985, 765),
    (1260, 705),
    (1535, 765),
    (1760, 905)
]
SKILL_LEGENDS = {
    0: 'normal',
    1: 'resonance',
    2: 'forte',
    3: 'liberation',
    4: 'intro'
}
CHAIN_POSITIONS = [
    (1395, 140),
    (1565, 305),
    (1640, 535),
    (1565, 765),
    (1400, 935),
    (1170, 995),
]
ASCENSION_LEVELS = [20, 40, 50, 60, 70, 80, 90]

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
        'resonator_name': (255, 115, 275, 45),
        'resonator_level': (184, 237, 117, 28),
        'weapon_name': (257, 126, 273, 34),
        'weapon_level': (258, 165, 102, 27),
        'weapon_rank': (176, 356, 92, 32),
        'skill_level': (405, 110, 58, 23),
        'skill_button': (210, 985, 110, 25),
        'chain_button': (345, 896, 108, 22),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

def scrapeResonator(image: np.ndarray, roiInfo: ROI_Info, characters: dict) -> tuple[str, bool]:
    coords = roiInfo.coords
    resonatorName = pytesseract.image_to_string(
        image[coords['resonator_name'].y:coords['resonator_name'].y + coords['resonator_name'].h, 
              coords['resonator_name'].x:coords['resonator_name'].x + coords['resonator_name'].w], 
        config=f'-c tessedit_char_whitelist= {string.ascii_letters + string.whitespace}'
    ).strip()
    
    resonatorID = '1502' if resonatorName.lower() == cfg.get(cfg.roverName).lower() else str(charactersID.get(resonatorName, resonatorName))

    if resonatorID in characters:
        return resonatorID, True

    level = pytesseract.image_to_string(
        image[coords['resonator_level'].y:coords['resonator_level'].y + coords['resonator_level'].h, 
              coords['resonator_level'].x:coords['resonator_level'].x + coords['resonator_level'].w], 
        config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/'
    ).strip().split('/')

    characters[resonatorID]['level'] = int(level[0])
    characters[resonatorID]['ascension'] = ASCENSION_LEVELS.index(int(level[1]))

    return resonatorID, False

def scrapeWeapon(image: np.ndarray, roiInfo: ROI_Info, characters: dict, resonatorID: str):
    coords = roiInfo.coords
    weaponName = pytesseract.image_to_string(
        image[coords['weapon_name'].y:coords['weapon_name'].y + coords['weapon_name'].h, 
              coords['weapon_name'].x:coords['weapon_name'].x + coords['weapon_name'].w]
    ).strip()
    weaponID = weaponsID.get(weaponName, {'id': weaponName})['id']
    
    level = pytesseract.image_to_string(
        image[coords['weapon_level'].y:coords['weapon_level'].y + coords['weapon_level'].h, 
              coords['weapon_level'].x:coords['weapon_level'].x + coords['weapon_level'].w], 
        config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/'
    ).strip().split('/')
    
    rank = pytesseract.image_to_string(
        image[coords['weapon_rank'].y:coords['weapon_rank'].y + coords['weapon_rank'].h, 
              coords['weapon_rank'].x:coords['weapon_rank'].x + coords['weapon_rank'].w], 
        config=f'--psm 7 -c tessedit_char_whitelist={string.digits}'
    )

    characters[resonatorID]['weapon']['id'] = weaponID
    characters[resonatorID]['weapon']['level'] = int(level[0])
    characters[resonatorID]['weapon']['ascension'] = ASCENSION_LEVELS.index(int(level[1]))
    characters[resonatorID]['weapon']['rank'] = int(rank)

def scrapeSkills(width: int, height: int, characters: dict, resonatorID: str, roiInfo: ROI_Info):
    leftClick(scaleWidth(460.5, width), scaleHeight(903, height), .5)

    coords = roiInfo.coords

    for index, skills in enumerate(SKILL_POSITIONS):
        leftClick(scaleWidth(skills[0], width), scaleHeight(skills[1], height))

        image = screenshot(0, 0, width, height, bw=True)

        level = pytesseract.image_to_string(
            image[coords['skill_level'].y:coords['skill_level'].y + coords['skill_level'].h, 
                  coords['skill_level'].x:coords['skill_level'].x + coords['skill_level'].w], 
            config=f'--psm 7 -c tessedit_char_whitelist={string.digits}'
        ).strip()
        try: level = int(level)
        except: level = 1

        characters[resonatorID]['skills'][SKILL_LEGENDS[index]] = level

        for y in range(1, 3):
            leftClick(scaleWidth(skills[0], width), scaleHeight(skills[1] - (255 * y), height), .1)

            image = screenshot(0, 0, width, height)

            button = pytesseract.image_to_string(
                image[coords['skill_button'].y:coords['skill_button'].y + coords['skill_button'].h, 
                      coords['skill_button'].x:coords['skill_button'].x + coords['skill_button'].w]
            ).strip()

            if button.lower() == 'activated':
                key = 'inherent' if index == 2 else f'stats{index}'
                characters[resonatorID]['skills'][key] += 1
            else:
                break

        time.sleep(.2)
    presskey('esc')

def scrapeChain(width: int, height: int, characters: dict, resonatorID: str, roiInfo: ROI_Info):
    leftClick(scaleWidth(1265, width), scaleHeight(135, height), .7)
    
    coords = roiInfo.coords

    for position in CHAIN_POSITIONS:
        leftClick(scaleWidth(position[0], width), scaleHeight(position[1], height))

        image = screenshot(0, 0, width, height)
        text = pytesseract.image_to_string(
            image[coords['chain_button'].y:coords['chain_button'].y + coords['chain_button'].h, 
                  coords['chain_button'].x:coords['chain_button'].x + coords['chain_button'].w], 
            config=f'-c tessedit_char_blacklist={string.punctuation}'
        ).strip()

        if text.lower() != 'activated':
            break

        characters[resonatorID]['chain'] += 1
    presskey('esc')

def resonatorScraper(WIDTH: int, HEIGHT: int):
    characters = defaultdict(
        lambda: defaultdict(
            int,
            {
                'level': 0,
                'ascension': 0,
                'weapon': defaultdict(
                    int,
                    {
                        'id': 0,
                        'level': 1,
                        'ascension': 0,
                        'rank': 0
                    }
                ),
                'echoes': dict(),
                'skills': defaultdict(
                    int,
                    {
                        'normal': 1,
                        'resonance': 1,
                        'forte': 1,
                        'liberation': 1,
                        'intro': 1,
                        'stats0': 0,
                        'stats1': 0,
                        'inherent': 0,
                        'stats3': 0,
                        'stats4': 0
                    }
                ),
                'chain': 0
            }
        )
    )

    roiInfo = getROI(WIDTH, HEIGHT)

    presskey(cfg.get(cfg.resonatorKeybind), 2, False)

    isDouble = False

    xLeftSide, yLeftSide = scaleWidth(82, WIDTH), scaleHeight(191, HEIGHT)
    xRightSide, yRightSide = scaleWidth(1814, WIDTH), scaleHeight(203, HEIGHT)

    while not isDouble:
        for resonatorIndex in range(7):
            leftClick(xRightSide, yRightSide + (scaleHeight(92, HEIGHT) + 14) * resonatorIndex, .7)
            resonatorID = str()

            for section in range(5):
                leftClick(xLeftSide, yLeftSide + (scaleHeight(136, HEIGHT) * section), .8)

                image = screenshot(0, 0, WIDTH, HEIGHT, bw=True)

                match(section):
                    case 0:
                        resonatorID, isDouble = scrapeResonator(image, roiInfo, characters)
                        if isDouble:
                            break
                    case 1:
                        scrapeWeapon(image, roiInfo, characters, resonatorID)
                    case 2:
                        pass  # Skip echoes for now
                    case 3:
                        scrapeSkills(WIDTH, HEIGHT, characters, resonatorID, roiInfo)
                    case 4:
                        scrapeChain(WIDTH, HEIGHT, characters, resonatorID, roiInfo)

                time.sleep(.5)

            if isDouble:
                break

        if isDouble:
            break

        moveMouse(xRightSide, yRightSide, .2)
        mouseScroll(-56, .5)
    
    # Process last page
    for resonatorIndex in range(6, -1, -1):
        leftClick(xRightSide, yRightSide + (scaleHeight(92, HEIGHT) + 14) * resonatorIndex, .7)
        
        for section in range(5):
            leftClick(xLeftSide, yLeftSide + (scaleHeight(136, HEIGHT) * section), .8)

            image = screenshot(0, 0, WIDTH, HEIGHT, bw=True)

            match(section):
                case 0:
                    resonatorID, isDouble = scrapeResonator(image, roiInfo, characters)
                    if isDouble:
                        break
                case 1:
                    scrapeWeapon(image, roiInfo, characters, resonatorID)
                case 2:
                    pass  # Skip echoes for now
                case 3:
                    scrapeSkills(WIDTH, HEIGHT, characters, resonatorID, roiInfo)
                case 4:
                    scrapeChain(WIDTH, HEIGHT, characters, resonatorID, roiInfo)

            time.sleep(.5)
        
        if isDouble:
            break

    return dict(characters)
