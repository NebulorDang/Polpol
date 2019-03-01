#encoding=utf-8#encoding=utf-8
from urllib import request
from bs4 import BeautifulSoup
import pymysql
import requests
from threading import Thread
import threading
import queue
import time


class airlineSpider:
    def __init__(self,dBOption):
        self.url = 'https://data.variflight.com/analytics/codeapi/initialList'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
            'Referer': 'https://data.variflight.com/profiles/Airlines',
            'Cookie': '_ga=GA1.2.1667515674.1551060036; _gid=GA1.2.671705792.1551060036; PHPSESSID=rgel8jke95kcdsmdv1kls5tob6; Hm_lvt_de76267abe273488e66f73620a0a2118=1551167752,1551237761,1551238055,1551238096; Hm_lpvt_de76267abe273488e66f73620a0a2118=1551250796',
            'Host': 'data.variflight.com'
        }
        self.postData = {'style': '2'}
        self.data = {}
        self.dBOption = dBOption

    def download(self):
        r = requests.post(url=self.url, headers=self.header, data=self.postData)
        result = r.json()
        self.data = result['data']

    def craw(self):
        for i in range(26):
            index = chr(65+i)
            ini_ch_data = self.data.get(index)
            for airline in ini_ch_data:
                data_toBase = {}
                data_toBase['id'] = airline['id']
                data_toBase['engName'] = airline['en']
                data_toBase['chName'] = airline['fn']
                data_toBase['ICAO'] = airline['ICAO']
                self.insertData(data_toBase)


    def insertData(self, airlineInfo):
        dBOption = self.dBOption
        dBOption.insertAirportInfo(airlineInfo)

class dBOption:
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql025hqw', db='flightInfo',
                                  charset='utf8')
        print("已连接数据库")

    def createTable(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('drop table if exists airlineInfo')

            sql = '''CREATE TABLE airlineInfo (
                             id varchar (10) not null,
                             engName varchar(50) null,
                             chName varchar (50) null,
                             ICAO varchar (50) null,
                             primary key(id)
                             )CHARACTER SET utf8MB3;'''

            cursor.execute(sql)

            self.db.commit()
            print('已建立数据表')
        except Exception as e:
            print('错误')
            self.db.rollback()

    def insertAirportInfo(self, airlineInfo):
        id = airlineInfo['id']
        engName = airlineInfo['engName']
        chName = airlineInfo['chName']
        ICAO = airlineInfo['ICAO']

        sql = '''insert into airlineInfo(id,engName,chName,ICAO)
                 values ('%s','%s','%s','%s')''' % (id,engName,chName,ICAO)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            print('数据插入成功!')
        except Exception as e:
            self.db.rollback()
            print('数据插入失败!')

    def createTabel_detailInfo(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('drop table if exists airlineDetail')

            sql = '''CREATE TABLE airlineDetail (
                             id varchar (10) not null,
                             country varchar(50) not null,
                             onTimeRate varchar (50) not null,
                             primary key(id)
                             )CHARACTER SET utf8MB3;'''
            cursor.execute(sql)
            self.db.commit()
            print('已建立数据表')
        except Exception as e:
            print('错误')
            self.db.rollback()

    def insertAirlineDetail(self,airlineDetail):
        id = airlineDetail['id']
        country = airlineDetail['country']
        onTimeRate = airlineDetail['onTimeRate']

        sql = '''insert into airlineDetail(id,country,onTimeRate)
                         values ('%s','%s','%s')''' % (id, country, onTimeRate)
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            print('数据插入成功!')
        except Exception as e:
            self.db.rollback()
            print('数据插入失败!')

    def queryAllData(self):

        sql = 'select * from airlineInfo'

        try:
            curor = self.db.cursor()
            curor.execute(sql)
            result = curor.fetchall()
            return result

        except Exception as e:
            print('数据查询失败!')

    def closeDatabase(self):
        db = self.db
        db.close()

class detailInfoSpider:
    def __init__(self, airlineCode):
        self.airlineCode = airlineCode

    def downLoadHtml(self,airlineCode):
        self.url = 'https://data.variflight.com/profiles/Airlines/' + airlineCode
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
        }
        req = request.Request(url=self.url, headers=self.header)
        response = request.urlopen(req)
        self.html_cont = response.read()
        return self.parsePage(airlineCode)

    def parsePage(self,airlineCode):
        soup = BeautifulSoup(self.html_cont, 'html.parser', from_encoding='GBK')
        detailInfo = soup.find('ul', class_='summary-detail').find_all('span')
        country = detailInfo[1].get_text()
        onTimeRate = detailInfo[3].get_text()
        return {'airlineCode':airlineCode,
                'country':country,
                'onTimeRate':onTimeRate}

    def craw(self,msg):
            detailInfo = self.downLoadHtml(self.airlineCode)
            print(msg + str(detailInfo))
            InfotoSave = detailInfo['airlineCode'] + ' ' + \
                         detailInfo['country'] + ' ' + \
                         detailInfo['onTimeRate'] + '\n'

            with open('../data/airlineDetail的副本.txt', 'a') as f:
                f.write(InfotoSave)

class threadPool:
    def __init__(self, threadNum, airlineCodeList):
        self.threadNum = threadNum
        self.airlineCodeList = airlineCodeList
        self.queue = queue.Queue()
        self.index = threadNum

    def createThreadPool(self):
        for i in range(self.threadNum):
            t = Thread(target=self.todoJob)
            t.daemon = True
            t.start()

        time.sleep(2)

        self.addTaskToQueue()


    def todoJob(self):
        while True:
            detailInfoSpider = self.queue.get()
            msg = str(self.index) + ' ' +str(threading.current_thread())
            detailInfoSpider.craw(msg)
            self.queue.task_done()
            self.index = self.index + 1

    def addTaskToQueue(self):
        q = self.queue
        for airlineCode in self.airlineCodeList:
            detailSpider = detailInfoSpider(airlineCode)
            q.put(detailSpider)
        q.join()


if __name__ == '__main__':

    option = input('请选择:\nA[爬取航空公司信息]\nB[爬取详细信息]\nC[存入详细信息]\n')
    if(option == 'A'):
        dBOption = dBOption()
        dBOption.createTable()
        airlineSpider = airlineSpider(dBOption)
        airlineSpider.download()
        airlineSpider.craw()
        dBOption.closeDatabase()

    if(option == 'B'):
        dBOption = dBOption()
        results = dBOption.queryAllData()
        airlineCodeList = []
        for result in results:
            airlineCodeList.append(result[0])

        threadPool = threadPool(10,airlineCodeList)
        threadPool.createThreadPool()
        dBOption.closeDatabase()

    if(option == 'C'):
        dBOption = dBOption()
        dBOption.createTabel_detailInfo()
        with open('../data/airlineDetail.txt', 'r') as f:
            lines = f.readlines()
            airlineDetail = {}
            for line in lines:
                dataline = line.split(' ')
                airlineDetail['id'] = dataline[0]
                airlineDetail['country'] = dataline[1]
                airlineDetail['onTimeRate'] = dataline[2]
                dBOption.insertAirlineDetail(airlineDetail)








