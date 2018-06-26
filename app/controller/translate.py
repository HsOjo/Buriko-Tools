from json import load, dump

from ..driver.baidu_translate import BaiduTranslate
from ..driver.google_translate import GoogleTranlate


class Translate:
    @staticmethod
    def action(action):
        return {
            'baidu': Translate.baidu,
            'google': Translate.google,
        }.get(action, Translate.help)

    @staticmethod
    def help(param):
        print('''Translate:
        Translate json file! script json only!
        baidu(path_in, path_out, from, to) # japanese: jp, chinese: zh
        google(path_in, path_out, from, to) # japanese: ja, chinese: zh-cn
        ''')

    @staticmethod
    def baidu(param):
        t = BaiduTranslate()
        with open(param[0], 'r', encoding='utf8') as io:
            data = load(io)
            text_content = data['text_content']  # type: dict
            for k, v in text_content.items():
                text_content[k] = t.translate(v, param[2], param[3])
                print(text_content[k])
        with open(param[1], 'w', encoding='utf8') as io:
            dump(data, io, ensure_ascii=False)

    @staticmethod
    def google(param):
        t = GoogleTranlate()
        with open(param[0], 'r', encoding='utf8') as io:
            data = load(io)
            text_content = data['text_content']  # type: dict
            for k, v in text_content.items():
                text_content[k] = t.translate(v, param[2], param[3])
        with open(param[1], 'w', encoding='utf8') as io:
            dump(data, io, ensure_ascii=False)
