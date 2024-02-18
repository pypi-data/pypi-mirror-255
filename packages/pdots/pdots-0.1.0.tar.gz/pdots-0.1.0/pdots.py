from time import sleep
from contextlib import contextmanager

@contextmanager
def dots():
    def _dots():
        while True:
            for i, char in enumerate("⠁⠃⠇⡇⣇⣧⣷⣿"):
                if i:
                    yield f"\x08{char}"
                else:
                    yield char
    d = _dots()
    def step():
        print(next(d), end="", flush=True)
    try:
        print("\x1b[?25l", end="", flush=True)
        yield step
    finally:
        print("\x1b[?25h", end="", flush=True)


if __name__ == "__main__":
    with dots() as dot:
        for _ in range(48):
            dot()
            sleep(0.05)
