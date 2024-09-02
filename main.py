import os
import logging
from logging.handlers import TimedRotatingFileHandler
from app import start

def main():
	configure_logging()
	logger = logging.getLogger('WuWaInventoryKamera')
	logger.info("WuWa Inventory Kamera initialized")
	try:
		start()
	except Exception:
		logger.critical("Main application crashed", exc_info=True)
	logger.info("Application closed")

def configure_logging():
	os.makedirs('logs', exist_ok=True)

	# Create the formatter
	formatter = logging.Formatter(
		fmt='%(asctime)s|%(levelname)s|%(name)s|%(message)s'
	)

	# Debug file handler
	debug_file_handler = TimedRotatingFileHandler(
		filename='./logs/WuWaInventoryKamera.debug.log',
		when='midnight',
		interval=1,
		backupCount=4,
		encoding='utf-8'
	)
	debug_file_handler.setFormatter(formatter)
	debug_file_handler.setLevel(logging.DEBUG)

	# General log file handler
	log_file_handler = TimedRotatingFileHandler(
		filename='./logs/WuWaInventoryKamera.log',
		when='midnight',
		interval=1,
		backupCount=4,
		encoding='utf-8'
	)
	log_file_handler.setFormatter(formatter)
	log_file_handler.setLevel(logging.INFO)

	# Console handler
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	console_handler.setLevel(logging.DEBUG)

	# Get the root logger and configure it
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)
	root_logger.addHandler(console_handler)
	root_logger.addHandler(debug_file_handler)
	root_logger.addHandler(log_file_handler)
	
	# Disable propagation from pyuac
	pyuac_logger = logging.getLogger('pyuac')
	pyuac_logger.propagate = False


if __name__ == '__main__':
	main()
