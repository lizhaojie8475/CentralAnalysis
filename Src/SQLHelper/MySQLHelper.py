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

    def updateSameobjDiffield(self, fieldList, valueList, tableName, whereField=None, whereValue=None):
        """
        该函数用来更新特定某一个元组的多个字段。所以whereField和whereValue都只有一个唯一取值
        而fieldList和valueList都是列表，且长度必须相同
        """
        if len(fieldList) != len(valueList):
            print("this function is used to update different fields of the same field !")
            print("so the len of fieldList and valueList have to be the same !")
        elif whereValue is None and whereField is None:
            for field, value in zip(fieldList, valueList):
                sql = 'UPDATE %s SET %s = "%s" ' % (tableName, field, value)
                self.cur.execute(sql)
            self.conn.commit()
        else:
            for field, value in zip(fieldList, valueList):
                sql = 'UPDATE %s SET %s = "%s" WHERE %s = "%s" ' % (tableName, field, value, whereField, whereValue)
                self.cur.execute(sql)
            self.conn.commit()

    def updateSamefieldDiffobj(self, field, valueList, tableName, whereField, whereValueList):
        """
        该函数用来更新多个不同元组的同一个字段，所以只能指定一个字段属性，即field属性是一个string
        而valueList和whereValueList的长度必须相同
        """
        if len(valueList) != len(whereValueList):
            print("this function is used to update the same field of different objs !")
            print("so the len of valueList and whereValueList have to be the same !")
        else:
            for whereValue, value in zip(whereValueList, valueList):
                sql = 'UPDATE %s SET %s = "%s" WHERE %s = "%s" ' % (tableName, field, value, whereField, whereValue)
                self.cur.execute(sql)
            self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()