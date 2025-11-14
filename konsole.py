import sys


def log(*args):
    if sys.stdin and sys.stdin.isatty():
        text = " ".join(str(a) for a in args)
        return sys.stdout.write(text.strip() + "\n")


def hr():
    return log("===============================================")


def header(*args):
    hr()
    for arg in args:
        log(arg)
    hr()
