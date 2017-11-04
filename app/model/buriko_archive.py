from os import walk

from ..driver.hsio import HsIO


class BurikoArchive(HsIO):
    h_mask = 'BURIKO ARC20'

    def __init__(self, path):
        super().__init__(path)
        self.srcs = {}
        self._load()

    def _load(self):
        self.seek(0)
        h_mask = self.read_string(len(BurikoArchive.h_mask), 'shift_jis', True)
        if h_mask == BurikoArchive.h_mask:
            [src_count] = self.read_param('<i')
            srcs = {}
            for i in range(src_count):
                name = self.read_string(96, 'shift_jis', True)
                [offset, size, _, _, _, _, raw, _] = self.read_param('<8i')
                srcs[name] = {'offset': offset, 'size': size, 'raw': bool(raw)}
            head_offset = self.tell()

            for i in srcs:
                srcs[i]['offset'] += head_offset

            self.srcs = srcs

    def _load_data(self, name):
        src = self.srcs[name]
        src['data'] = self.read_range(src['offset'], src['size'])

    def _destroy_data(self, name):
        src = self.srcs[name]
        del src['data']

    @staticmethod
    def create(src: dict, path):
        io = HsIO(path, mode='w')
        io.write_string(BurikoArchive.h_mask, zero_over=False)
        io.write_param('<i', len(src))
        offset = 0
        for i in sorted(src):
            io.write_string(i, length=96)
            size = len(src[i]['data'])
            io.write_param('<8i', offset, size, 0, 0, 0, 0, int(src[i]['raw']), 0)
            offset += size

        for i in sorted(src):
            io.write(src[i]['data'])

    @staticmethod
    def create_by_dir(p_out, *args):
        src = {}
        for p_in in args:
            for n, ds, fs in walk(p_in):
                for f in fs:
                    with open('%s/%s' % (n, f), 'br') as io:
                        data = io.read()
                        src[f] = {'data': data, 'raw': True}
                break

        BurikoArchive.create(src, p_out)

    def extract_all(self, p_out):
        for name in self.srcs:
            self._load_data(name)
            src = self.srcs[name]
            with open('%s/%s' % (p_out, name), 'bw') as io:
                io.write(src['data'])
            self._destroy_data(name)
            print(name)
