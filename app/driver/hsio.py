from io import BytesIO, FileIO, IOBase
from struct import unpack, calcsize, pack

from chardet import detect


class HsIO(IOBase):
    def __init__(self, path=None, mode='r'):
        super().__init__()
        self.io = None
        if type(path) == str:
            self.io = FileIO(path, 'b' + mode)
        else:
            self.io = BytesIO(path)
        HsIO.__overwrite__(self.io, self)

    @staticmethod
    def __overwrite__(core, ins):
        ins.read = core.read
        ins.write = core.write
        ins.seek = core.seek
        ins.tell = core.tell
        ins.close = core.close
        ins.readline = core.readline
        ins.fileno = core.fileno
        ins.flush = core.flush
        ins.isatty = core.isatty
        ins.readable = core.readable
        ins.readlines = core.readlines
        ins.seekable = core.seekable
        ins.truncate = core.truncate
        ins.writable = core.writable
        ins.writelines = core.writelines

    def peek(self, *args, **kwargs):
        p = self.tell()
        data = self.read(*args, **kwargs)
        self.seek(p)
        return data

    def read(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass

    def read_string(self, maxsize=-1, encoding='auto', to_ms=False):
        tgt = 0
        if to_ms:
            tgt = self.tell() + maxsize

        ret_bytes = b''
        while len(ret_bytes) < maxsize or maxsize == -1:
            data = self.read(1)
            if len(data) != 1:
                break
            if data != b'\x00':
                ret_bytes += data
            else:
                break

        if to_ms:
            self.seek(tgt)

        if encoding == 'auto':
            encoding = detect(ret_bytes)['encoding']

        if encoding is None:
            ret = ret_bytes
        else:
            ret = ret_bytes.decode(encoding, errors='ignore')
        return ret

    def read_param(self, mask, fix=True):
        size = calcsize(mask)
        data = self.read(size)
        if fix:
            for i in range(size - len(data)):
                data += b'\x00'
        return unpack(mask, data)

    def read_range(self, offset, size=-1, rec=True):
        rec_pos = self.tell()
        self.seek(offset)
        ret = self.read(size)
        if rec:
            self.seek(rec_pos)
        return ret

    def write_param(self, mask, *args):
        self.write(pack(mask, *args))

    def size(self):
        pos = self.tell()
        self.seek(0, 2)
        ret = self.tell()
        self.seek(pos)
        return ret

    def write_string(self, content: str, encoding='utf8', zero_over=True, length=None):
        data = content.encode(encoding, errors='ignore')
        self.write(data)
        if length is not None:
            f_len = length - len(data)
            if f_len > 0:
                self.write(bytes(f_len))
        elif zero_over:
            self.write(b'\x00')
