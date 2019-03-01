#encoding=utf-8
from urllib import request
from bs4 import BeautifulSoup
import pymysql

class HtmlDownloader:
    def __init__(self,url):
        self.url = url

    def download(self):
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}

        req = request.Request(url=self.url, headers=header)
        response = request.urlopen(req)
        html_cont = response.read()
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='GBK')
        return soup

class CrawData:
    def __init__(self,soup):
        self.soup = soup

    def craw(self):
        data_list = []
        for index, tr in enumerate(self.soup.find(cellpadding="2").find_all('tr')):
            if index % 2 == 1:
                tds = tr.find_all('td')
                data_list.append({'所属城市': tds[0].get_text().strip(),
                                  '三字代码': tds[1].get_text().strip(),
                                  '所属国家': tds[2].get_text().strip(),
                                  '国家代码': tds[3].get_text().strip(),
                                  '四字代码': tds[4].get_text().strip(),
                                  '机场名称': tds[5].get_text().strip(),
                                  '英文名称': tds[6].get_text().strip(),
                                  })
        return data_list

class dBOption:
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql025hqw', db='flightInfo',
                                  charset='utf8')
        print("已连接数据库")

    def createTable(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('drop table if exists airportInfo2')

            sql = '''CREATE TABLE airportInfo2 (
                             abbreviation varchar (10) not null,
                             airportName varchar(30) null,
                             engName varchar (50) null,
                             code4D varchar (20) null,
                             address varchar (20) null,
                             countryCode varchar (20) null,
                             country varchar (20) null,
                             primary key(abbreviation)
                             )CHARACTER SET utf8MB3;'''

            cursor.execute(sql)

            self.db.commit()
            print('已建立数据表')
        except Exception as e:
            print('错误')
            self.db.rollback()

    def insertAirportInfo(self, airportInfo2):
        abbreviation = airportInfo2['abbreviation']
        airportName = airportInfo2['airportName']
        engName = airportInfo2['engName']
        code4D = airportInfo2['code4D']
        address = airportInfo2['address']
        countryCode = airportInfo2['countryCode']
        country = airportInfo2['country']

        sql = '''insert into airportInfo2(abbreviation,airportName,engName,code4D,address,countryCode,country)
                 values ('%s','%s','%s','%s','%s','%s','%s')''' % (abbreviation,airportName,engName,code4D,address,countryCode,country)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            print('数据插入成功!')
        except Exception as e:
            self.db.rollback()
            print('数据插入失败!')


if __name__ == '__main__':

    rootUrl = 'http://www.6qt.net/index.asp?Field=&keyword=&MaxPerPage=50&page='
    dBOption = dBOption()
    dBOption.createTable()

    for i in range(1,69):
        url = rootUrl + str(i)
        htmlDownloader =  HtmlDownloader(url)
        soup = htmlDownloader.download()
        crawData = CrawData(soup)
        data_list = crawData.craw()
        airportInfo2 = {}
        for data in data_list:
            airportInfo2['abbreviation'] = data['三字代码']
            airportInfo2['airportName'] = data['机场名称']
            airportInfo2['engName'] = data['英文名称']
            airportInfo2['code4D'] = data['四字代码']
            airportInfo2['address'] = data['所属城市']
            airportInfo2['countryCode'] = data['国家代码']
            airportInfo2['country'] = data['所属国家']
            print(airportInfo2)
            dBOption.insertAirportInfo(airportInfo2)




