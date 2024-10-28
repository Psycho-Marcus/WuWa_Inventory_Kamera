import os
import sys
import time
import signal
import logging
import multiprocessing
from datetime import datetime

from properties.config import FAILED, INVENTORY
from scraping.utils import (
	savingScraped, presskey
)

from scraping.shellScraper import getShell
from scraping.itemsScraper import itemsScraper
from scraping.charactersScraper import resonatorScraper
from scraping.weaponsScraper import weaponScraper
from scraping.echoesScraper import echoScraper
from scraping.achievementsScraper import achievementScraper

from game.menu import MainMenuController
from game.screenSize import WindowManager
from game.screenInfo import ScreenInfo
from game.isForeground import isGameForeground
from game.foreground import WindowFocusManager
from game.stopKey import KeyPressChecker

logger = logging.getLogger('ScraperManager')

def managerStart(scraperEnabled: list):
	global INVENTORY, FAILED
	INVENTORY['date'] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

	result = MainMenuController().isInMainMenu()
	if result[0] == 'error':
		return result
	time.sleep(1.2)

	completeFLAG = multiprocessing.Event()
	queue = multiprocessing.Queue()
	
	scrapersProcess = multiprocessing.Process(target=scrapers, args=(scraperEnabled, WindowManager.getScreenInfo(), completeFLAG, queue, INVENTORY['date']))
	scrapersProcess.start()

	stopMonitor = multiprocessing.Process(target=needToStop, args=(scrapersProcess.pid, completeFLAG, WindowFocusManager().getGamePID()))
	stopMonitor.start()

	scrapersProcess.join()
	
	stopMonitor.terminate()
	stopMonitor.join()

	try:
		timeout = 60
		start_time = time.time()
		
		while time.time() - start_time < timeout:
			try:
				scraperResult = queue.get_nowait()
				INVENTORY['items'].update(scraperResult['inventory'])
				FAILED.extend(scraperResult['failed'])
			except multiprocessing.queues.Empty:
				break
			except Exception as e:
				logger.error(f"Error processing queue item: {e}")
				continue
		
		while True:
			try:
				queue.get_nowait()
			except:
				break
				
	except Exception as e:
		logger.error(f"Fatal error processing queue: {e}")
		return ('failed', 'Queue processing error', str(e))
	finally:
		queue.close()
		queue.join_thread()

	savingScraped(START_DATE=INVENTORY['date'])

	if len(FAILED) > 0:
		return ('failed', 'Failed to recognize', f'Failed to recognize {len(FAILED)} items.')
	else:
		return ('success', 'Complete', f'Scan completed with no errors.')


def needToStop(tPID, completeFLAG, PROCESS_ID):
	keyPress = KeyPressChecker()

	while not completeFLAG.is_set():
		# Check if the game is no longer in the foreground or if the key is pressed
		if not isGameForeground().isForeground(PROCESS_ID) or keyPress.isPressed():
			try:
				os.kill(tPID, signal.SIGTERM)
				logger.debug("Terminated scraper process due to key press or game not in foreground.")
			except Exception as e:
				logger.error(f"Error terminating process: {e}")
			sys.exit(0)
		time.sleep(.1)

def scrapers(scraperEnabled: list, screenInfo: ScreenInfo, FLAG: multiprocessing.Event, queue: multiprocessing.Queue, START_DATE: str): # type: ignore
	try:
		resonator = dict()
		inventory = dict()
		failed = list()
		weapons = list()
		echoes = list()
		achievements = list()

		for scraper in scraperEnabled:
			presskey('esc', .5)

			match(scraper):
				case 'characters':
					resonator = resonatorScraper(screenInfo)
				case 'weapons':
					i, w = weaponScraper(screenInfo.scaleWidth((81.5, 71.5)), screenInfo.scaleHeight((191.5, 167)), screenInfo)
					inventory.update(i)
					weapons.extend(w)
				case 'echoes':
					echoes = echoScraper(screenInfo.scaleWidth((81.5, 71.5)), screenInfo.scaleHeight((326.5, 285)), screenInfo)
				case 'devItems':
					i, f = itemsScraper(START_DATE, screenInfo.scaleWidth((81.5, 71.5)), screenInfo.scaleHeight((596.5, 521)), screenInfo)
					inventory.update(i)
					failed.extend(f)
				case 'resources':
					i, f = itemsScraper(START_DATE, screenInfo.scaleWidth((81.5, 71.5)), screenInfo.scaleHeight((731.5, 639)), screenInfo)
					inventory.update(i)
					failed.extend(f)
				case 'achievements':
					achievements = achievementScraper(screenInfo)

			if scraper not in ['characters', 'achievements']:
				if '2' not in inventory or inventory.get('2') == 0:
					shell = getShell(screenInfo)
					inventory = {**shell, **inventory}

		presskey('esc')

		chunkSize = 20
		inventoryItems = list(inventory.items())
		
		for i in range(0, len(inventoryItems), chunkSize):
			chunk = dict(inventoryItems[i:i + chunkSize])
			queue.put({
				'inventory': chunk,
				'failed': failed[i:i + chunkSize] if failed else []
			})
			
		FLAG.set()
		savingScraped({
			'characters_wuwainventorykamera.json': (resonator, dict),
			'weapons_wuwainventorykamera.json': (weapons, list),
			'echoes_wuwainventorykamera.json': (echoes, list),
			'achievements_wuwainventorykamera.json': (achievements, list),
		}, START_DATE)

	except Exception as e:
		FLAG.set()
		logger.error(f"Error in scrapers: {e}")
		queue.put({
			'inventory': {},
			'failed': ['Scraper error: ' + str(e)]
		})
