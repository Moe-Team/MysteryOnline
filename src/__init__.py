connect = False


def set_connect(value: bool):
    global connect
    connect = value


def get_connect() -> bool:
    return connect
