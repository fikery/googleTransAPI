import requests
import execjs
import json
import re
from bs4 import BeautifulSoup


class GgTransAPI:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }

    def getTrans(self, q, flg=0):
        '''
        如果flg为0默认返回拼音和翻译结果
        如果flg为1默认返回拼音
        否则返回翻译结果
        '''
        url = 'http://translate.google.cn/'
        html = requests.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
        info = soup.find_all('script')
        for i in info:
            data = i.get_text()
            if 'TKK' in data:
                content = execjs.get().compile(data)  # 编译js代码
                tkk = content.eval('TKK')  # 获取变量
                result = self.getTK(q, tkk, flg)
                return result
                # print(content.eval('TKK'))

    def getTK(self, q, tkk, flg):
        # os.environ["NODE_PATH"]=os.getcwd()+"/node_modules"#防止调用node时报错模块不存在
        gettranslation = execjs.compile(
            '''
            function b (a, b) {
                for (var d = 0; d < b.length - 2; d += 3) {
                    var c = b.charAt(d + 2),
                        c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),
                        c = "+" == b.charAt(d + 1) ? a >>> c : a << c;
                    a = "+" == b.charAt(d) ? a + c & 4294967295 : a ^ c
                }
                return a
            }

            function tk (a,TKK) {
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
            '''
        )
        tk = gettranslation.call('tk', q, tkk)
        # print('tk码: ',tk)
        result = self.getdata(tk, q, flg)
        return result

    def getdata(self, tk, q, flg):
        sl, tl = 'zh-CN', 'en'
        if not re.match('[\u4e00-\u9fa5]', q[0]):
            sl, tl = tl, sl
        data_url = 'http://translate.google.cn/translate_a/single?client=t&sl=' + sl + '&tl=' + tl + '&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&pc=1&otf=1&ssel=6&tsel=3&kc=0&tk=' + tk + '&q=' + q
        result = {'msg': '', 'pinyin': '', 'trans': ''}
        try:
            html = requests.get(data_url, headers=self.headers)
            res = json.loads(html.text)[0]
            if sl is 'zh-CN':
                pinyin = res[-1][3]
            else:
                pinyin = res[-1][2]
            trans = [x[0] for x in res if x[0]]
            trans = ''.join(trans)
            if flg == 0:
                result.update({'msg': 'success', 'pinyin': pinyin, 'trans': trans})
            elif flg == 1:
                result.update({'msg': 'success', 'pinyin': pinyin, 'trans': ''})
            else:
                result.update({'msg': 'success', 'pinyin': '', 'trans': trans})
        except Exception as e:
            result = {'msg': str(e), 'pinyin': '', 'trans': ''}
        return json.dumps(result, ensure_ascii=False)

    def beginTrans(self):
        try:
            text = input('请输入待翻译文本：')
            if not text == 'Quit':
                self.getTrans(text)
                self.beginTrans()
        except:
            pass


ggtrans = GgTransAPI()

if __name__ == '__main__':
    # ggtrans.beginTrans()
    print(ggtrans.getTrans("apple and book"))
