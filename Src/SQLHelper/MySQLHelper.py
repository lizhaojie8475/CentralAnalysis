import pymysql

class MySqlHelper():

    def __init__(self, host="localhost", user="root", passwd="li712139", db="Network"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    def connect(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset="utf8")
        self.cur = self.conn.cursor()

    def search(self, sql):
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def insert(self, sql, *args):
        self.conn.ping(reconnect=True)
        self.cur.execute(sql, args)
        self.conn.commit()

    def insertMany(self, args):
        """
        批量插入
        :param tableName:
        :param params:      要批量插入到的属性列
        :param args:        批量插入的记录组成的list，记录的类型是list
        :return:            批量插入的条数
        """
        if len(args) == 0:
            return
            # sql = "INSERT INTO segment_data(id, content, type, role) VALUES(%s, %s, %s, %s)"
            # MySql.insert(sql, item[0], res, item[2], item[3])
        sql = "INSERT INTO segment_data(id, content, type, role) VALUES(%s, %s, %s, %s)"
        self.cur.executemany(sql, args)
        self.conn.commit()

    def update(self, fieldList, valueList, tableName, whereField, whereValue):
        if len(fieldList) != len(valueList):
            print("the number of field and value must be the same !")
        else:
            for field, value in zip(fieldList, valueList):
                sql = 'UPDATE %s SET %s = "%s" WHERE %s = "%s" ' % (tableName, field, value, whereField, whereValue)
                self.cur.execute(sql)
            self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()