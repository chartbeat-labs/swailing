
import logging

from swailing import Logger

logging.basicConfig()

logger = Logger(logging.getLogger(), 10, 100)
logger.error('hello world')

with logger.warning() as L:
    L.primary('this is the primary %d', 1234)
    L.detail('some extra detail: %s failed', 'syscall')
    L.hint('you ought to do ...')
