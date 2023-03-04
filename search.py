# encoding=utf-8
import requests
import re
import time
import json
import sys
import datetime

def getLogin():
    url = "https://account.ccnu.edu.cn/cas/login?service=http://kjyy.ccnu.edu.cn/loginmall.aspx"
    try:
        res = requests.get(url, timeout=3)
        context = res.text
        lt = re.findall('type="hidden" name="lt" value="(.*?)"', context)[0]
        execution = re.findall('type="hidden" name="execution" value="(.*?)"', context)[0]
        service_url = re.findall('<form id="fm1" action="(.*?)" method="post">', context)[0]
        return lt, execution, service_url
    except Exception as e:
        print(e)  # log
        return '', '', ''


def login(session, username, password):
    lt, execution, service_url = getLogin()
    if lt == '' or execution == '' or service_url == '':
        return 0
    url = f"https://account.ccnu.edu.cn{service_url}"
    try:
        session_id = re.findall(";jsessionid=(.*?)\?", url)[0]
        cookies = {"JSESSIONID": session_id}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"}
        data = {"username": username, "password": password,
                "lt": lt, "execution": execution, "_eventId": "submit", "submit": "\xe7\x99\xbb\xe5\xbd\x95"}
        res = session.post(url=url, headers=headers, cookies=cookies, data=data, timeout=3)
        if f"acc.id = \"{username}\";" in res.text:
            print("[+] Login Success!")
            return 1
        else:
            print("[!] Login Failed!")
            return 0
    except Exception as e:
        print(e)
        return 0


def getAllSeat(session,name):
    roomid = ["100455820","100455822", "100455824", "100455826","101699191", "101699189", "101699187", "101699179"]
    # roomid = ["101699191", "101699189", "101699187", "101699179"] # 南湖
    times = []
    now1 = datetime.datetime.now() + datetime.timedelta(days=1)
    date_time = now1.strftime("%Y-%m-%d")
    times.append(date_time)
    times.append(date_time)
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d")    
    times.append(date_time)
    for id in roomid:
        for d in times:
            print(d)
            baseUrl = f"http://kjyy.ccnu.edu.cn/ClientWeb/pro/ajax/device.aspx?byType=devcls&classkind=8&display=fp&md=d&room_id={id}&purpose=&selectOpenAty=&cld_name=default&date={d}&fr_start=20%3A30&fr_end=21%3A30&act=get_rsv_sta&_=1677504580917 "
            res = session.get(baseUrl)
            data =json.loads(res.text)
            seats = data["data"]
            if seats == None:
                continue
            for seat in seats:
                if len(seat["ts"]) == 0:
                    continue
                owner = seat["ts"][0]["owner"]
                if owner == name or name in owner:
                    print(d,seat["name"],seat["title"],seat["ts"][0]["owner"]) 
            time.sleep(0.2)
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("python3 search.py <uname> <passwd> name")
    else:
        username = sys.argv[1]
        password = sys.argv[2]        
        name = sys.argv[3]
        session = requests.session()
        ok = login(session, username, password)
        if ok:
            res = getAllSeat(session, name)
        else:
            print("login failed!\nusage:python3 search.py <uname> <passwd> name")