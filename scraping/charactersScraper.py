import time
import string
import pytesseract
import pydirectinput
from collections import defaultdict

from scraping.utils import charactersID, weaponsID
from scraping.utils import (
    pressEscape, scaleWidth, scaleHeight,
    screenshot
)
from properties.config import cfg

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

    pydirectinput.press(cfg.get(cfg.resonatorKeybind))
    time.sleep(2)

    isDouble = False

    xLeftSide, yLeftSide = scaleWidth(82, WIDTH), scaleHeight(191, HEIGHT)
    xRightSide, yRightSide = scaleWidth(1814, WIDTH), scaleHeight(203, HEIGHT)

    while not isDouble:
        for resonatorIndex in range(7):
            pydirectinput.leftClick(xRightSide, yRightSide + (scaleHeight(92, HEIGHT) + 14) * resonatorIndex)
            time.sleep(.7)
            resonatorID = str()

            for section in range(5):
                pydirectinput.leftClick(xLeftSide, yLeftSide + (scaleHeight(136, HEIGHT) * section))
                time.sleep(.8)

                image = screenshot(0, 0, WIDTH, HEIGHT, bw=True)

                match(section):
                    case 0:
                        resonatorID, isDouble = scrapeResonator(WIDTH, HEIGHT, image, characters, resonatorID)
                        if isDouble:
                            break
                    case 1:
                        scrapeWeapon(WIDTH, HEIGHT, image, characters, resonatorID)
                    case 2:
                        pass  # Skip echoes for now
                    case 3:
                        scrapeSkills(WIDTH, HEIGHT, characters, resonatorID)
                    case 4:
                        scrapeChain(WIDTH, HEIGHT, characters, resonatorID)

                time.sleep(.5)

            if isDouble:
                break

        pydirectinput.moveTo(xRightSide, yRightSide)
        time.sleep(.2)
        pydirectinput.scroll(-56)
        time.sleep(.5)
    
    # last 'page'
    for resonatorIndex in range(7 - 1, -1, -1):
        pydirectinput.leftClick(xRightSide, yRightSide + (scaleHeight(92, HEIGHT) + 14) * resonatorIndex)
        time.sleep(.7)

        for section in range(5):
            pydirectinput.leftClick(xLeftSide, yLeftSide + (scaleHeight(136, HEIGHT) * section))
            time.sleep(.8)

            image = screenshot(0, 0, WIDTH, HEIGHT, bw=True)

            match(section):
                case 0:
                    resonatorID, isDouble = scrapeResonator(WIDTH, HEIGHT, image, characters, resonatorID)
                    if isDouble:
                        break
                case 1:
                    scrapeWeapon(WIDTH, HEIGHT, image, characters, resonatorID)
                case 2:
                    pass  # Skip echoes for now
                case 3:
                    scrapeSkills(WIDTH, HEIGHT, characters, resonatorID)
                case 4:
                    scrapeChain(WIDTH, HEIGHT, characters, resonatorID)

            time.sleep(.5)
        if isDouble:
            break

    return dictify(characters)


def scrapeResonator(WIDTH, HEIGHT, image, characters, resonatorID):
    xName, yName, wName, hName = (
        scaleWidth(255, WIDTH),
        scaleHeight(115, HEIGHT),
        scaleWidth(275, WIDTH),
        scaleHeight(45, HEIGHT)
    )
    xLevel, yLevel, wLevel, hLevel = (
        scaleWidth(184, WIDTH),
        scaleHeight(237, HEIGHT),
        scaleWidth(117, WIDTH),
        scaleHeight(28, HEIGHT)
    )

    resonatorName = pytesseract.image_to_string(image[yName:yName + hName, xName:xName + wName], config=f'-c tessedit_char_whitelist={string.ascii_letters + string.whitespace} ').strip()
    if resonatorName.lower() == cfg.get(cfg.roverName).lower():
        resonatorID = '1502'
    else:
        resonatorID = str(charactersID.get(resonatorName, resonatorName))

    if resonatorID in characters:
        return resonatorID, True

    level = pytesseract.image_to_string(image[yLevel:yLevel + hLevel, xLevel:xLevel + wLevel], config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/').strip().split('/')

    characters[resonatorID]['level'] = int(level[0])
    characters[resonatorID]['ascension'] = [20, 40, 50, 60, 70, 80, 90].index(int(level[1]))

    return resonatorID, False

def scrapeWeapon(WIDTH, HEIGHT, image, characters, resonatorID):
    xName, yName, wName, hName = (
        scaleWidth(257, WIDTH),
        scaleHeight(126, HEIGHT),
        scaleWidth(273, WIDTH),
        scaleHeight(34, HEIGHT)
    )
    xLevel, yLevel, wLevel, hLevel = (
        scaleWidth(258, WIDTH),
        scaleHeight(165, HEIGHT),
        scaleWidth(102, WIDTH),
        scaleHeight(27, HEIGHT)
    )
    xRank, yRank, wRank, hRank = (
        scaleWidth(176, WIDTH),
        scaleHeight(356, HEIGHT),
        scaleWidth(92, WIDTH),
        scaleHeight(32, HEIGHT)
    )

    weaponName = pytesseract.image_to_string(image[yName:yName + hName, xName:xName + wName]).strip()
    weaponID = weaponsID.get(weaponName)
    level = pytesseract.image_to_string(image[yLevel:yLevel + hLevel, xLevel:xLevel + wLevel], config=f'--psm 7 -c tessedit_char_whitelist={string.digits}/').strip().split('/')
    rank = pytesseract.image_to_string(image[yRank:yRank + hRank, xRank:xRank + wRank], config=f'--psm 7 -c tessedit_char_whitelist={string.digits}')

    characters[resonatorID]['weapon']['id'] = weaponID
    characters[resonatorID]['weapon']['level'] = int(level[0])
    characters[resonatorID]['weapon']['ascension'] = [20, 40, 50, 60, 70, 80, 90].index(int(level[1]))
    characters[resonatorID]['weapon']['rank'] = int(rank)

def scrapeSkills(WIDTH, HEIGHT, characters, resonatorID):
    pydirectinput.leftClick(scaleWidth(460.5, WIDTH), scaleHeight(903, HEIGHT))
    time.sleep(.5)

    xLevel, yLevel, wLevel, hLevel = (
        scaleWidth(405, WIDTH),
        scaleHeight(110, HEIGHT),
        scaleWidth(58, WIDTH),
        scaleHeight(23, HEIGHT)
    )

    xButton, yButton, wButton, hButton = (
        scaleWidth(210, WIDTH),
        scaleHeight(985, HEIGHT),
        scaleWidth(110, WIDTH),
        scaleHeight(25, HEIGHT)
    )

    skillPositions = [
        (755, 905),
        (985, 765),
        (1260, 705),
        (1535, 765),
        (1760, 905)
    ]
    skillLegends = {
        0: 'normal',
        1: 'resonance',
        2: 'forte',
        3: 'liberation',
        4: 'intro'
    }

    for index, skills in enumerate(skillPositions):
        pydirectinput.leftClick(scaleWidth(skills[0], WIDTH), scaleHeight(skills[1], HEIGHT))
        time.sleep(.2)

        image = screenshot(0, 0, WIDTH, HEIGHT, bw=True)

        level = pytesseract.image_to_string(image[yLevel:yLevel + hLevel, xLevel:xLevel + wLevel], config='--psm 7 -c tessedit_char_whitelist=0123456789').strip()
        characters[resonatorID]['skills'][skillLegends[index]] = int(level)

        for y in range(1, 3):
            pydirectinput.leftClick(scaleWidth(skills[0], WIDTH), scaleHeight(skills[1] - (255 * y), HEIGHT))
            time.sleep(.1)

            image = screenshot(0, 0, WIDTH, HEIGHT)

            button = pytesseract.image_to_string(image[yButton:yButton + hButton, xButton:xButton + wButton]).strip()

            if button.lower() == 'activated':
                if index != 2:
                    key = f'stats{index}'
                else:
                    key = 'inherent'

                characters[resonatorID]['skills'][key] += 1
            else:
                break

        time.sleep(.2)
    pressEscape()
    time.sleep(.1)

def scrapeChain(WIDTH, HEIGHT, characters, resonatorID):
    chainPositions = [
        (1395, 140),
        (1565, 305),
        (1640, 535),
        (1565, 765),
        (1400, 935),
        (1170, 995),
    ]
    pydirectinput.leftClick(scaleWidth(1265, WIDTH), scaleHeight(135, HEIGHT))
    time.sleep(.7)
    for position in chainPositions:
        pydirectinput.leftClick(scaleWidth(position[0], WIDTH), scaleHeight(position[1], HEIGHT))
        time.sleep(.2)

        xButton, yButton, wButton, hButton = (
            scaleWidth(345, WIDTH),
            scaleHeight(896, HEIGHT),
            scaleWidth(108, WIDTH),
            scaleHeight(22, HEIGHT)
        )

        image = screenshot(0, 0, WIDTH, HEIGHT)
        text = pytesseract.image_to_string(image[yButton:yButton + hButton, xButton:xButton + wButton], config=f'-c tessedit_char_blacklist={string.punctuation}').strip()

        if text.lower() != 'activated':
            break

        characters[resonatorID]['chain'] += 1
    pressEscape()
    time.sleep(.1)

def dictify(d):
    if isinstance(d, defaultdict):
        d = {k: dictify(v) for k, v in d.items()}
    return d
