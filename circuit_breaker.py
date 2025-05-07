import time


class CircuitBreaker:
    def __init__(self, fail_max=3, reset_timeout=10):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.state = 'CLOSED'
        self.opened_at = None

    def call(self, func, *args, **kwargs):
        now = time.time()

        if self.state == 'OPEN':
            if now - self.opened_at > self.reset_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise RuntimeError("Circuit is open")

        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.fail_count = 0
            return result
        except Exception:
            self.fail_count += 1
            if self.fail_count >= self.fail_max:
                self.state = 'OPEN'
                self.opened_at = now
            raise
