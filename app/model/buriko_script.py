from json import dump as json_dump, load as json_load

from ..driver.baidu_translate import BaiduTranslate
from ..driver.hsio import HsIO


class BurikoScript():
    h_magic = 'BurikoCompiledScriptVer1.00'
    command = {
        # body
        0: {'param': 1},  # 00 00 00 00
        1: {'param': 1},  # 01 00 00 00
        2: {'param': 0},  # 02 00 00 00
        3: {'param': 1},  # 03 00 00 00, text
        4: {'param': 0},  # 04 00 00 00
        9: {'param': 0},  # 09 00 00 00
        16: {'param': 0},  # 10 00 00 00
        17: {'param': 0},  # 11 00 00 00
        24: {'param': 0},  # 18 00 00 00
        25: {'param': 1},  # 19 00 00 00
        27: {'param': 1},  # 1b 00 00 00, end
        28: {'param': 0},  # 1c 00 00 00
        32: {'param': 0},  # 20 00 00 00
        33: {'param': 0},  # 21 00 00 00
        48: {'param': 0},  # 30 00 00 00
        56: {'param': 0},  # 38 00 00 00
        63: {'param': 2},  # 3f 00 00 00

        123: {'param': 1},  # 7B 00 00 00
        127: {'param': 2},  # 7f 00 00 00
        320: {'param': 0},  # 40 01 00 00
        # foot
        249: {'param': 0},  # f9 00 00 00
        244: {'param': 0},  # f4 00 00 00

    }

    def __init__(self):
        self.pkg = []
        self.code = []
        self.code_foot = []
        self.text = {}
        self.text_content = {}
        self.bsb = ''

    def _clear(self):
        self.pkg = []
        self.code = []
        self.code_foot = []
        self.text = {}
        self.bsb = ''

    def load(self, path, raw):
        self._clear()

        io = HsIO(path)
        io.seek(0)
        h_magic = io.read_string(len(BurikoScript.h_magic) + 1, to_ms=True)
        if h_magic == BurikoScript.h_magic:
            pkg_list_pos = io.tell()
            [pkg_list_len] = io.read_param('<i')
            code_pos = pkg_list_pos + pkg_list_len

            [pkg_count] = io.read_param('<i')
            for i in range(pkg_count):
                pkg_name = io.read_string(pkg_list_len)
                self.pkg.append(pkg_name)

            io.seek(code_pos)

            [_, foot_offset] = io.read_param('<2i')

            foot_pos = code_pos + 4 + foot_offset

            def read_command(code_list):
                [cmd_id] = io.read_param('<i')
                cmd = BurikoScript.command.get(cmd_id)
                if cmd is not None:
                    param = ()
                    p_num = cmd['param']
                    if p_num > 0:
                        param = io.read_param('<%di' % p_num)
                    code = {'cmd_id': cmd_id, 'param': param}
                    code_list.append(code)
                else:
                    code = {'cmd_id': cmd_id, 'param': ()}
                    code_list.append(code)
                    print(path, 'unknown command id', cmd_id, '%#x' % cmd_id, 'position', '%#x' % (io.tell() - 4),(io.tell() - 4))
                    #raise Exception(path, 'unknown command id', cmd_id,'%#x'%cmd_id, 'position','%#x'%(io.tell() - 4))

            while io.tell() < foot_pos:
                read_command(self.code)

            if io.tell() != foot_pos:
                raise Exception(path, 'foot position error.', io.tell(), foot_pos)

            if len(self.code) > 0 and self.code[-1] == {'cmd_id': 27, 'param': (0,)}:
                for _ in range(6):
                    read_command(self.code_foot)

            self.bsb = io.read_string(encoding='shift_jis')

            exists_info = {}

            def load_text(code_list):
                for i in range(len(code_list)):
                    code = code_list[i]
                    if code['cmd_id'] == 3:
                        p0 = code['param'][0]

                        next_cmd_id = code_list[i + 1]['cmd_id']
                        next_2_cmd_id = code_list[i + 2]['cmd_id']

                        character_text = next_cmd_id == 320
                        character_name = next_cmd_id == 3 and next_2_cmd_id == 320
                        character_select = next_cmd_id == 9 and next_2_cmd_id == 2
                        error_message = next_cmd_id == 249 and next_2_cmd_id == 244
                        translate = character_text or character_name or character_select or error_message

                        if self.text.get(p0) is None and self.text_content.get(p0) is None:
                            offset = code_pos + p0
                            io.seek(offset)

                            if raw:
                                encoding = 'shift_jis'
                            elif translate:
                                encoding = 'gbk'
                            else:
                                encoding = 'shift_jis'

                            exists_info[p0] = {'encoding': encoding, 'offset': io.tell()}
                            text = io.read_string(encoding=encoding)
                            if translate:
                                self.text_content[p0] = text
                            else:
                                self.text[p0] = text
                        else:
                            info = exists_info[p0]
                            if not raw and translate:
                                if info['encoding'] == 'shift_jis':
                                    info['encoding'] = 'gbk'
                                    text = io.read_string(encoding=info['encoding'])
                                    if translate:
                                        self.text_content[p0] = text
                                    else:
                                        self.text[p0] = text

            load_text(self.code)
            load_text(self.code_foot)
            io.close()

    def save(self, path, raw):
        io = HsIO(path, 'w')
        io.write_string(BurikoScript.h_magic, 'ascii')
        pkg_list = ''
        for pkg in self.pkg:
            pkg_list += pkg + '\x00'
        io.write_param('<i', 84)
        io.write_param('<i', len(self.pkg))
        io.write_string(pkg_list, 'ascii', length=76)

        io.write_param('<i', 1)
        code_size = self._calc_code_size(self.code)
        io.write_param('<i', 4 + code_size)

        text_data = []

        bsb = self.bsb.encode('shift_jis') + b'\x00'
        foot_size = self._calc_code_size(self.code_foot)
        text_offset = 8 + code_size + foot_size + len(bsb)

        text_data.append(bsb)

        code_all = self.code + self.code_foot
        exists_info = {}

        for i in range(len(code_all)):
            code = code_all[i]
            if code['cmd_id'] == 3:
                p0 = code['param'][0]

                next_cmd_id = code_all[i + 1]['cmd_id']
                next_2_cmd_id = code_all[i + 2]['cmd_id']

                character_text = next_cmd_id == 320
                character_name = next_cmd_id == 3 and next_2_cmd_id == 320
                character_select = next_cmd_id == 9 and next_2_cmd_id == 2
                error_message = next_cmd_id == 249 and next_2_cmd_id == 244
                translate = character_text or character_name or character_select or error_message

                code_text = self.text.get(p0)
                if code_text is None:
                    code_text = self.text_content.get(p0)
                if code_text is None:
                    raise Exception('miss code_text: %s' % p0)

                if exists_info.get(p0) is None:
                    if raw:
                        encoding = 'shift_jis'
                    elif translate:
                        encoding = 'gbk'
                    else:
                        encoding = 'shift_jis'
                    text = code_text.encode(encoding, errors='ignore') + b'\x00'
                    exists_info[p0] = {'index': len(text_data), 'encoding': encoding, 'offset': None}
                    text_data.append(text)
                else:
                    if not raw and (character_text or character_name or character_select):
                        info = exists_info[p0]
                        if info['encoding'] == 'shift_jis':
                            info['encoding'] = 'gbk'
                            text = code_text.encode(info['encoding'], errors='ignore') + b'\x00'
                            text_data[info['index']] = text

        for i in range(len(code_all)):
            code = code_all[i]
            io.write_param('<i', code['cmd_id'])
            if code['cmd_id'] == 3:
                p0 = code['param'][0]
                info = exists_info[p0]
                if info['offset'] is None:
                    info['offset'] = text_offset
                    io.write_param('<i', info['offset'])

                    index = exists_info.get(p0)['index']
                    text_offset += len(text_data[index])
                else:
                    io.write_param('<i', info['offset'])

            else:
                num_param = len(code['param'])
                if num_param > 0:
                    io.write_param('<%di' % num_param, *code['param'])

        for data in text_data:
            io.write(data)

        io.close()

    @staticmethod
    def _calc_code_size(target):
        size = 0
        for code in target:
            if (code['cmd_id'] in BurikoScript.command.keys()) == False:
                size += 4
            else:
                size += 4 + BurikoScript.command[code['cmd_id']]['param'] * 4
        return size

    def save_json(self, path):
        io = open(path, 'w', encoding='utf8')
        data = {
            'pkg': self.pkg,
            'code': self.code,
            'code_foot': self.code_foot,
            'bsb': self.bsb,
            'text': self.text,
            'text_content': self.text_content,
        }
        json_dump(data, io, ensure_ascii=False, indent=4)
        io.close()

    def load_json(self, path):
        io = open(path, 'r', encoding='utf8')
        data = json_load(io)
        self.pkg = data['pkg']
        self.code = data['code']
        self.code_foot = data['code_foot']
        self.bsb = data['bsb']
        self.text = {}
        for key, value in data['text'].items():
            self.text[int(key)] = value

        self.text_content = {}
        for key, value in data['text_content'].items():
            self.text_content[int(key)] = value
        io.close()
