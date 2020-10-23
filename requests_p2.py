import requests
from configs import *
from datetime import datetime
from tpsf_package.tools.db import PyODBCHandler
from tpsf_package.tools.db.configs import SMZB_DB_CONFIG, AISPORTS_DB_CONFIG, OUTSOURCE_DB_CONFIG

class Aisports(object):
    token = None
    username = None
    password = None
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.getToken()

    def timestampToDatetime(self, timestamp_):
        timestamp = int(str(timestamp_)[:10])
        dt = datetime.fromtimestamp(timestamp)
        dt = f'{dt.year}-{dt.month}-{dt.day} {dt.hour}:{dt.minute}:{dt.second}'
        return dt

    def getToken(self):
        
        headers = {
            "Host": "cn2.pc.aisports.io",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "terType": "1",
            "lang" : "zh-cn",
            "Content-Length": "129",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://cn2.pc.aisports.io",
            "Referer": "http://cn2.pc.aisports.io/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        postUrl = "http://cn2.pc.aisports.io/ai/login"
        postData = {
                "userId": "0b6e845fefdbe3434d47ba789e6e548b",
                "merchantId": "038f3e1d118e41c9a248f045701a37b4",
                "loginName": self.username,
                "passWord": self.password
            }
        try:
            res = requests.post(postUrl, json=postData, headers=headers)
            res.raise_for_status() # 如果狀態非200就拋異常
            self.token = res.json()["data"]
        except Excpetion as e:
            print(e)
    
    def getBetRecords(self, beginTime=None, endTime=None, orderState=""):
        ret = []
        if beginTime and endTime:
            beginTime = beginTime + " 00:00:00"
            endTime = endTime + " 23:59:59"
            beginTime_datetime = datetime.strptime(beginTime, "%Y-%m-%d %H:%M:%S")
            endTime_datetime = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
            beginTime = round(datetime.timestamp(beginTime_datetime)*1000)
            endTime = round(datetime.timestamp(endTime_datetime)*1000)
        elif not beginTime or not endTime:
            beginTime = None
            endTime = None

        if not self.token:
            return "token is None, should use getToken first"

        headers = {
            'Host': 'cn2.pc.aisports.io',
            'Connection' : 'keep-alive',
            'Content-Length': "90",
            'Accept': 'application/json, text/plain, */*',
            'terType': '1',
            'lang': 'zh-cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
            'token': self.token,
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'http://cn2.pc.aisports.io',
            'Referer': 'http://cn2.pc.aisports.io/usercenter/BetRecords',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        postUrl = "http://cn2.pc.aisports.io/ai/order/betRecordTab"
        postData = {"beginTime": beginTime, "endTime": endTime, "page": 1, "pageSize": 20, "orderState": orderState}
        try:
            res = requests.post(postUrl, json=postData, headers=headers)
            res.raise_for_status() # 如果狀態非200就拋異常
            data = res.json()

            # ret = data["data"]["pageDTOList"][0]["orderDTOList"]
            # get specificed data only
            for d in data["data"]["pageDTOList"]: # 訂單列表
                _ = {}
                _["orderId"] = d["orderDTOList"][0]["orderId"]
                _["orderTime"] = d["orderTime"]
                _["orderDateTime"]= self.timestampToDatetime(d["orderTime"])
                _["gameType"]= d["orderDTOList"][0]["gameType"]
                _["resultScore"]= d["orderDTOList"][0]["betDTOList"][0]["resultScore"]
                _["homeTeam"]= d["orderDTOList"][0]["betDTOList"][0]["homeTeam"]
                _["awayTerm"]= d["orderDTOList"][0]["betDTOList"][0]["awayTeam"]
                _["leagueName"]= d["orderDTOList"][0]["betDTOList"][0]["leagueName"]
                _["gameDate"]= d["orderDTOList"][0]["betDTOList"][0]["gameDate"]
                _["gameDateTime"]= self.timestampToDatetime(d["orderDTOList"][0]["betDTOList"][0]["gameDate"])
                _["betItem"]= d["orderDTOList"][0]["betDTOList"][0]["betItem"]
                _["betResultDetail"]= d["orderDTOList"][0]["betDTOList"][0]["betResultDetail"]
                _["ioRatio"]= d["orderDTOList"][0]["betDTOList"][0]["ioRatio"]
                _["winAndLossGold"]= d["orderDTOList"][0]["winAndLossGold"]
                _["gold"]= d["orderDTOList"][0]["gold"]
                ret.append(_)
            return ret
            
        except Exception as e:
            print(e)



aisport = Aisports(username=USERNAME, password=PASSWORD)



db = PyODBCHandler(host=AISPORTS_DB_CONFIG["HOST"],
                   db=AISPORTS_DB_CONFIG["DB"],
                   uid=AISPORTS_DB_CONFIG["UID"],
                   pwd=AISPORTS_DB_CONFIG["PWD"])

db.insert(tablename="BetRecords", list_=aisport.getBetRecords())
db.close()




