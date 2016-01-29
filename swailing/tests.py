
import logging
import unittest

import mock

import swailing.logger
import swailing.token_bucket
from swailing.token_bucket import TokenBucket


class TokenBucketTest(unittest.TestCase):
    """TokenBucket test.

    Since TokenBucket depends on time.time(), we mock it out. The
    `clock.return_value = X` statements set the clock to that time.

    """

    @mock.patch('swailing.token_bucket.time.time')
    def test_simple(self, clock):
        clock.return_value = 1
        tb = TokenBucket(10, 100)
        self.assertEqual(len(tb), 100)
        self.assertTrue(tb.check_and_consume())

    @mock.patch('swailing.token_bucket.time.time')
    def test_throttle(self, clock):
        clock.return_value = 1
        tb = TokenBucket(10, 100)

        # we get to consume 100 tokens...
        for i in xrange(100):
            self.assertTrue(tb.check_and_consume())

        # ...then next one fails
        self.assertFalse(tb.check_and_consume())

        # fill halfway and check level
        clock.return_value += 0.5
        tb._fill()
        self.assertEqual(len(tb), 5)

        clock.return_value += 0.5
        tb._fill()
        self.assertEqual(len(tb), 10)

        # this fill maxes out capacity
        clock.return_value += 10
        tb._fill()
        self.assertEqual(len(tb), 100)

        # attempt to consume more than allowed then check throttle
        # count
        for i in xrange(123):
            tb.check_and_consume()
        self.assertEqual(tb.throttle_count, 23)

        # fill, consume, then check throttle count again
        clock.return_value += 1
        tb.check_and_consume()
        self.assertEqual(tb.throttle_count, 0)


class LoggerTest(unittest.TestCase):
    def test_fallback(self):
        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger, 10, 100,
                                 structured_detail=False, with_prefix=False)

        logger.info("hello world!")
        mock_logger.log.assert_called_with(
            logging.INFO,
            "hello world!",
        )

    def test_context(self):
        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger, 10, 100,
                                 structured_detail=False, with_prefix=False)
        with logger.info() as L:
            L.primary("primary")
            L.detail("detail")
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
            mock.call(logging.INFO, "detail"),
            mock.call(logging.INFO, "hint"),
        ]
        mock_logger.log.assert_has_calls(calls)

    def test_no_rate(self):
        """Simple test without rate limiting."""

        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger,
                                 structured_detail=False, with_prefix=False)
        with logger.info() as L:
            L.primary("primary")
            L.detail("detail")
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
            mock.call(logging.INFO, "detail"),
            mock.call(logging.INFO, "hint"),
        ]
        mock_logger.log.assert_has_calls(calls)

    @mock.patch('swailing.token_bucket.time.time')
    def test_throttle(self, clock):
        mock_logger = mock.Mock()
        clock.return_value = 1
        logger = swailing.Logger(mock_logger, 1, 2,
                                 structured_detail=False, with_prefix=False)

        # We'll write a buch of times, but since capacity is just 2,
        # we should expect the root_logger to only have been called
        # twice.
        for i in xrange(10):
            with logger.info() as L:
                L.primary("primary %d" % i)
                L.detail("detail %d" % i)
                L.hint("hint %d" % i)

        calls = [
            mock.call(logging.INFO, "primary 0"),
            mock.call(logging.INFO, "detail 0"),
            mock.call(logging.INFO, "hint 0"),

            mock.call(logging.INFO, "primary 1"),
            mock.call(logging.INFO, "detail 1"),
            mock.call(logging.INFO, "hint 1"),
        ]
        mock_logger.log.assert_has_calls(calls)


        # Now let's wait a second so we get one more token, then run test again.
        clock.return_value += 1
        mock_logger.reset_mock()

        for i in xrange(10):
            with logger.info() as L:
                L.primary("primary %d" % i)
                L.detail("detail %d" % i)
                L.hint("hint %d" % i)

        calls = [
            mock.call(logging.INFO, "primary 0"),
            mock.call(logging.INFO, "detail 0"),
            mock.call(logging.INFO, "hint 0"),
        ]
        mock_logger.log.assert_has_calls(calls)


        # Force a throttle message.
        clock.return_value += 100
        mock_logger = mock.Mock()
        logging.basicConfig()
        logger = swailing.Logger(mock_logger, 1, 1,
                                 structured_detail=False, with_prefix=False)
        for i in xrange(10):
            logger.error("foo")
        clock.return_value += 100
        logger.error("bar")

        calls = [
            mock.call(logging.ERROR, "foo"),
            mock.call(logging.ERROR, ""),
            mock.call(logging.ERROR, "(... throttled %d messages ...)", 9),
            mock.call(logging.ERROR, ""),
            mock.call(logging.ERROR, "bar"),
        ]
        mock_logger.log.assert_has_calls(calls)

    def test_verbosity(self):
        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger,
                                 10,
                                 100,
                                 verbosity=swailing.PRIMARY,
                                 structured_detail=False,
                                 with_prefix=False)
        with logger.info() as L:
            L.primary("primary")
            L.detail("detail")
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
        ]
        self.assertEqual(mock_logger.log.mock_calls, calls)

        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger,
                                 10,
                                 100,
                                 verbosity=swailing.DETAIL,
                                 structured_detail=False,
                                 with_prefix=False)
        with logger.info() as L:
            L.primary("primary")
            L.detail("detail")
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
            mock.call(logging.INFO, "detail"),
        ]
        self.assertEqual(mock_logger.log.mock_calls, calls)

        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger,
                                 10,
                                 100,
                                 verbosity=swailing.HINT,
                                 structured_detail=False,
                                 with_prefix=False)
        with logger.info() as L:
            L.primary("primary")
            L.detail("detail")
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
            mock.call(logging.INFO, "detail"),
            mock.call(logging.INFO, "hint"),
        ]
        self.assertEqual(mock_logger.log.mock_calls, calls)

    def test_with_prefix(self):
        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger, 10, 100,
                                 structured_detail=False, with_prefix=True)
        with logger.info() as L:
            L.primary("primary")
            L.detail("detail")
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
            mock.call(logging.INFO, "DETAIL: detail"),
            mock.call(logging.INFO, "HINT: hint"),
        ]
        mock_logger.log.assert_has_calls(calls)

    def test_with_structured_detail(self):
        mock_logger = mock.Mock()
        logger = swailing.Logger(mock_logger, 10, 100,
                                 structured_detail=True, with_prefix=False)
        with logger.info() as L:
            L.primary("primary")
            L.detail({"my":"dict"})
            L.hint("hint")

        calls = [
            mock.call(logging.INFO, "primary"),
            mock.call(logging.INFO, '{"my": "dict"}'),
            mock.call(logging.INFO, "hint"),
        ]
        mock_logger.log.assert_has_calls(calls)
