
import unittest

import mock

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
