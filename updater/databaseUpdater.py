import os
import re
import json
import urllib.request
import logging
from dataclasses import dataclass

from properties.config import basePATH
from scraping.utils import (
	itemsID, charactersID, weaponsID,
	echoesID, achievementsID, echoStats,
	definedText
)

logger = logging.getLogger('DatabaseManager')

@dataclass
class FileConfig:
	folder: list[str]
	file: str

class DataUpdater:
	API = 'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
	
	def __init__(self):
		self.author = 'Dimbreath'
		self.repo = 'WutheringData'
		self.files = [
			FileConfig(['TextMap', 'en'], 'MultiText.json'),
			FileConfig(['ConfigDB'], 'ItemInfo.json'),
			FileConfig(['ConfigDB'], 'WeaponConf.json'),
		]
		self.updated = False

	def makeFolder(self):
		os.makedirs('data', exist_ok=True)
		logger.debug("Ensured 'data' directory exists.")

	def fetchFileData(self, url: str) -> dict:
		with urllib.request.urlopen(urllib.request.Request(url)) as response:
			return json.loads(response.read().decode())

	def updateFiles(self):
		for fileConfig in self.files:
			url = self.API.format(
				owner=self.author,
				repo=self.repo,
				path='/'.join(fileConfig.folder + [fileConfig.file])
			)

			logger.info(f'Checking for updates on file: {fileConfig.file}')
			try:
				data = self.fetchFileData(url)
				filePath = f'./data/{fileConfig.file}'

				currentSize = os.path.getsize(filePath) if os.path.isfile(filePath) else 0

				if data['size'] != currentSize:
					logger.info(f'Downloading updated version of {fileConfig.file}...')
					urllib.request.urlretrieve(data['download_url'], filePath)
					self.updated = True
					logger.info(f'File updated: {fileConfig.file}')
					
			except Exception as e:
				logger.error(f'Failed to update {fileConfig.file}. Error: {str(e)}')

	def loadJson(self, filename: str) -> dict:
		with open(f'./data/{filename}', 'r', encoding='utf-8') as f:
			return json.load(f)

	def saveJson(self, data: dict, filename: str):
		with open(f'./data/{filename}', 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=4)

	def updateItems(self):
		if self.updated or not os.path.isfile('./data/items.json'):
			logger.info('Updating items.json...')
			try:
				infoText = self.loadJson('MultiText.json')
				itemInfo = self.loadJson('ItemInfo.json')
				weaponInfo = self.loadJson('WeaponConf.json')

				items = {
					infoText[item['Name']].lower().replace(' ', ''): {
						'id': item['Id'],
						'name': infoText[item['Name']],
						'image': os.path.join(basePATH, 'assets', item['Icon'].split('/Image/')[1].rsplit('.', 1)[0] + '.png')
					}
					for item in itemInfo if item['Name'] in infoText
				}
				weapons = {
					infoText[weapon['WeaponName']].lower().replace(' ', ''): {
						'id': weapon['ModelId'],
						'name': infoText[weapon['WeaponName']],
						'rarity': weapon['QualityId'],
						'image': os.path.join(basePATH, 'assets', weapon['Icon'].split('/Image/')[1].rsplit('.', 1)[0] + '.png')
					}
					for weapon in weaponInfo if weapon['WeaponName'] in infoText
				}

				self.saveJson(items, 'items.json')
				self.saveJson(weapons, 'weapons.json')

				itemsID.update(items)
				weaponsID.update(weapons)

			except Exception as e:
				logger.error(f'Failed to update items.json. Error: {str(e)}')

	def updateJsonFromPattern(self, fileName: str, pattern: str, transformFunc):
		if self.updated or not os.path.isfile(fileName):
			logger.info(f'Updating {fileName}...')
			try:
				infoText = self.loadJson('MultiText.json')
				
				data = {}
				compiledPattern = re.compile(pattern)
				for key in infoText:
					if match := compiledPattern.match(key):
						transformed = transformFunc(infoText[key], match)
						if transformed is not None:
							data[transformed] = int(match.group(1))

				self.saveJson(data, fileName)
				return data
			except Exception as e:
				logger.error(f'Failed to update {fileName}. Error: {str(e)}')

	def updateCharacters(self):
		data = self.updateJsonFromPattern(
			'characters.json',
			r'^RoleInfo_(\d+)_Name$',
			lambda text, match: text.lower().replace(' ', '') if int(match.group(1)) < 5000 else None
		)
		if data:
			charactersID.update(data)

	def updateEcho(self):
		data = self.updateJsonFromPattern(
			'echoes.json',
			r'^MonsterInfo_(\d+)_Name$',
			lambda text, match: text.lower().replace(' ', '') if int(match.group(1)) < 350000000 else None
		)
		if data:
			echoesID.update(data)

	def updateAchievements(self):
		data = self.updateJsonFromPattern(
			'achievements.json',
			r'^Achievement_(\d+)_Name$',
			lambda text, _: text
		)
		if data:
			achievementsID.update(data)

	def updateEchoStats(self):
		statsKey = {
			'PropertyIndex_10003_Name': 'hp',
			'PropertyIndex_10007_Name': 'atk',
			'PropertyIndex_10008_Name': 'cr',
			'PropertyIndex_10009_Name': 'cd',
			'PropertyIndex_10010_Name': 'def',
			'PropertyIndex_10011_Name': 'er',
			'PropertyIndex_10014_Name': 'skillDmg',
			'PropertyIndex_10017_Name': 'basicAttack',
			'PropertyIndex_10018_Name': 'heavyAttack',
			'PropertyIndex_10019_Name': 'liberationDmg',
			'PropertyIndex_10022_Name': 'glacio',
			'PropertyIndex_10023_Name': 'fusion',
			'PropertyIndex_10024_Name': 'electro',
			'PropertyIndex_10025_Name': 'aero',
			'PropertyIndex_10026_Name': 'spectro',
			'PropertyIndex_10027_Name': 'havoc',
			'PropertyIndex_10035_Name': 'healing'
		}

		try:
			infoText = self.loadJson('MultiText.json')
			
			stats = {infoText[key].lower().replace(' ', '').replace('.', ''): value
					 for key, value in statsKey.items()}
			
			self.saveJson(stats, 'echoStats.json')
			echoStats.update(stats)
			
		except Exception as e:
			logger.error(f'Failed to update echoStats. Error: {str(e)}')

	def updateDefinedText(self):
		textKey = [
			'PrefabTextItem_1547656443_Text', # Terminal
			'PrefabTextItem_2954494437_Text', # Complete
			'PrefabTextItem_2829957711_Text', # Ongoing
			'PrefabTextItem_128820487_Text', # Claim
			'PrefabTextItem_Activate_Text', # Activate
			'PrefabtextItem_Rogueskilltree_Max', # Activated
			'SkillType_4_TypeName', # Inherent Skill
			'VisionSkillTitle' # Echo Skill
		]

		try:
			infoText = self.loadJson('MultiText.json')
			
			stats = [infoText[key].lower().replace(' ', '').replace('-', '').strip()
					 for key in textKey]
			
			self.saveJson(stats, 'definedText.json')
			definedText.extend(stats)
			
		except Exception as e:
			logger.error(f'Failed to update definedText. Error: {str(e)}')

	def run(self):
		self.makeFolder()
		self.updateFiles()
		self.updateItems()
		self.updateEchoStats()
		self.updateDefinedText()
		self.updateAchievements()
		self.updateCharacters()
		self.updateEcho()