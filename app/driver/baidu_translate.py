from hashlib import md5
from io import StringIO
from json import load
from time import sleep
from traceback import print_exc
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class BaiduTranslate:
    buffer = {}

    appid = ''
    key = ''

    @staticmethod
    def _translate(content, lang_from, lang_to):
        url = 'http://fanyi-api.baidu.com/api/trans/vip/translate'
        salt = 0
        sign = md5((BaiduTranslate.appid + content + str(salt) + BaiduTranslate.key).encode('utf8')).hexdigest()
        param = {
            'q': content,
            'from': lang_from,
            'to': lang_to,
            'appid': BaiduTranslate.appid,
            'salt': salt,
            'sign': sign,
        }

        req = Request(url, urlencode(param).encode())

        while True:
            try:
                res = urlopen(req, timeout=5)
                with StringIO(res.read().decode('utf8')) as io:
                    result = load(io)['trans_result'][0]['dst']
                break
            except Exception as e:
                print(e)
                sleep(3)

        return result

    @staticmethod
    def translate(content, lang_from='auto', lang_to='zh', buffer=True):
        if buffer:
            if BaiduTranslate.buffer.get(lang_from) is not None:
                gt_buf_lf = BaiduTranslate.buffer[lang_from]
                if gt_buf_lf.get(lang_to) is not None:
                    gt_buf_lf_lt = gt_buf_lf[lang_to]
                    res = gt_buf_lf_lt.get(content)
                    if res is not None:
                        return res

        ret = ''
        line = content.replace('\n', ' ')
        while True:
            try:
                if ret != '':
                    ret += '\n'
                ret += BaiduTranslate._translate(line, lang_from, lang_to)
                break
            except:
                print_exc()
                sleep(3)

        if buffer:
            if BaiduTranslate.buffer.get(lang_from) is None:
                BaiduTranslate.buffer[lang_from] = {}
                gt_buf_lf = BaiduTranslate.buffer[lang_from]
                if gt_buf_lf.get(lang_to) is None:
                    gt_buf_lf[lang_to] = {}
                    gt_buf_lf_lt = gt_buf_lf[lang_to]
                    gt_buf_lf_lt[content] = ret

        return ret


if __name__ == '__main__':
    text = '服を赤く染めている。'
    print(BaiduTranslate.translate(text, 'jp'))
    pass
