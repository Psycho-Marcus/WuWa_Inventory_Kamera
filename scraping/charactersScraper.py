import time
import string
import logging
import numpy as np
from difflib import get_close_matches
from collections import defaultdict

from scraping.utils import charactersID, weaponsID
from scraping.utils import (
    scaleWidth, scaleHeight, screenshot,
    convertToBlackWhite, imageToString, moveMouse,
    mouseScroll, leftClick, presskey
)
from properties.config import cfg

logger = logging.getLogger('CharacterScraper')

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
        'resonator_name': (250, 110, 280, 50),
        'resonator_level': (180, 200, 135, 80),
        'weapon_name': (257, 126, 273, 34),
        'weapon_level': (255, 160, 110, 35),
        'weapon_rank': (175, 355, 95, 35),
        'skill_level': (390, 100, 70, 40),
        'skill_button': (200, 980, 120, 35),
        'chain_button': (345, 896, 108, 22),
    }
    return ROI_Info(width, height, scaleCoordinates(unscaled_coords, width, height))

def scrapeResonator(image: np.ndarray, roiInfo: ROI_Info, characters: dict, _cache: dict) -> tuple[str, bool]:
    coords = roiInfo.coords
    resonatorNameImage = image[coords['resonator_name'].y:coords['resonator_name'].y + coords['resonator_name'].h, coords['resonator_name'].x:coords['resonator_name'].x + coords['resonator_name'].w]
    resonatorNameImage = convertToBlackWhite(resonatorNameImage)
    resonatorNameHash = hash(resonatorNameImage.tobytes())

    if resonatorNameHash in _cache:
        return None, True
    else:
        resonatorName = imageToString(resonatorNameImage, '', bannedChars=' ').lower()
        _cache[resonatorNameHash] = None
    
    result = get_close_matches(resonatorName, charactersID, 1, 0.9)
    if result:
        resonatorName = result[0]
    resonatorID = '1502' if resonatorName == cfg.get(cfg.roverName).replace(' ', '').lower() else charactersID.get(resonatorName, resonatorName)

    if resonatorID in characters:
        return resonatorID, True

    levelImage = image[coords['resonator_level'].y:coords['resonator_level'].y + coords['resonator_level'].h, coords['resonator_level'].x:coords['resonator_level'].x + coords['resonator_level'].w]
    levelImage = convertToBlackWhite(levelImage)
    levelHash = hash(levelImage.tobytes())

    if levelHash in _cache:
        level = _cache[levelHash]
    else:
        level = imageToString(levelImage, '', allowedChars=string.digits + '/').split('/')
        _cache[levelHash] = level

    characters[resonatorID]['level'] = int(level[0])
    characters[resonatorID]['ascension'] = ASCENSION_LEVELS.index(int(level[1]))

    return resonatorID, False

def scrapeWeapon(image: np.ndarray, roiInfo: ROI_Info, characters: dict, resonatorID: str, _cache: dict):
    coords = roiInfo.coords
    weaponNameImage = image[coords['weapon_name'].y:coords['weapon_name'].y + coords['weapon_name'].h, coords['weapon_name'].x:coords['weapon_name'].x + coords['weapon_name'].w]
    weaponNameImage = convertToBlackWhite(weaponNameImage)
    weaponNameHash = hash(weaponNameImage.tobytes())

    if weaponNameHash in _cache:
        weaponName = _cache[weaponNameHash]
    else:
        weaponName = imageToString(weaponNameImage, bannedChars=' ').lower()
        _cache[weaponNameHash] = weaponName
    
    result = get_close_matches(weaponName, weaponsID, 1, 0.9)
    if result:
        weaponName = result[0]
    
    weaponID = weaponsID.get(weaponName, {'id': weaponName})['id']
    
    levelImage = image[coords['weapon_level'].y:coords['weapon_level'].y + coords['weapon_level'].h, coords['weapon_level'].x:coords['weapon_level'].x + coords['weapon_level'].w]
    levelImage = convertToBlackWhite(levelImage)
    levelHash = hash(levelImage.tobytes())
    
    if levelHash in _cache:
        level = _cache[levelHash]
    else:
        level = imageToString(levelImage, '', allowedChars=string.digits + '/').split('/')
        _cache[levelHash] = level
    
    rankImage = image[coords['weapon_rank'].y:coords['weapon_rank'].y + coords['weapon_rank'].h, coords['weapon_rank'].x:coords['weapon_rank'].x + coords['weapon_rank'].w]
    rankImage = convertToBlackWhite(rankImage)
    rankHash = hash(rankImage.tobytes())

    if rankHash in _cache:
        rank = _cache[rankHash]
    else:
        rank = imageToString(rankImage, '', allowedChars=string.digits)
        _cache[rankHash] = rank

    try:
        characters[resonatorID]['weapon']['id'] = weaponID
        characters[resonatorID]['weapon']['level'] = int(level[0])
        characters[resonatorID]['weapon']['ascension'] = ASCENSION_LEVELS.index(int(level[1]))
        characters[resonatorID]['weapon']['rank'] = int(rank)
    except:
        logger.debug('Failed scraping the weapon')

def scrapeSkills(width: int, height: int, characters: dict, resonatorID: str, roiInfo: ROI_Info, _cache: dict):
    leftClick(scaleWidth(460.5, width), scaleHeight(903, height), .5)

    coords = roiInfo.coords

    for index, skills in enumerate(SKILL_POSITIONS):
        leftClick(scaleWidth(skills[0], width), scaleHeight(skills[1], height))

        image = screenshot(width=width, height=height, bw=True)

        levelImage = image[coords['skill_level'].y:coords['skill_level'].y + coords['skill_level'].h, coords['skill_level'].x:coords['skill_level'].x + coords['skill_level'].w]
        levelHash = hash(levelImage.tobytes())
        
        if levelHash in _cache:
            level = _cache[levelHash]
        else:
            level = imageToString(levelImage, '', allowedChars=string.digits)
            _cache[levelHash] = level

        try: level = int(level)
        except:
            level = 1
            _cache[levelHash] = level
            logger.debug('Failed scraping the skill level')

        characters[resonatorID]['skills'][SKILL_LEGENDS[index]] = level

        for y in range(1, 3):
            leftClick(scaleWidth(skills[0], width), scaleHeight(skills[1] - (255 * y), height), .6)

            buttonImage = screenshot(coords['skill_button'].x, coords['skill_button'].y, coords['skill_button'].w, coords['skill_button'].h, bw=True)
            buttonHash = hash(buttonImage.tobytes())

            if buttonHash in _cache:
                button = _cache[button]
            else:
                button = imageToString(buttonImage).lower()
                _cache[button] = button

            if button.lower() == 'activated': # MULTILANG
                key = 'inherent' if index == 2 else f'stats{index}' # MULTILANG
                characters[resonatorID]['skills'][key] += 1
            else:
                break

    presskey('esc')

def scrapeChain(width: int, height: int, characters: dict, resonatorID: str, roiInfo: ROI_Info, _cache: dict):
    leftClick(scaleWidth(1265, width), scaleHeight(135, height), .7)
    
    coords = roiInfo.coords

    for position in CHAIN_POSITIONS:
        leftClick(scaleWidth(position[0], width), scaleHeight(position[1], height))

        statusImage = screenshot(coords['chain_button'].x, coords['chain_button'].y, coords['chain_button'].w, coords['chain_button'].h, bw=True)
        statusHash = hash(statusImage.tobytes())
        
        if statusHash in _cache:
            status = _cache[statusHash]
        else:
            status = imageToString(statusImage, '', bannedChars=f'{string.punctuation} ').lower()
            _cache[statusHash] = status

        if status.lower() != 'activated': # MULTILANG
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

    _cache = dict()
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

                image = screenshot(width=WIDTH, height=HEIGHT, bw=True)

                match(section):
                    case 0:
                        resonatorID, isDouble = scrapeResonator(image, roiInfo, characters, _cache)
                        if isDouble:
                            break
                    case 1:
                        scrapeWeapon(image, roiInfo, characters, resonatorID, _cache)
                    case 2:
                        pass  # Skip echoes for now
                    case 3:
                        scrapeSkills(WIDTH, HEIGHT, characters, resonatorID, roiInfo, _cache)
                    case 4:
                        scrapeChain(WIDTH, HEIGHT, characters, resonatorID, roiInfo, _cache)
                time.sleep(.5)

            if isDouble:
                break

        if isDouble:
            break

        moveMouse(xRightSide, yRightSide, .3)
        mouseScroll(-56, .5)
    
    # Process last page
    for resonatorIndex in range(6, -1, -1):
        leftClick(xRightSide, yRightSide + (scaleHeight(92, HEIGHT) + 14) * resonatorIndex, .7)
        resonatorID = str()
        
        for section in range(5):
            leftClick(xLeftSide, yLeftSide + (scaleHeight(136, HEIGHT) * section), .8)

            image = screenshot(width=WIDTH, height=HEIGHT, bw=True)

            match(section):
                case 0:
                    resonatorID, isDouble = scrapeResonator(image, roiInfo, characters, _cache)
                    if isDouble:
                        break
                case 1:
                    scrapeWeapon(image, roiInfo, characters, resonatorID, _cache)
                case 2:
                    pass  # Skip echoes for now
                case 3:
                    scrapeSkills(WIDTH, HEIGHT, characters, resonatorID, roiInfo, _cache)
                case 4:
                    scrapeChain(WIDTH, HEIGHT, characters, resonatorID, roiInfo, _cache)

            time.sleep(.5)
        
        if isDouble:
            break
    
    del _cache
    return dict(characters)
