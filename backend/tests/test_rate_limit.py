from services.security.rate_limit import SlidingWindowLimiter


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_allows_up_to_the_limit_then_refuses():
    clock = Clock()
    limiter = SlidingWindowLimiter(3, 60, clock)
    assert [limiter.allow("a") for _ in range(5)] == [True, True, True, False, False]


def test_keys_are_independent():
    limiter = SlidingWindowLimiter(1, 60, Clock())
    assert limiter.allow("a") and limiter.allow("b")
    assert not limiter.allow("a")


def test_the_window_slides():
    clock = Clock()
    limiter = SlidingWindowLimiter(2, 60, clock)
    assert limiter.allow("a")
    clock.now += 30
    assert limiter.allow("a")
    assert not limiter.allow("a")
    clock.now += 31
    assert limiter.allow("a")
    assert not limiter.allow("a")


def test_failures_can_be_counted_without_blocking():
    limiter = SlidingWindowLimiter(3, 60, Clock())
    for _ in range(2):
        limiter.add("a")
    assert limiter.count("a") == 2 and not limiter.blocked("a")
    limiter.add("a")
    assert limiter.blocked("a")
    limiter.clear("a")
    assert not limiter.blocked("a") and limiter.count("a") == 0


def test_retry_after_is_sensible():
    clock = Clock()
    limiter = SlidingWindowLimiter(1, 60, clock)
    assert limiter.retry_after("a") == 1
    limiter.allow("a")
    clock.now += 20
    assert 39 <= limiter.retry_after("a") <= 41


def test_old_keys_are_cleaned_up():
    clock = Clock()
    limiter = SlidingWindowLimiter(1, 60, clock)
    for i in range(5001):
        limiter.add(f"k{i}")
    clock.now += 120
    limiter.add("fresh")
    assert len(limiter._hits) < 100


def test_clear_everything():
    limiter = SlidingWindowLimiter(1, 60, Clock())
    limiter.allow("a")
    limiter.clear()
    assert limiter.allow("a")
