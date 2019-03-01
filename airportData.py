#encoding=utf-8
import pymysql
class dbOption:
    def __init__(self):
        self.db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql025hqw', db='flightInfo',
                                  charset='utf8')
        print("已连接数据库")

    def createTable(self):
        try:
            cursor = self.db.cursor()
            cursor.execute('drop table if exists airportInfo')

            sql = '''CREATE TABLE airportInfo (
                             abbreviation varchar (10) not null,
                             airportName text not null,
                             primary key(abbreviation)
                             )CHARACTER SET utf8MB3;'''

            cursor.execute(sql)

            self.db.commit()
            print('已建立数据表')
        except Exception as e:
            print('错误')
            self.db.rollback()

    def insertAirportInfo(self, airportInfo):
        abbreviation = airportInfo['abbreviation']
        airportName = airportInfo['airportName']

        sql = '''insert into airportInfo(abbreviation,airportName)
                 values ('%s','%s')''' % (abbreviation,airportName)

        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            print('数据插入成功!')
        except Exception as e:
            self.db.rollback()
            print('数据插入失败!')

class AirportInfo:
    def __init__(self,dataPath):
        self.dataPath = dataPath

    def parseData(self):
        with open(self.dataPath, 'r') as f:
            lines = f.readlines()
            airportInfos = []
            for line in lines:
                formLine = line.replace('\t', '').replace('\n', '')
                airportInfo = {}
                airportInfo['abbreviation'] = formLine[0:3]
                airportInfo['airportName'] = formLine[3:]
                airportInfos.append(airportInfo)
            return airportInfos

if __name__ == '__main__':
    airportInfos = AirportInfo('../data/airport2.txt').parseData()
    print(airportInfos)
    dbOption = dbOption()
    dbOption.createTable()
    for airportInfo in airportInfos:
        dbOption.insertAirportInfo(airportInfo)