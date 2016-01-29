
import logging
import json
import threading
from contextlib import contextmanager

from swailing.token_bucket import TokenBucket


PRIMARY = 10
DETAIL = 20
HINT = 30


class Logger(object):
    """A logging.Logger-like object with some swailing goodness.

    """

    def __init__(self,
                 name_or_logger,
                 fill_rate=None,
                 capacity=None,
                 verbosity=HINT,
                 structured_detail=False,
                 with_prefix=True):
        """Set up Logger-like object with some swailing goodness.

        name_or_logger is either a (possibly unicode) string or a
        logging.Logger-like object. If supplied as a string, we simply
        use logging.getLogger.

        fill_rate is the number of tokens per second Logger
        accumulates. Each log output consumes one token.

        capacity is the maximum number of tokens the Logger is allowed
        to have accumulated.

        verbosity is the initial verbosity level (defaults to HINT).
        Setting it to PRIMARY will stop detail and hint outputs.
        Setting it to DETAIL will stop hint outputs. Setting it to
        HINT allows all output.

        When structured_detail is True, logger.detail(msg) expects msg to be a
        dict and json dumps it when logging.

        When with_prefix is True, logger.detail and logger.hint will prefix
        their output with "DETAIL: " and
        "HINT: ", respectively.
        """

        if fill_rate and capacity:
            self._tb = TokenBucket(fill_rate, capacity)
        else:
            self._tb = None
        self._tb_lock = threading.Lock()

        if isinstance(name_or_logger, basestring):
            self._logger = logging.getLogger(name_or_logger)
        else:
            self._logger = name_or_logger

        self._verbosity = verbosity
        self._structured_detail = structured_detail
        self._with_prefix = with_prefix

    def debug(self, msg=None, *args, **kwargs):
        """Write log at DEBUG level. Same arguments as Python's built-in
        Logger.

        """

        return self._log(logging.DEBUG, msg, args, kwargs)

    def info(self, msg=None, *args, **kwargs):
        """Similar to DEBUG but at INFO level."""

        return self._log(logging.INFO, msg, args, kwargs)

    def warning(self, msg=None, *args, **kwargs):
        """Similar to DEBUG but at WARNING level."""

        return self._log(logging.WARNING, msg, args, kwargs)

    def error(self, msg=None, *args, **kwargs):
        """Similar to DEBUG but at ERROR level."""

        return self._log(logging.ERROR, msg, args, kwargs)

    def exception(self, msg=None, *args, **kwargs):
        """Similar to DEBUG but at ERROR level with exc_info set.

        https://github.com/python/cpython/blob/2.7/Lib/logging/__init__.py#L1472
        """
        kwargs['exc_info'] = 1
        return self._log(logging.ERROR, msg, args, kwargs)

    def critical(self, msg=None, *args, **kwargs):
        """Similar to DEBUG but at CRITICAL level."""

        return self._log(logging.CRITICAL, msg, args, kwargs)

    def log(self, level, msg=None, *args, **kwargs):
        """Writes log out at any arbitray level."""

        return self._log(level, msg, args, kwargs)

    def set_verbosity(self, level):
        self._verbosity = level


    def _log(self, level, msg, args, kwargs):
        """Throttled log output."""

        with self._tb_lock:
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

            return FancyLogContext(self._logger,
                                   level,
                                   self._verbosity,
                                   self._structured_detail,
                                   self._with_prefix)
        else:
            return NoopLogContext()


class FancyLogContext(object):
    """Accepts primary, detail, and hint log statements and outputs them
    when the context exits without error.

    """

    def __init__(self,
                 logger,
                 level,
                 verbosity,
                 structured_detail,
                 with_prefix):
        self._logger = logger
        self._level = level
        self._verbosity = verbosity
        self._log = {}
        self._structured_detail = structured_detail
        self._with_prefix = with_prefix

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # do not log anything if an exception occurs while forming the
        # log messages
        if exc_type or exc_value or traceback:
            return

        for msg, args, kwargs in self._log.values():
            self._logger.log(self._level, msg, *args, **kwargs)

    def primary(self, msg, *args, **kwargs):
        if self._verbosity >= PRIMARY:
            self._log[PRIMARY] = (msg, args, kwargs)

    def detail(self, msg, *args, **kwargs):
        spec = 'DETAIL: %s' if self._with_prefix else '%s'
        if self._verbosity >= DETAIL:
            if self._structured_detail:
                msg = spec % json.dumps(msg)
            else:
                msg = spec % msg

            self._log[DETAIL] = (msg, args, kwargs)

    def hint(self, msg, *args, **kwargs):
        spec = 'HINT: %s' if self._with_prefix else '%s'
        if self._verbosity >= HINT:
            self._log[HINT] = (spec % msg, args, kwargs)


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
