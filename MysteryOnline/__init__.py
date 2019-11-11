dev = False

MAJOR = 1
MINOR = 3
REVISION = 1


def set_dev(value: bool):
    global dev
    dev = value


def get_dev() -> bool:
    return dev


def get_version() -> str:
    return "v{0}.{1}.{2}".format(MAJOR, MINOR, REVISION)