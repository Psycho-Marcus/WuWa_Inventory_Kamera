from properties.config import cfg
from scraping.utils.common import isUserAdmin
from scraping.scraperManager import managerStart

def startScraper():
    if isUserAdmin():
        scanners = {
            'characters': cfg.get(cfg.scanCharacters),
            'weapons': cfg.get(cfg.scanWeapons),
            'echoes': cfg.get(cfg.scanEchoes),
            'devItems': cfg.get(cfg.scanDevItems),
            'resources': cfg.get(cfg.scanResources),
            'achievements': cfg.get(cfg.scanAchievements),
        }
        enabled = [key for key, value in scanners.items() if value]
        enabled = ['achievements'] if 'achievements' in enabled else enabled

        if enabled:
            return managerStart(enabled)
        else:
            return ('warning', 'Warning', 'Select at least one scanner.')
    else:
        # type, Title, Content
        return ('warning', 'Warning', 'Administrator privileges not granted.\nTo use the scanner, administrator rights must be granted.')