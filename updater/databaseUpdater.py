import os
import re
import json
import urllib.request
import logging

from properties.config import basePATH
from scraping.utils import itemsID, charactersID, weaponsID, echoesID, achievementsID

logger = logging.getLogger('DatabaseManager')

class DataUpdater():
	def __init__(self):
		self.API = 'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
		self.author = 'Dimbreath'
		self.repo = 'WutheringData'
		self.files = [
			{
				'folder': ['TextMap', 'en'],
				'file': 'MultiText.json'
			},
			{
				'folder': ['ConfigDB'],
				'file': 'ItemInfo.json'
			},
			{
				'folder': ['ConfigDB'],
				'file': 'WeaponConf.json'
			},
		]
		self.updated = False

	def _make_folder(self):
		"""Create the data directory if it does not exist."""
		if not os.path.isdir(os.path.join(basePATH, 'data')):
			os.makedirs('data')
			logger.debug("Created 'data' directory.")

	def _fetch_file_data(self, url):
		"""Fetch the file data from the given URL."""
		request = urllib.request.Request(url)
		with urllib.request.urlopen(request) as response:
			content = response.read().decode()
			return json.loads(content)

	def update_files(self):
		"""Check and update files from the remote API."""
		for paths in self.files:
			url = self.API.format(
				owner=self.author,
				repo=self.repo,
				path='/'.join(paths['folder'] + [paths['file']])
			)

			logger.info(f"Checking for updates on file: {paths['file']}")
			try:
				data = self._fetch_file_data(url)
				file_path = f'./data/{paths["file"]}'

				current_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0

				if data['size'] != current_size:
					logger.info(f"Downloading updated version of {paths['file']}...")
					urllib.request.urlretrieve(data['download_url'], file_path)
					self.updated = True
					logger.info(f"File updated: {paths['file']}")
					
			except Exception as e:
				logger.error(f"Failed to update {paths['file']}. Error: {str(e)}")

	def update_items(self):
		"""Update items.json based on MultiText.json and ItemInfo.json."""
		if self.updated or not os.path.isfile('./data/items.json'):
			logger.info("Updating items.json...")
			try:
				with open('./data/MultiText.json', 'r', encoding='utf-8') as f:
					info_text = json.load(f)

				with open('./data/ItemInfo.json', 'r', encoding='utf-8') as f:
					item_info = json.load(f)

				with open('./data/WeaponConf.json', 'r', encoding='utf-8') as f:
					weapon_info = json.load(f)

				items = {
					info_text[item['Name']]: {
						'id': item['Id'],
						'image': os.path.join(basePATH, 'assets', item['Icon'].split('/Image/')[1].rsplit('.', 1)[0] + '.png')
					}
					for item in item_info if item['Name'] in info_text
				}
				weapons = {
					info_text[weapon['WeaponName']]: {
						'id': weapon['ModelId'],
						'rarity': weapon['QualityId'],
						'image': os.path.join(basePATH, 'assets', weapon['Icon'].split('/Image/')[1].rsplit('.', 1)[0] + '.png')
					}
					for weapon in weapon_info if weapon['WeaponName'] in info_text
				}

				with open('./data/items.json', 'w', encoding='utf-8') as f:
					json.dump(items, f, indent=4)

				itemsID.update(items)

				with open('./data/weapons.json', 'w', encoding='utf-8') as f:
					json.dump(weapons, f, indent=4)

				itemsID.update(items)
				weaponsID.update(weapons)

			except Exception as e:
				logger.error(f"Failed to update items.json. Error: {str(e)}")

	def update_data(self, data_type, pattern_str):
		"""Update json file based on MultiText.json."""
		file_name = f'./data/{data_type}.json'
		if self.updated or not os.path.isfile(file_name):
			logger.info(f"Updating {data_type}.json...")
			try:
				with open('./data/MultiText.json', 'r', encoding='utf-8') as f:
					info_text = json.load(f)

				pattern = re.compile(pattern_str)
				data = {
					info_text[key]: int(match.group(1))
					for key in info_text
					if (match := pattern.match(key))
				}

				with open(file_name, 'w', encoding='utf-8') as f:
					json.dump(data, f, indent=4)
				
				globals()[f"{data_type}ID"].update(data)

			except Exception as e:
				logger.error(f"Failed to update {file_name}. Error: {str(e)}")

	def run(self):
		"""Run the data update process."""
		self._make_folder()
		self.update_files()
		self.update_items()
		self.update_data('characters', r'^RoleInfo_(\d+)_Name$')
		self.update_data('echoes', r'^MonsterInfo_(\d+)_Name$')
		self.update_data('achievements', r'^Achievement_(\d+)_Name$')
