import logging
import os
import sys

from elena.elena_bot import Elena
from elena.exchange_manager import Exchange
from elena.binance import Binance
from elena.logging import llog
from elena.record import Record
from elena.utils import get_time

binance = Exchange(Binance())
logging.basicConfig(filename='elena.log', level=logging.INFO, format='%(asctime)s %(message)s')

if len(sys.argv) > 1:
    robots = [sys.argv[1]]
else:
    robots = []
    dire = '.'
    for filename in os.listdir(dire):
        if filename.endswith('.json'):
            f = os.path.join(dire, filename)
            robots.append(f)

llog('time', get_time())
for robot_filename in robots:
    llog(robot_filename)
    elena = Elena(robot_filename, binance)
    Record.enable()
    elena.iterate()
