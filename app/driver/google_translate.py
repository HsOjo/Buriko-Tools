import re
import ssl
from http.cookiejar import CookieJar
from io import StringIO
from json import load
from time import sleep
from traceback import print_exc
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, Request

from execjs import eval as js_eval


class GoogleTranlate:
    buffer = {}

    @staticmethod
    def _translate(content, lang_from, lang_to):
        ssl._create_default_https_context = ssl._create_unverified_context
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        opener = build_opener(HTTPCookieProcessor(CookieJar()))

        reg = re.compile("TKK=eval\('\(\((.*)\)\)'\)")

        req = Request('https://translate.google.cn/', headers=header)
        resp = opener.open(req)
        res = resp.read().decode('unicode_escape')

        [js] = reg.findall(res)

        tkk = js_eval(js)
        tk = js_eval('''
        function (a,TKK) {
var b = function (a, b) {

  for (var d = 0; d < b.length - 2; d += 3) {

    var c = b.charAt(d + 2),

      c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),

      c = "+" == b.charAt(d + 1) ? a >>> c : a << c;

    a = "+" == b.charAt(d) ? a + c & 4294967295 : a ^ c

  }

  return a

}
  for (var e = TKK.split("."), h = Number(e[0]) || 0, g = [], d = 0, f = 0; f < a.length; f++) {

    var c = a.charCodeAt(f);

    128 > c ? g[d++] = c : (2048 > c ? g[d++] = c >> 6 | 192 : (55296 == (c & 64512) && f + 1 < a.length && 56320 == (a.charCodeAt(f + 1) & 64512) ? (c = 65536 + ((c & 1023) << 10) + (a.charCodeAt(++f) & 1023), g[d++] = c >> 18 | 240, g[d++] = c >> 12 & 63 | 128) : g[d++] = c >> 12 | 224, g[d++] = c >> 6 & 63 | 128), g[d++] = c & 63 | 128)

  }

  a = h;

  for (d = 0; d < g.length; d++) a += g[d], a = b(a, "+-a^+6");

  a = b(a, "+-3^+b+-f");

  a ^= Number(e[1]) || 0;

  0 > a && (a = (a & 2147483647) + 2147483648);

  a %= 1E6;

  return a.toString() + "." + (a ^ h)

} 
''' + '("%s","%s")' % (content.replace('\n', '\\n'), tkk))

        param = {
            'sl': lang_from,
            'tl': lang_to,
            'hl': lang_to,
            'q': content,
            'tk': tk,
        }
        req = Request(
            'https://translate.google.cn/translate_a/single?client=t&dt=bd&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8' + urlencode(
                param), headers=header)
        resp = opener.open(req, timeout=10)
        with StringIO(resp.read().decode('utf8')) as io:
            result = load(io)[0][0][0]

        return result

    @staticmethod
    def translate(content, lang_from, lang_to='zh-cn', buffer=True):
        if buffer:
            if GoogleTranlate.buffer.get(lang_from) is not None:
                gt_buf_lf = GoogleTranlate.buffer[lang_from]
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
                ret += GoogleTranlate._translate(line, lang_from, lang_to)
                break
            except:
                print_exc()
                sleep(3)

        if buffer:
            if GoogleTranlate.buffer.get(lang_from) is None:
                GoogleTranlate.buffer[lang_from] = {}
                gt_buf_lf = GoogleTranlate.buffer[lang_from]
                if gt_buf_lf.get(lang_to) is None:
                    gt_buf_lf[lang_to] = {}
                    gt_buf_lf_lt = gt_buf_lf[lang_to]
                    gt_buf_lf_lt[content] = ret

        return ret


if __name__ == '__main__':
    print(GoogleTranlate.translate('服を赤く染めている。', 'ja', 'zh-cn'))
    print(GoogleTranlate.translate('かんぱーい！', 'ja', 'zh-cn'))
