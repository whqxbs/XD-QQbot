import bs4
import requests
#from PIL import Image
import re
import getpass
import json
from aip import AipOcr
import os

APP_ID = '14419630'
API_KEY = '03Aj2f0NvSRmkOakF69IG5O3'
SECRET_KEY = 'ILmaXFu10ZxekO6B4CWeozfcu21w9Q8M'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

r = requests.session()

BASE_URL = "https://zfw.xidian.edu.cn"

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0",
    "Accept": "text/html,application/xhtml+xml,application/xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate"
}


def get_info(ses):
    info_url = BASE_URL + '/home'
    ip_list = []
    stu = ""
    name = ""
    used = ""
    rest = ""
    charged = ""
    end = ""
    stu = re.search(r'姓名</label>(.*?)</li>',ses.get(info_url).text).group(1)
    #print(name)
    filt = re.compile(r'>(.*)<')
    soup = bs4.BeautifulSoup(ses.get(info_url).text, 'lxml')
    tr_list = soup.find_all('tr')
    for tr in tr_list:
        td_list = bs4.BeautifulSoup(str(tr), 'lxml').find_all('td')
        #print(len(td_list))
        if len(td_list) == 0:
            continue
        elif len(td_list) == 4:
            ip = filt.search(str(td_list[0])).group(1)
            online_time = filt.search(str(td_list[1])).group(1)
            used_t = filt.search(str(td_list[2])).group(1)
            if used_t == '':
                continue
            ip_list.append((ip, online_time, used_t))
        elif len(td_list) == 5:
            name = filt.search(str(td_list[0])).group(1)
            used = filt.search(str(td_list[1])).group(1)
            rest = filt.search(str(td_list[2])).group(1)
            charged = filt.search(str(td_list[3])).group(1)
            end = filt.search(str(td_list[4])).group(1)
    return ip_list, name, used, rest, charged, end, stu

#print("欢迎使用校园网流量查询！")
#print("请输入学号:")
#username=input()
#password=getpass.getpass(r"请输入密码(密码不会显示):")

if os.path.exists('llresult.txt'):
    os.remove('llresult.txt')
with open("u1er.txt", "r") as f1:
    username = f1.readline()
    #print(data)
    f1.close()
with open("p@ssw0rd.txt", "r") as f2:
    password = f2.readline()
    #print(data)
    f2.close()

soup = bs4.BeautifulSoup(r.get(BASE_URL).text, "lxml")
csrf = soup.find('input', type='hidden').get('value')
#print(csrf)

img_url = BASE_URL + \
            soup.find('img', id='loginform-verifycode-image').get('src')
#print(img_url)
image = r.get(img_url,headers=HEADER)
with open('captcha.jpg', 'wb') as f:
    f.write(image.content)
    f.close()
    
imagesa = get_file_content('captcha.jpg')
mid = client.basicGeneral(imagesa)
vcode=mid['words_result'][0]["words"]
    
#try:
    #im = Image.open('captcha.jpg')
    #im.show()
    #im.close()
#except:
    #print("请到文件目录下手动查看并输入验证码。")
#vcode=input("请输入验证码：")

result = r.post(BASE_URL + '/login', data={
                "LoginForm[username]": username,
                "LoginForm[password]": password,
                "LoginForm[verifyCode]": vcode,
                "_csrf": csrf,
                "login-button": ""
            }).text
            
fo = open("llresult.txt", "w")
fo.seek(0, 2)

if len(result)<12000:
    error = re.findall(
            r'请修复以下错误<\/p><ul><li>(.*?)<',
            result
        )[0]
    while error == '验证码不正确。':
        result = r.post(BASE_URL + '/login', data={
                        "LoginForm[username]": username,
                        "LoginForm[password]": password,
                        "LoginForm[verifyCode]": vcode,
                        "_csrf": csrf,
                        "login-button": ""
                    }).text    
    else:
        #print(error)
        line = fo.write(str(error))
        fo.close()
        exit()

fo = open("llresult.txt", "w")
fo.seek(0, 2)

r.headers = HEADER
ip_list, name, used, rest, charged, end, stu= get_info(r)
for ip_info in ip_list:
    #print(ip_info)
    line = fo.write(str(ip_info))
line = fo.write(str("%s同学你好 , 你的套餐名称为 %s , 此月已使用流量 %s , 充值剩余流量(累计) %s , 结算日期 %s , 套餐到期时间 %s" % (stu, name, used, rest, charged, end)))
fo.close()
if os.path.exists('u1er.txt'):
    os.remove('u1er.txt')

if os.path.exists('p@ssw0rd.txt'):
    os.remove('p@ssw0rd.txt')
