import time
import string
import logging
import numpy as np
from difflib import get_close_matches as getMatches
from collections import defaultdict

from scraping.utils import charactersID, weaponsID, definedText
from scraping.utils import (
    screenshot, convertToBlackWhite, imageToString,
    WindowsInputController
)
from game.screenInfo import ScreenInfo
from properties.config import cfg

logger = logging.getLogger('CharacterScraper')

# Constants
SKILL_LEGENDS = {
    0: 'normal',
    1: 'resonance',
    2: 'forte',
    3: 'liberation',
    4: 'intro'
}
ASCENSION_LEVELS = [20, 40, 50, 60, 70, 80, 90]

def scrapeResonator(image: np.ndarray, screenInfo: ScreenInfo, characters: dict, _cache: dict) -> tuple[str, bool]:
    resonatorNameImage = image[screenInfo.characters.resonatorName.y:screenInfo.characters.resonatorName.y + screenInfo.characters.resonatorName.h, screenInfo.characters.resonatorName.x:screenInfo.characters.resonatorName.x + screenInfo.characters.resonatorName.w]
    resonatorNameImage = convertToBlackWhite(resonatorNameImage)
    resonatorNameHash = hash(resonatorNameImage.tobytes())

    if resonatorNameHash in _cache:
        return None, True
    else:
        resonatorName = imageToString(resonatorNameImage, '', bannedChars=' ').lower()
    
        result = getMatches(resonatorName, charactersID, 1, 0.9)
        if result:
            resonatorName = result[0]
        
        resonatorID = '1502' if resonatorName == cfg.get(cfg.roverName).replace(' ', '').lower() else charactersID.get(resonatorName, resonatorName)
        _cache[resonatorNameHash] = resonatorID

    if resonatorID in characters:
        return resonatorID, True

    levelImage = image[screenInfo.characters.resonatorLevel.y:screenInfo.characters.resonatorLevel.y + screenInfo.characters.resonatorLevel.h, screenInfo.characters.resonatorLevel.x:screenInfo.characters.resonatorLevel.x + screenInfo.characters.resonatorLevel.w]
    levelImage = convertToBlackWhite(levelImage)
    levelHash = hash(levelImage.tobytes())

    if levelHash in _cache:
        level = _cache[levelHash]
    else:
        level = imageToString(levelImage, '', allowedChars=string.digits + '/').split('/')
        _cache[levelHash] = level

    try: ascensionLvl = ASCENSION_LEVELS.index(int(level[1]))
    except: ascensionLvl = 0

    try: characterLvl = int(level[0])
    except: characterLvl = 1

    characters[resonatorID]['level'] = characterLvl
    characters[resonatorID]['ascension'] = ascensionLvl

    return resonatorID, False

def scrapeWeapon(image: np.ndarray, screenInfo: ScreenInfo, characters: dict, resonatorID: str, _cache: dict):
    weaponNameImage = image[screenInfo.characters.weaponName.y:screenInfo.characters.weaponName.y + screenInfo.characters.weaponName.h, screenInfo.characters.weaponName.x:screenInfo.characters.weaponName.x + screenInfo.characters.weaponName.w]
    weaponNameImage = convertToBlackWhite(weaponNameImage)
    weaponNameHash = hash(weaponNameImage.tobytes())

    if weaponNameHash in _cache:
        weaponID = _cache[weaponNameHash]
    else:
        weaponName = imageToString(weaponNameImage, bannedChars=' ').lower()
    
        result = getMatches(weaponName, weaponsID, 1, 0.9)
        if result:
            weaponName = result[0]
        
        weaponID = weaponsID.get(weaponName, {'id': weaponName})['id']
        _cache[weaponNameHash] = weaponID
    
    levelImage = image[screenInfo.characters.weaponLevel.y:screenInfo.characters.weaponLevel.y + screenInfo.characters.weaponLevel.h, screenInfo.characters.weaponLevel.x:screenInfo.characters.weaponLevel.x + screenInfo.characters.weaponLevel.w]
    levelImage = convertToBlackWhite(levelImage)
    levelHash = hash(levelImage.tobytes())
    
    if levelHash in _cache:
        level = _cache[levelHash]
    else:
        level = imageToString(levelImage, '', allowedChars=string.digits + '/').split('/')
        _cache[levelHash] = level
    
    rankImage = image[screenInfo.characters.weaponRank.y:screenInfo.characters.weaponRank.y + screenInfo.characters.weaponRank.h, screenInfo.characters.weaponRank.x:screenInfo.characters.weaponRank.x + screenInfo.characters.weaponRank.w]
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

def scrapeSkills(controller: WindowsInputController, screenInfo: ScreenInfo, characters: dict, resonatorID: str, _cache: dict):

    controller.leftClick(screenInfo.characters.skillClick.x, screenInfo.characters.skillClick.y, .5)

    for index, skills in enumerate(screenInfo.characters.skillPositions):
        controller.leftClick(skills.x, skills.y)

        image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, bw=True)

        levelImage = image[screenInfo.characters.skillLevel.y:screenInfo.characters.skillLevel.y + screenInfo.characters.skillLevel.h, screenInfo.characters.skillLevel.x:screenInfo.characters.skillLevel.x + screenInfo.characters.skillLevel.w]
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
            controller.leftClick(skills.x, skills.y - (screenInfo.characters.offsets.skillPosition.y * y), .6)

            buttonImage = screenshot(screenInfo.characters.skillButton.x, screenInfo.characters.skillButton.y, screenInfo.characters.skillButton.w, screenInfo.characters.skillButton.h, monitor=screenInfo.monitor, bw=True)
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

    controller.pressKey('esc')

def scrapeChain(controller: WindowsInputController, screenInfo: ScreenInfo, characters: dict, resonatorID: str, _cache: dict):
    controller.leftClick(screenInfo.characters.chainClick.x, screenInfo.characters.chainClick.y, .7)

    for position in screenInfo.characters.chainPositions:
        controller.leftClick(position.x, position.y, .2)

        statusImage = screenshot(screenInfo.characters.chainButton.x, screenInfo.characters.chainButton.y, screenInfo.characters.chainButton.w, screenInfo.characters.chainButton.h, monitor=screenInfo.monitor)
        statusHash = hash(statusImage.tobytes())
        
        if statusHash in _cache:
            status = _cache[statusHash]
        else:
            status = imageToString(statusImage, '', bannedChars=f'{string.punctuation} ').lower()
            _cache[statusHash] = status

        if status.lower() != definedText['PrefabTextItem_3963945691_Text']: # MULTILANG
            break

        characters[resonatorID]['chain'] += 1
    controller.pressKey('esc')

def resonatorScraper(controller: WindowsInputController, screenInfo: ScreenInfo):
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

    controller.pressKey(cfg.get(cfg.resonatorKeybind), 2, False)

    isDouble = False
    xLeftSide, yLeftSide = screenInfo.characters.leftSide.x, screenInfo.characters.leftSide.y
    xRightSide, yRightSide = screenInfo.characters.rightSide.x, screenInfo.characters.rightSide.y

    while not isDouble:
        for resonatorIndex in range(7):
            controller.leftClick(xRightSide, yRightSide + (screenInfo.characters.offsets.rightSide.y * resonatorIndex), .7)
            resonatorID = str()

            for section in range(5):
                controller.leftClick(xLeftSide, yLeftSide + (screenInfo.characters.offsets.leftSide.y * section), .8)

                image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, bw=True)

                match(section):
                    case 0:
                        resonatorID, isDouble = scrapeResonator(image, screenInfo, characters, _cache)
                        if isDouble:
                            break
                    case 1:
                        scrapeWeapon(image, screenInfo, characters, resonatorID, _cache)
                    case 2:
                        pass  # Skip echoes for now
                    case 3:
                        scrapeSkills(controller, screenInfo, characters, resonatorID, _cache)
                    case 4:
                        scrapeChain(controller, screenInfo, characters, resonatorID, _cache)
                time.sleep(.5)

            if isDouble:
                break

        if isDouble:
            break

        controller.moveMouse(xRightSide, yRightSide, .3)
        controller.mouseScroll(screenInfo.scroll.characters.y, .5)
    
    # Process last page
    for resonatorIndex in range(6, -1, -1):
        controller.leftClick(xRightSide, yRightSide + (screenInfo.characters.offsets.rightSide.y * resonatorIndex), .7)
        resonatorID = str()
        
        for section in range(5):
            controller.leftClick(xLeftSide, yLeftSide + (screenInfo.characters.offsets.leftSide.y * section), .8)

            image = screenshot(width=screenInfo.width, height=screenInfo.height, monitor=screenInfo.monitor, bw=True)

            match(section):
                case 0:
                    resonatorID, isDouble = scrapeResonator(image, screenInfo, characters, _cache)
                    del _cache
                    return dict(characters)
                case 1:
                    scrapeWeapon(image, screenInfo, characters, resonatorID, _cache)
                case 2:
                    pass  # Skip echoes for now
                case 3:
                    scrapeSkills(controller, screenInfo, characters, resonatorID, _cache)
                case 4:
                    scrapeChain(controller, screenInfo, characters, resonatorID, _cache)

            time.sleep(.5)
        
        if isDouble:
            break
    
    del _cache
    return dict(characters)
