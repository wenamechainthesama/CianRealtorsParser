import enum


class ProxyStatus(enum.Enum):
    ready = 1
    busy = 2
    banned = 3
