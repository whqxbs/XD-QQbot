import requests
import re
#from icalendar import Calendar, Event
from datetime import datetime, timedelta
import json
import getpass
import os

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate"
}

REGEX_HIDDEN_TAG = '<input type="hidden" name="(.*)" value="(.*)"'
REGEX_HTML_COMMENT = r'<!--\s*([\s\S]*?)\s*-->'

def get_login_session(target, username, password):
    ses = requests.session()
    ses.headers = HEADER
    page = ses.get(
        'http://ids.xidian.edu.cn/authserver/login',
        params={'service': target}
    ).text
    page = re.sub(REGEX_HTML_COMMENT,'',page)
    params = {i[0]: i[1] for i in re.findall(REGEX_HIDDEN_TAG, page)}
    ses.post(
        'http://ids.xidian.edu.cn/authserver/login',
        params={'service': target},
        data=dict(params,**{
            'username': username,
            'password': password
        })
    )
    return ses

if os.path.exists('cjresult.txt'):
    os.remove('cjresult.txt')
with open("u1er.txt", "r") as f1:
    username = f1.readline()
    #print(data)
    f1.close()
with open("p@ssw0rd.txt", "r") as f2:
    password = f2.readline()
    #print(data)
    f2.close()

#print("欢迎使用成绩查询！")
#print("请输入学号:")
#username=input()
#password=getpass.getpass(r"请输入密码(密码不会显示):")

ses = get_login_session(
    'http://ehall.xidian.edu.cn:80//appShow', username,password)

a = ses.get('http://ehall.xidian.edu.cn//appShow?appId=4770397878132218', headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
})

if(len(a.text)>12000):
    #print("请检查学号和密码正确性。")
    kbresult = open("kbresult.txt","w")
    kbresult.write(str("请检查学号和密码正确性。"))
    kbresult.close()
    exit()

################查成绩##################

ses.get('http://ehall.xidian.edu.cn//appShow?appId=4768574631264620', headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
})

querySetting = [
    {  # 学期
        'name': 'XNXQDM',
        'value': '2017-2018-2,2018-2019-1',
        'linkOpt': 'and',
        'builder': 'm_value_equal'
    }, {  # 是否有效
        'name': 'SFYX',
        'value': '1',
        'linkOpt': 'and',
        'builder': 'm_value_equal'
    }
]
courses = {}

for i in ses.post(
        'http://ehall.xidian.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do',
        data={
            'querySetting=': json.dumps(querySetting),
            '*order': 'KCH,KXH',  # 按课程名，课程号排序
            'pageSize': 1000,  # 有多少整多少.jpg
            'pageNumber': 1
        }
).json()['datas']['xscjcx']['rows']:
    if i['XNXQDM_DISPLAY'] not in courses.keys():
        courses[i['XNXQDM_DISPLAY']] = []
    courses[i['XNXQDM_DISPLAY']].append((i['XSKCM'].strip(), str(i['ZCJ']), str(i['XFJD'])))

fo = open("cjresult.txt", "w")
fo.seek(0, 2)
#line = fo.write( str )

for i in courses.keys():
    #print(i + ':')
    line = fo.write(str(i + ':' + '\n'))
    for j in courses[i]:
        if j[2] == 'None':
            #print('\t' + j[0] + ': ' + j[1])
            line = fo.write(str('\t' + j[0] + ': ' + j[1] + '\n'))
        else:
            #print('\t' + j[0] + ': ' + j[1] + ' (' + j[2] + ')')
            line = fo.write(str('\t' + j[0] + ': ' + j[1] + ' (' + j[2] + ')' + '\n'))

fo.close()

if os.path.exists('u1er.txt'):
    os.remove('u1er.txt')

if os.path.exists('p@ssw0rd.txt'):
    os.remove('p@ssw0rd.txt')
###############################################