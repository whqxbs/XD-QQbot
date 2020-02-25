import requests
import typing
import hashlib
import time
import random
import getpass
import os

BASE = 'http://202.117.121.7:8080/'

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate"
}

def timestamp():
    return int(time.time() * 1000)

class Session:  # 封装requests.Session
    _ses: requests.Session

    @property
    def headers(self):
        return self._ses.headers

    @headers.setter
    def headers(self, headers):
        self._ses.headers = headers

    def _dump_sign(self, data: typing.Dict):
        l = list(data.keys())
        l.sort()
        s = ''
        for i in l:
            s += i+'='+str(data[i])+'&'
        s = s[:-1]
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def options(self, url):
        return self._ses.options(url, headers={
            'Access-Control-Request-Headers': 'content-type,token',
            'Access-Control-Request-Method': 'POST'
        })

    def post(self, url, data=None, json=None, headers=None, param=None):
        self.options(url)
        if param is not None:
            json = {
                'appKey': "GiITvn",
                'param': param,
                'secure': 0
            }
        if json is not None:
            json['time'] = timestamp()  # 先后顺序
            json['sign'] = self._dump_sign(json)  # 数据签名在生成时间戳之后
            if headers == None:
                headers = {}
            headers = dict(headers, **{
                'Content-Type': 'application/json;charset=UTF-8'
            })
        return self._ses.post(url, json=json, data=data, headers=headers)

    def __init__(self):
        self._ses = requests.session()
        self._ses.headers = HEADER
        self._ses.headers['token'] = ''


def _generate_uuid():
    a = [str(random.random())[2:10] for i in range(2)]
    a = [a[i]+str(timestamp())[-10:] for i in range(2)]
    a = [hex(int(a[i]))[2:10] for i in range(2)]
    return "web"+a[0]+a[1]


def get_login_session(username, password) -> Session:
    ses = Session()
    data = {
        'appKey': "GiITvn",
        'param': "{{\"userName\":\"{}\","
                 "\"password\":\"{}\","
                 "\"schoolId\":190,"
                 "\"uuId\":\"{}\"}}"
                 .format(username, password, _generate_uuid()),
        'secure': 0
    }
    result = ses.post(BASE+'baseCampus/login/login.do', json=data).json()
    if result['isConfirm'] != 1:
        raise Exception('登录失败')  # 请检查用户名与密码
    ses.headers['token'] = result['token'][0]+'_'+result['token'][1]
    return ses

if __name__ == '__main__':
    #print("欢迎使用校园卡余额查询！")
    #print("请输入学号:")
    #username=input()
    #password=getpass.getpass(r"请输入密码(密码不会显示):")
    if os.path.exists('yeresult.txt'):
        os.remove('yeresult.txt')
    with open("u1er.txt", "r") as f1:
        username = f1.readline()
        #print(data)
        f1.close()
    with open("p@ssw0rd.txt", "r") as f2:
        password = f2.readline()
        #print(data)
        f2.close()

    ses = get_login_session(
        username, password)
    result = ses.post(
        BASE + 'infoCampus/playCampus/getAllPurposeCard.do',
        param={}
    ).json()
    
    fo = open("yeresult.txt", "w")
    fo.seek(0, 2)
    line = fo.write(str("一卡通余额: " + str(int(result["allPurposeCardVO"]
                              ["cardGeneralInfo"][0]["value"]) / 100) + " 元"))
    #print("一卡通余额: " + str(int(result["allPurposeCardVO"]
                              #["cardGeneralInfo"][0]["value"]) / 100) + " 元")
    fo.close()
    if os.path.exists('u1er.txt'):
        os.remove('u1er.txt')

    if os.path.exists('p@ssw0rd.txt'):
        os.remove('p@ssw0rd.txt')