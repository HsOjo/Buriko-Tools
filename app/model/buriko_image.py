from ..driver.hsio import HsIO


class BurikoImage(HsIO):
    magic = 'CompressedBG___'

    def __init__(self, path):
        super().__init__(path)

        self._load()

    def _load(self):
        self.seek(0)
        magic = self.read_string(len(BurikoImage.magic) + 1, 'shift_jis', True)
        [w, h, bit, _, _, _, u1, u2, u3, u4] = self.read_param('<2H4I2H2I')
        print(w, h, bit, u1, u2, u3, u4)
