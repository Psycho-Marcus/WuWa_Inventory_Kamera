import re
import mss
import cv2
import json
import ctypes
import numpy as np
import win32clipboard
from pathlib import Path

from properties.config import (
    cfg, INVENTORY, ocr
)

def loadFile(filePATH: str, default = {}) -> dict:
    try:
        with open(filePATH, 'r') as file:
            data = json.load(file)
            if isinstance(default, list):
                data = list(data)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return default

itemsID: dict = loadFile('./data/items.json')
charactersID: dict = loadFile('./data/characters.json')
weaponsID: dict = loadFile('./data/weapons.json')
echoesID: dict = loadFile('./data/echoes.json')
achievementsID: dict = loadFile('./data/achievements.json')
echoStats: dict = loadFile('./data/echoStats.json')
definedText: dict = loadFile('./data/definedText.json')
sonataName: list = loadFile('./data/sonataName.json', [])

def savingScraped(scannedData: dict = {'inventory_wuwainventorykamera.json': (INVENTORY['items'], dict)}, START_DATE: str = ''):
    savePATH: Path = Path(cfg.get(cfg.exportFolder)) / START_DATE
    
    if any(data != emptyType() for data, emptyType in scannedData.values()):
        savePATH.mkdir(parents=True, exist_ok=True)

        for filename, (data, emptyType) in scannedData.items():
            if data != emptyType():
                filePATH = savePATH / filename
                with open(filePATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f)

def screenshot(left: int = 0, top: int = 0, width: int = 0, height: int = 0, monitor: int = 1, bw: bool = False):

    with mss.mss() as sct:
        mon = sct.monitors[monitor]
        if all(coord == 0 for coord in [top, left, width, height]):
            left, top, width, height = tuple(coord for coord in mon.values())

        region = {
            'left': mon['left'] + left,
            'top': mon['top'] + top,
            'width': width,
            'height': height,
            'mon': monitor
        }
        image = np.array(sct.grab(region))
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    
    if bw:
        image = convertToBlackWhite(image)

    return image

def convertToBlackWhite(image: np.ndarray):
    if len(image.shape) == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    elif len(image.shape) == 2:
        gray = image
    else:
        raise ValueError(f"Unsupported image format. Image shape: {image.shape}")
    
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

def imageToString(
    image: np.ndarray, 
    divisor: str = ' ', 
    allowedChars: str = None, 
    bannedChars: str = None
) -> str:
    try:
        ocrResults = ocr(image)[0]
        
        banned_pattern = re.compile(f"[{re.escape(bannedChars)}]") if bannedChars else None
        allowed_pattern = re.compile(f"[^{re.escape(allowedChars)}]") if allowedChars else None
        
        lines = []
        for bbox, text, _ in ocrResults:
            if banned_pattern:
                text = banned_pattern.sub('', text)
            
            if allowed_pattern:
                text = allowed_pattern.sub('', text)
                
            lines.append((bbox, text))

        groupedLines = []
        currentRow = []
        lastY = None

        for bbox, text in lines:
            yMin = min(point[1] for point in bbox)
            yMax = max(point[1] for point in bbox)

            if lastY is None or (yMin < lastY + 10):
                currentRow.append(text)
            else:
                groupedLines.append(currentRow)
                currentRow = [text]
                
            lastY = yMax

        if currentRow:
            groupedLines.append(currentRow)

        finalOutput = []
        for row in groupedLines:
            finalOutput.append(divisor.join(row))
        
        return '\n'.join(finalOutput).strip()

    except:
        return ''

def isUserAdmin():
    return ctypes.windll.shell32.IsUserAnAdmin()

def copyToClipboard(text):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text)
    finally:
        win32clipboard.CloseClipboard()