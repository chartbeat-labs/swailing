
import time


class TokenBucket(object):
    """Implements token bucket algorithm.

    https://en.wikipedia.org/wiki/Token_bucket
    """

    def __init__(self, fill_rate, capacity):
        self._fill_rate = float(fill_rate)
        self._capacity = float(capacity)
        self._count = float(capacity)
        self._last_fill = time.time()

        self.throttle_count = 0

    def check_and_consume(self):
        """Returns True if there is currently at least one token, and reduces
        it by one.

        """

        if self._count < 1.0:
            self._fill()

        consumable = self._count >= 1.0
        if consumable:
            self._count -= 1.0
            self.throttle_count = 0
        else:
            self.throttle_count += 1

        return consumable

    def __len__(self):
        """Returns current number of discrete tokens."""

        return int(self._count)

    def _fill(self):
        """Fills bucket with accrued tokens since last fill."""

        right_now = time.time()
        time_diff = right_now - self._last_fill
        if time_diff < 0:
            return

        self._count = min(
            self._count + self._fill_rate * time_diff,
            self._capacity,
        )
        self._last_fill = right_now
