import logging
from logging.config import dictConfig

# Logs
def llog(*arguments):
    for message in arguments:
        logging.info(message)
