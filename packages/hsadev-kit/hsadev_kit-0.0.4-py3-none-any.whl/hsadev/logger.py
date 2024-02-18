import logging
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] <%(levelname)-7s> [%(funcName)-16s %(lineno)-4d] %(message)s',
        },
        'console': {
            'format': '[%(asctime)s] <%(levelname)-7s> %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'default',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file', 'console']
    }
})


def init(title, clean=True):
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    if clean:
        with open('debug.log', 'w'):
            pass

    logging.info('=' * (50 + len(title)))
    logging.info('=' * 25 + title + '=' * 25)
    logging.info('=' * (50 + len(title)))


def emphasis(msg):
    logging.info('-' * (10 + len(msg)))
    logging.info(msg)
    logging.info('-' * (10 + len(msg)))
