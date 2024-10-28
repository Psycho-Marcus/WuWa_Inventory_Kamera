import time
import string
import logging
import numpy as np
from difflib import get_close_matches
from collections import defaultdict

from scraping.utils import charactersID, weaponsID, definedText
from scraping.utils import (
    screenshot, convertToBlackWhite, imageToString,
    moveMouse, mouseScroll, leftClick,
    presskey
)
from game.screenInfo import ScreenInfo
from properties.config import cfg

logger = logging.getLogger('CharacterScraper')

# Constants
SKILL_POSITIONS = [
    ((755, 660), (905, 842)),
    ((985, 864), (765, 722)),
    ((1260, 1103), (705, 667)),
    ((1535, 1342), (765, 722)),
    ((1760, 1545), (905, 842))
]
SKILL_LEGENDS = {
    0: 'normal',
    1: 'resonance',
    2: 'forte',
    3: 'liberation',
    4: 'intro'
}
CHAIN_POSITIONS = [
    ((1395, 1224), (140, 176)),
    ((1565, 1369), (305, 319)),
    ((1640, 1424), (535, 519)),
    ((1565, 1369), (765, 724)),
    ((1400, 1224), (935, 864)),
    ((1170, 1024), (995, 919)),
]
ASCENSION_LEVELS = [20, 40, 50, 60, 70, 80, 90]

class Coordinates:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class ROI_Info:
    def __init__(self, width: int, height: int, coords: dict[str, Coordinates | list[tuple[int, int]]]):
        self.width = width
        self.height = height
        self.coords = coords

def scaleCoordinates(coords: dict[str, tuple[int, int, int, int] | list[tuple[int, int]]], screenInfo: ScreenInfo) -> dict[str, Coordinates | list[tuple[int, int]]]:
    scaled_coords = {}
    for key, value in coords.items():
        if isinstance(value, list):
            scaled_coords[key] = [
                Coordinates(screenInfo.scaleWidth(x), screenInfo.scaleHeight(y), 0, 0)
                for x, y in value
            ]
        else:
            x, y, w, h = value
            scaled_coords[key] = Coordinates(
                screenInfo.scaleWidth(x),
                screenInfo.scaleHeight(y),
                screenInfo.scaleWidth(w),
                screenInfo.scaleHeight(h)
            )
    return scaled_coords

def getROI(screenInfo: ScreenInfo) -> ROI_Info:
    unscaled_coords = {
        'left_side': ((82, 72), (191, 167.5), 0, 0),
        'left_side_diff': (0, (136, 119), 0, 0),
        'right_side': ((1814, 1586.5), (203, 177.5), 0, 0),
        'right_side_diff': (0, (92, 81), 0, 0),
        'resonator_name': ((250, 220), (110, 102), 280, 50),
        'resonator_level': ((180, 160), (200, 180), 135, 80),
        'weapon_name': ((257, 225), (126, 118), (273, 240), 34),
        'weapon_level': ((255, 215), (160, 150), 110, 35),
        'weapon_rank': ((175, 143), (355, 320), (95, 93), 35),
        'skill_click': ((460.5, 403), (903, 845), 0, 0),
        'skill_level': ((390, 340), (100, 95), 70, 40),
        'skill_button': ((200, 170), (980, 950), 120, 35),
        'chain_button': ((342, 292), (964, 936), 110, 32),
        'skill_positions': SKILL_POSITIONS,
        'chain_positions': CHAIN_POSITIONS
    }
    return ROI_Info(screenInfo.width, screenInfo.height, scaleCoordinates(unscaled_coords, screenInfo))

def scrapeResonator(image: np.ndarray, roiInfo: ROI_Info, characters: dict, _cache: dict) -> tuple[str, bool]:
    coords = roiInfo.coords
    resonatorNameImage = image[coords['resonator_name'].y:coords['resonator_name'].y + coords['resonator_name'].h, coords['resonator_name'].x:coords['resonator_name'].x + coords['resonator_name'].w]
    resonatorNameImage = convertToBlackWhite(resonatorNameImage)
    resonatorNameHash = hash(resonatorNameImage.tobytes())

    if resonatorNameHash in _cache:
        return None, True
    else:
        resonatorName = imageToString(resonatorNameImage, '', bannedChars=' ').lower()
    
        result = get_close_matches(resonatorName, charactersID, 1, 0.9)
        if result:
            resonatorName = result[0]
        
        resonatorID = '1502' if resonatorName == cfg.get(cfg.roverName).replace(' ', '').lower() else charactersID.get(resonatorName, resonatorName)
        _cache[resonatorNameHash] = resonatorID

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
        weaponID = _cache[weaponNameHash]
    else:
        weaponName = imageToString(weaponNameImage, bannedChars=' ').lower()
    
        result = get_close_matches(weaponName, weaponsID, 1, 0.9)
        if result:
            weaponName = result[0]
        
        weaponID = weaponsID.get(weaponName, {'id': weaponName})['id']
        _cache[weaponNameHash] = weaponID
    
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

def scrapeSkills(screenInfo: ScreenInfo, characters: dict, resonatorID: str, roiInfo: ROI_Info, _cache: dict):
    coords = roiInfo.coords

    leftClick(coords['skill_click'].x, coords['skill_click'].y, .5)

    for index, skills in enumerate(coords['skill_positions']):
        leftClick(skills.x, skills.y)

        image = screenshot(width=screenInfo.width, height=screenInfo.height, bw=True)

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
            leftClick(skills.x, skills.y - screenInfo.scaleHeight((255 * y, 220 * y)), .6)

            buttonImage = screenshot(coords['skill_button'].x, coords['skill_button'].y, coords['skill_button'].w, coords['skill_button'].h, bw=True)
            buttonHash = hash(buttonImage.tobytes())

            if buttonHash in _cache:
                button = _cache[button]
            else:
                button = imageToString(buttonImage).lower()
                _cache[button] = button

            if button.lower() == definedText['PrefabTextItem_3963945691_Text']: # MULTILANG
                key = 'inherent' if index == 2 else f'stats{index}'
                characters[resonatorID]['skills'][key] += 1
            else:
                break

    presskey('esc')

def scrapeChain(screenInfo: ScreenInfo, characters: dict, resonatorID: str, roiInfo: ROI_Info, _cache: dict):
    leftClick(screenInfo.scaleWidth((1265, 1109)), screenInfo.scaleHeight((135, 174)), .7)
    
    coords = roiInfo.coords

    for position in coords['chain_positions']:
        leftClick(position.x, position.y, .2)

        statusImage = screenshot(coords['chain_button'].x, coords['chain_button'].y, coords['chain_button'].w, coords['chain_button'].h)
        statusHash = hash(statusImage.tobytes())
        
        if statusHash in _cache:
            status = _cache[statusHash]
        else:
            status = imageToString(statusImage, '', bannedChars=f'{string.punctuation} ').lower()
            _cache[statusHash] = status

        if status.lower() != definedText['PrefabTextItem_3963945691_Text']: # MULTILANG
            break

        characters[resonatorID]['chain'] += 1
    presskey('esc')

def resonatorScraper(screenInfo: ScreenInfo):
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
    roiInfo = getROI(screenInfo)
    coords = roiInfo.coords

    presskey(cfg.get(cfg.resonatorKeybind), 2, False)

    isDouble = False

    xLeftSide, yLeftSide = coords['left_side'].x, coords['left_side'].y
    xRightSide, yRightSide = coords['right_side'].x, coords['right_side'].y

    while not isDouble:
        for resonatorIndex in range(7):
            leftClick(xRightSide, yRightSide + (coords['right_side_diff'].y + screenInfo.scaleHeight(14)) * resonatorIndex, .7)
            resonatorID = str()

            for section in range(5):
                leftClick(xLeftSide, yLeftSide + (coords['left_side_diff'].y * section), .8)

                image = screenshot(width=screenInfo.width, height=screenInfo.height, bw=True)

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
                        scrapeSkills(screenInfo, characters, resonatorID, roiInfo, _cache)
                    case 4:
                        scrapeChain(screenInfo, characters, resonatorID, roiInfo, _cache)
                time.sleep(.5)

            if isDouble:
                break

        if isDouble:
            break

        moveMouse(xRightSide, yRightSide, .3)
        mouseScroll(-56, .5)
    
    # Process last page
    for resonatorIndex in range(6, -1, -1):
        leftClick(xRightSide, yRightSide + (coords['right_side_diff'].y + screenInfo.scaleHeight(14)) * resonatorIndex, .7)
        resonatorID = str()
        
        for section in range(5):
            leftClick(xLeftSide, yLeftSide + (coords['left_side_diff'].y * section), .8)

            image = screenshot(width=screenInfo.width, height=screenInfo.height, bw=True)

            match(section):
                case 0:
                    resonatorID, isDouble = scrapeResonator(image, roiInfo, characters, _cache)
                    del _cache
                    return dict(characters)
                case 1:
                    scrapeWeapon(image, roiInfo, characters, resonatorID, _cache)
                case 2:
                    pass  # Skip echoes for now
                case 3:
                    scrapeSkills(screenInfo, characters, resonatorID, roiInfo, _cache)
                case 4:
                    scrapeChain(screenInfo, characters, resonatorID, roiInfo, _cache)

            time.sleep(.5)
        
        if isDouble:
            break
    
    del _cache
    return dict(characters)
