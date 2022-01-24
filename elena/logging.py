import logging
from logging.config import dictConfig

# Logs
def llog(*arguments):
    for arg in arguments.items():
        logging.info(arg)
