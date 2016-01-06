
import logging
from contextlib import contextmanager

from swailing.token_bucket import TokenBucket


class Logger(object):
    """A logging.Logger-like object with some swailing goodness.

    """

    def __init__(self, name_or_logger, fill_rate=None, capacity=None):
        if fill_rate and capacity:
            self._tb = TokenBucket(fill_rate, capacity)
        else:
            self._tb = None

        if isinstance(name_or_logger, basestring):
            self._logger = logging.getLogger(name_or_logger)
        else:
            self._logger = name_or_logger

    def debug(self, msg=None, *args, **kwargs):
        return self._log(logging.DEBUG, msg, args, kwargs)

    def info(self, msg=None, *args, **kwargs):
        return self._log(logging.INFO, msg, args, kwargs)

    def warning(self, msg=None, *args, **kwargs):
        return self._log(logging.WARNING, msg, args, kwargs)

    def error(self, msg=None, *args, **kwargs):
        return self._log(logging.ERROR, msg, args, kwargs)

    def critical(self, msg=None, *args, **kwargs):
        return self._log(logging.CRITICAL, msg, args, kwargs)

    def log(self, level, msg=None, *args, **kwargs):
        return self._log(level, msg, args, kwargs)


    def _log(self, level, msg, args, kwargs):
        if self._tb is None:
            throttled = 0
            should_log = True
        else:
            throttled = self._tb.throttle_count
            should_log = self._tb.check_and_consume()

        if should_log:
            if throttled > 0:
                self._logger.log(level, "")
                self._logger.log(
                    level,
                    "(... throttled %d messages ...)",
                    throttled,
                )
                self._logger.log(level, "")

            if msg is not None:
                self._logger.log(level, msg, *args, **kwargs)

            return FancyLogContext(self._logger, level)
        else:
            return NoopLogContext()


class FancyLogContext(object):
    def __init__(self, logger, level):
        self._logger = logger
        self._level = level
        self._log = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # do not log anything if an exception occurs while forming the
        # log messages
        if exc_type or exc_value or traceback:
            return

        for log_message in ['primary', 'detail', 'hint']:
            info = self._log.get(log_message)
            if not info:
                continue

            msg, args, kwargs = info
            self._logger.log(self._level, msg, *args, **kwargs)

    def primary(self, msg, *args, **kwargs):
        self._log['primary'] = (msg, args, kwargs)

    def detail(self, msg, *args, **kwargs):
        self._log['detail'] = (msg, args, kwargs)

    def hint(self, msg, *args, **kwargs):
        self._log['hint'] = (msg, args, kwargs)


class NoopLogContext(object):
    """Fakes a FancyLogContext but does nothing."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def primary(self, msg, *args, **kwargs):
        pass

    def detail(self, msg, *args, **kwargs):
        pass

    def hint(self, msg, *args, **kwargs):
        pass
