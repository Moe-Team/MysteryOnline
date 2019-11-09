dev = False


def set_dev(value: bool):
    global dev
    dev = value


def get_dev() -> bool:
    return dev
