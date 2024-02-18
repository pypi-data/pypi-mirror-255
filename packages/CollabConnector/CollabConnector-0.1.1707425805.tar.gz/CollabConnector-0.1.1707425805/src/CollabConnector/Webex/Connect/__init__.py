from .TXT import TXT
from .REST import REST


class Connect:
    def __init__(self, key=None):
        self.rest = REST(key)
        self.txt = TXT(self)
