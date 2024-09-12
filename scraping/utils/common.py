import os
import mss
import cv2
import json
import numpy as np

from properties.config import (
    cfg, INVENTORY
)

def loadFile(filePATH: str) -> dict:
    try:
        with open(filePATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

itemsID = loadFile('./data/items.json')
charactersID = loadFile('./data/characters.json')
weaponsID = loadFile('./data/weapons.json')
echoesID = loadFile('./data/echoes.json')
achievementsID = loadFile('./data/achievements.json')

def savingScraped(scannedData: dict = {'inventory_wuwainventorykamera.json': (INVENTORY['items'], dict)}, START_DATE: str = ''):
    savePATH = os.path.join(cfg.get(cfg.exportFolder), START_DATE)
    
    if any(data != emptyType() for data, emptyType in scannedData.values()):
        os.makedirs(savePATH, exist_ok=True)

        for filename, (data, emptyType) in scannedData.items():
            if data != emptyType():
                filePATH = os.path.join(savePATH, filename)
                with open(filePATH, 'w', encoding='UTF-8') as f:
                    json.dump(data, f)

def scaleWidth(value, width):
    return int(value / 1920 * width)

def scaleHeight(value, height):
    return int(value / 1080 * height)

def screenshot(left: int = 0, top: int = 0, width: int = 0, height: int = 0, bw: bool = False):

    region = {
        'left': left,
        'top': top,
        'width': width,
        'height': height
    }

    with mss.mss() as sct:
        image = np.array(sct.grab(region))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    if bw:
        image = convertToBlackWhite(image)

    return image

def convertToBlackWhite(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrasted = clahe.apply(gray)
    
    blurred = cv2.GaussianBlur(contrasted, (3, 3), 0)
    
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    if np.mean(thresh) > 127: thresh = cv2.bitwise_not(thresh)
    
    kernel = np.ones((2,2), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(morph, -1, sharpen_kernel)

    return sharpened
