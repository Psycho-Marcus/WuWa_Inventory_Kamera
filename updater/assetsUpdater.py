import json
import urllib.request
import logging
from pathlib import Path
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal

from properties.config import basePATH

logger = logging.getLogger('AssetsUpdater')

@dataclass
class PathConfig:
	folder: list[str]
	sub: list[str]

class AssetsUpdater(QObject):
	updateProgress = Signal(int, str)
	updateFinished = Signal()

	API = 'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
	
	def __init__(self):
		super().__init__()
		self.author = 'Stormy-Waves'
		self.repo = 'WW_Icon'
		self.pathConfig = PathConfig(
			['UIResources', 'Common', 'Image'], 
			['IconA', 'IconC', 'IconCook', 'IconMout', 'IconMst', 'IconRup', 'IconTask', 'IconWup']
		)

	def makeFolder(self, filePath: Path) -> None:
		try:
			filePath.mkdir(parents=True, exist_ok=True)
		except Exception as e:
			logger.error(f"Failed to create folder: {e}", exc_info=True)

	def fetchFileData(self, url: str) -> dict:
		try:
			with urllib.request.urlopen(urllib.request.Request(url)) as response:
				return json.loads(response.read().decode())
		except:
			return {}
	
	def run(self) -> None:
		baseUrl = self.API.format(
			owner=self.author,
			repo=self.repo,
			path='/'.join(self.pathConfig.folder)
		)

		for folder in self.pathConfig.sub:
			path: Path = basePATH / 'assets' / folder
			self.makeFolder(path)
			
			folderUrl = '/'.join([baseUrl, folder])
			datas = self.fetchFileData(folderUrl)

			if datas and len(list(path.glob('*.*'))) != len(datas):
				for data in datas:
					filePath: Path = path / data['name']
					if not filePath.exists():
						try:
							urllib.request.urlretrieve(
								data['download_url'],
								filePath,
								reporthook=lambda block_num, block_size, total_size: self.reportProgress(f'{folder}/{data["name"]}', block_num, block_size, total_size)
							)
						except Exception as e:
							logger.error(f'Failed while downloading {folder}/{data["name"]}. Error: {e}')
		self.updateFinished.emit()
	
	def reportProgress(self, file_name, block_num, block_size, total_size):
		downloaded = block_num * block_size
		percent = (downloaded / total_size)*100
		self.updateProgress.emit(percent, file_name)
