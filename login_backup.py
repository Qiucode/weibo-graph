"""
Thanks to mrluanma@gmail.com
I found the weibo login script at https://gist.github.com/mrluanma/3621775
Then I made some necessary changes here

Login work flow:

1.get the pubkey, servertime, nonce and rsakv from prelogin address
2.encrypt the passwd using rsa
3.post data and get the retcode (also login address)
"""
import re
import json
import base64
import binascii
import requests

import rsa


wbclient = 'ssologin.js(v1.4.18)'
user_agent = (
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
    'Chrome/20.0.1132.57 Safari/536.11'
)


class WeiboLogin():
    def __init__(self):
        self.session = requests.session()
        self.session.headers['User-Agent'] = user_agent

    @staticmethod
    def encrypt_passwd(passwd, pubkey, servertime, nonce):
        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)
        passwd = rsa.encrypt(message.encode('utf-8'), key)
        return binascii.b2a_hex(passwd)

    def login(self, username, password):
        resp = self.session.get(
            'http://login.sina.com.cn/sso/prelogin.php?'
            'entry=sso&callback=sinaSSOController.preloginCallBack&'
            'su=%s&rsakt=mod&client=%s' %
            (base64.b64encode(username.encode('utf-8')), wbclient)
        )

        pre_login_str = re.match(r'[^{]+({.+?})', resp.text).group(1)
        pre_login = json.loads(pre_login_str)

        data = {
            'entry': 'weibo',
            'gateway': 1,
            'from': '',
            'savestate': 7,
            'userticket': 1,
            'ssosimplelogin': 1,
            'su': base64.b64encode(requests.utils.quote(username).encode('utf-8')),
            'service': 'miniblog',
            'servertime': pre_login['servertime'],
            'nonce': pre_login['nonce'],
            'vsnf': 1,
            'vsnval': '',
            'pwencode': 'rsa2',
            'sp': self.encrypt_passwd(password, pre_login['pubkey'],
                                      pre_login['servertime'], pre_login['nonce']),
            'rsakv': pre_login['rsakv'],
            'encoding': 'UTF-8',
            'prelt': '115',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.si'
                   'naSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        resp = self.session.post(
            'http://login.sina.com.cn/sso/login.php?client=%s' % wbclient,
            data=data
        )

        # print(resp.text)
        login_url = re.search(r'replace\([\"\']([^\'\"]+)[\"\']',
                              resp.text).group(1)
        resp = self.session.get(login_url)
        login_str = resp.text[resp.text.index("{"): resp.text.rindex("}") + 1]
        login_str = json.loads(login_str)
        if (login_str['result'] == True):
            return self.session
        else:
            return False


if __name__ == '__main__':
    a = WeiboLogin()
    session = a.login('cct439@163.com', 'xxx')
    print(session.get('http://weibo.com/u/3973501575').text)