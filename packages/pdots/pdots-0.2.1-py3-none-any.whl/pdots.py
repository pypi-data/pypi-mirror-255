import sys
from time import sleep
from contextlib import contextmanager
from itertools import count

@contextmanager
def dots(every=1):
    def _dots():
        while True:
            for i, char in enumerate("⠁⠃⠇⡇⣇⣧⣷⣿"):
                if i:
                    yield f"\x08{char}"
                else:
                    yield char
    d = _dots()
    c = count()
    def step():
        if next(c) % every == 0:
            print(next(d), end="", flush=True, file=sys.stderr)
    try:
        print("\x1b[?25l", end="", flush=True, file=sys.stderr)
        yield step
    finally:
        print("\x1b[?25h", end="", flush=True, file=sys.stderr)


if __name__ == "__main__":
    with dots() as dot:
        for _ in range(48):
            dot()
            sleep(0.05)
