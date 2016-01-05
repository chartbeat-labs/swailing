
import logging

from swailing import Logger

logging.basicConfig()

logger = Logger(logging.getLogger(), 1, 100)
logger.error('hello world')

counter = 0
while True:
    with logger.warning() as L:
        L.primary('this is the primary %d', counter)
        L.detail('some extra detail: %s failed', 'syscall')
        L.hint('you ought to do ...')

    counter += 1
