import requests
import re
from datetime import datetime, timedelta
import json
import getpass
# coding:utf-8
import xlwt
import os
#os.environ['NO_PROXY'] = 'http://ids.xidian.edu.cn/authserver/login'
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
if os.path.exists('kbresult.txt'):
    os.remove('kbresult.txt')
with open("u1er.txt", "r") as f1:
    username = f1.readline()
    #print(data)
    f1.close()
with open("p@ssw0rd.txt", "r") as f2:
    password = f2.readline()
    #print(data)
    f2.close()

#print("欢迎使用课表查询!")
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
    
#################课表#########################

semesterCode = ses.post(
        'http://ehall.xidian.edu.cn/jwapp/sys/wdkb/modules/jshkcb/dqxnxq.do',
        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
    ).json()['datas']['dqxnxq']['rows'][0]['DM']

termStartDay = datetime.strptime(ses.post(
    'http://ehall.xidian.edu.cn/jwapp/sys/wdkb/modules/jshkcb/cxjcs.do',
    headers={
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    },
    data={
        'XN': semesterCode.split('-')[0] + '-' + semesterCode.split('-')[1],
        'XQ': semesterCode.split('-')[2]
    }
).json()['datas']['cxjcs']['rows'][0]["XQKSRQ"].split(' ')[0], '%Y-%m-%d')

qResult = ses.post(
    'http://ehall.xidian.edu.cn/jwapp/sys/wdkb/modules/xskcb/xskcb.do',
    headers={  # 学生课程表
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }, data={
        'XNXQDM': semesterCode
    }
).json()

qResult = qResult['datas']['xskcb']

#print(qResult)
rows = qResult['rows']
kebiao = xlwt.Workbook (encoding= 'utf-8') #创建表格
alignment = xlwt.Alignment()
alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT #换行
alignment.horz = 0x02      # 设置水平居中
alignment.vert = 0x01      # 设置垂直居中
style = xlwt.XFStyle() # Create the Style
style.alignment = alignment
class_list = kebiao.add_sheet('课程列表',cell_overwrite_ok=True)#创建列表标签
class_list.write(0, 0,  '课程名称',style)
class_list.write(0, 1,  '课程号',style)
class_list.write(0, 2,  '课序号',style)
class_list.write(0, 3,  '开课单位',style)
class_list.write(0, 4,  '上课周次',style)
class_list.write(0, 5,  '上课星期',style)
class_list.write(0, 6,  '开始节次',style)
class_list.write(0, 7,  '结束节次',style)
class_list.write(0, 8,  '教师',style)
class_list.write(0, 9,  '教室',style)
i = 1
for  dict in rows :
    class_list.write(i, 0,  dict['KCM'],style)
    class_list.write(i, 1,  dict['KCH'],style)
    class_list.write(i, 2,  dict['KXH'],style)
    class_list.write(i, 3,  dict['KKDWDM_DISPLAY'],style)
    class_list.write(i, 4,  dict['ZCMC'],style)
    class_list.write(i, 5,  dict['SKXQ'],style)
    class_list.write(i, 6,  dict['KSJC'],style)
    class_list.write(i, 7,  dict['JSJC'],style)
    class_list.write(i, 8,  dict['SKJS'],style)
    class_list.write(i, 9,  dict['JASMC'],style)
    i = i+1
#课程列表填写完成

class_all = kebiao.add_sheet('总课表',cell_overwrite_ok=True)#创建总课表
class_all.write(0, 1,  '周一',style)
class_all.write(0, 2,  '周二',style)
class_all.write(0, 3,  '周三',style)
class_all.write(0, 4,  '周四',style)
class_all.write(0, 5,  '周五',style)
class_all.write(0, 6,  '周六',style)
class_all.write(0, 7,  '周日',style)
class_all.write(1, 0,  '1',style)
class_all.write(2, 0,  '2',style)
class_all.write(3, 0,  '3',style)
class_all.write(4, 0,  '4',style)
class_all.write(5, 0,  '晚',style)
for dict in rows :
    x = (int(dict['KSJC'])+1)/2
    y = int(dict['SKXQ'])
    str_1 = str (dict['KCM'])
    str_2 = str (dict['ZCMC'])
    str_3 = str (dict['SKJS'])
    str_4 = str (dict['JASMC'])
    class_all.write(x, y, str_1+str_2 +str_3 +str_4 ,style)

#总课表填写完成

week1 = kebiao.add_sheet('第1周',cell_overwrite_ok=True)
week2 = kebiao.add_sheet('第2周',cell_overwrite_ok=True)
week3 = kebiao.add_sheet('第3周',cell_overwrite_ok=True)
week4 = kebiao.add_sheet('第4周',cell_overwrite_ok=True)
week5 = kebiao.add_sheet('第5周',cell_overwrite_ok=True)
week6 = kebiao.add_sheet('第6周',cell_overwrite_ok=True)
week7 = kebiao.add_sheet('第7周',cell_overwrite_ok=True)
week8 = kebiao.add_sheet('第8周',cell_overwrite_ok=True)
week9 = kebiao.add_sheet('第9周',cell_overwrite_ok=True)
week10 = kebiao.add_sheet('第10周',cell_overwrite_ok=True)
week11 = kebiao.add_sheet('第11周',cell_overwrite_ok=True)
week12 = kebiao.add_sheet('第12周',cell_overwrite_ok=True)
week13 = kebiao.add_sheet('第13周',cell_overwrite_ok=True)
week14 = kebiao.add_sheet('第14周',cell_overwrite_ok=True)
week15 = kebiao.add_sheet('第15周',cell_overwrite_ok=True)
week16 = kebiao.add_sheet('第16周',cell_overwrite_ok=True)
week17 = kebiao.add_sheet('第17周',cell_overwrite_ok=True)
week_list = [week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13, week14, week15, week16, week17]
for week in week_list :
    week.write(0, 1, '周一',style)
    week.write(0, 2,  '周二',style)
    week.write(0, 3,  '周三',style)
    week.write(0, 4,  '周四',style)
    week.write(0, 5,  '周五',style)
    week.write(0, 6,  '周六',style)
    week.write(0, 7,  '周日',style)
    week.write(1, 0,  '1',style)
    week.write(2, 0,  '2',style)
    week.write(3, 0,  '3',style)
    week.write(4, 0,  '4',style)
    week.write(5, 0,  '晚',style)
i = 0
for week in week_list :
    for dict in rows :
        if int(dict['SKZC'][i])==1 :
            x = (int(dict['KSJC'])+1) / 2
            y = int(dict['SKXQ'])
            str_5 = str (dict['KCM'])+'\n'
            str_6 = str (dict['SKJS'])+'\n'
            str_7 = str (dict['JASMC'])+'\n'
            week.write(x, y,  str_5+str_6+str_7,style)
    i = i+1
#每周课表填写完成

kebiao.save("C:\\phpStudy\\PHPTutorial\\WWW\\" + username + '.xls')
kbresult = open("kbresult.txt","w")
kbresult.write(str("下载地址：http://192.14.168.241/"+username+".xls"))
kbresult.close()

#保存

if os.path.exists('u1er.txt'):
    os.remove('u1er.txt')

if os.path.exists('p@ssw0rd.txt'):
    os.remove('p@ssw0rd.txt')

