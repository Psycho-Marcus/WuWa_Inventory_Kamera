from properties.config import cfg
from scraping.scraperManager import managerStart

from pyuac import isUserAdmin

def start():
    if isUserAdmin():
        scanners = {
            'characters': cfg.get(cfg.scanCharacters),
            'weapons': cfg.get(cfg.scanWeapons),
            'echoes': cfg.get(cfg.scanEchoes),
            'devItems': cfg.get(cfg.scanDevItems),
            'resources': cfg.get(cfg.scanResources),
        }
        enabled = [key for key, value in scanners.items() if value]
        if enabled:
            return managerStart(enabled)
        else:
            return ('warning', 'Warning', 'Select at least one scanner.')
    else:
        # type, Title, Content
        return ('warning', 'Warning', 'Administrator privileges not granted.\nTo use the scanner, administrator rights must be granted.')