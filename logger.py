import logging
from datetime import datetime


class AppLogger:
    def __init__(self):
        logging.basicConfig(
            filename=f'app_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log(self, message, level='info'):
        getattr(logging, level)(message)