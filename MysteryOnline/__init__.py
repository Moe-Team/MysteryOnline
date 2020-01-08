dev = False

PREFIX = "v"
MAJOR = 1
MINOR = 3
REVISION = 4
SUFFIX = " stable"


def set_dev(value: bool):
    global dev
    dev = value


def get_dev() -> bool:
    return dev


def get_version() -> str:
    return "{0}{1}.{2}.{3}{4}".format(PREFIX, MAJOR, MINOR, REVISION, SUFFIX)
