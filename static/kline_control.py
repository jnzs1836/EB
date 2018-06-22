import pymysql
import datetime

td = datetime.datetime.now()
p1 = td + datetime.timedelta(days=-1)
p2 = td + datetime.timedelta(days=-2)
p3 = td + datetime.timedelta(days=-3)
p4 = td + datetime.timedelta(days=-4)
p5 = td + datetime.timedelta(days=-5)

def get_stock_info():
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "select * from stock_set"

    cur = dbForOwner.cursor()
    results = []

    try:
        cur.execute(sql)
        results = cur.fetchall()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return results

def get_end_price(stock_info):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "select end_price, date from previous_stock where stock_id=%s"
    args = [stock_info[0], ]
    cur = dbForOwner.cursor()
    results = []

    try:
        dic = {}
        cur.execute(sql, args)
        results = cur.fetchall()
        for i in range(len(results)):
            dic[results[i][1].strftime("%Y-%m-%d")] = results[i][0]

        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return dic



def cal_pma(pma, stock_info):
    dic = get_end_price(stock_info)
    td = datetime.datetime.now()
    argsList = []
    date = datetime.datetime.strptime("2018-01-02", "%Y-%m-%d")
    date = date + datetime.timedelta(days=+(pma+1))
    last = date.strftime(("%Y-%m-%d"))
    while True:
        if td.strftime("%Y-%m-%d") == last:
            break
        sum = 0
        for i in range(pma):
            d = (td + datetime.timedelta(days=-(i+1))).strftime("%Y-%m-%d")
            sum = sum + float(dic[d])
        avg = sum / 5
        argsList.append([stock_info[0], td.strftime("%Y-%m-%d"), avg])
        td = td + datetime.timedelta(days=-1)

    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    if pma == 5:
        sql = "insert into pma5 values(%s, %s, %s)"
    elif pma == 10:
        sql = "insert into pma10 values(%s, %s, %s)"
    elif pma == 30:
        sql = "insert into pma30 values(%s, %s, %s)"

    cur = dbForOwner.cursor()
    results = []

    try:
        for i in argsList:
            cur.execute(sql, i)
        dbForOwner.commit()

        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag



if __name__ == "__main__":
    info = get_stock_info()
    for i in info:
        cal_pma(5, i)
        cal_pma(10, i)
        cal_pma(30, i)

