
# Logs
import logging


def llog(*arguments):
    for message in arguments:
        logging.info(message)
