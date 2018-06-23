import pymysql
import datetime
import re
import random
import time

def stock_change(info):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "insert into today_stock values(%s, %s, %s, %s)"
    present_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args_list = []
    for i in range(len(info)):
        args = []
        args.append(info[i][0])
        args.append(info[i][1])
        yesterday_price = float(info[i][3])
        today_price = yesterday_price + yesterday_price * random.uniform(-0.1, 0.1)
        while today_price < 4.0:
            print("here")
            today_price = yesterday_price + yesterday_price * random.uniform(0, 0.1)
        args.append(today_price)
        args.append(present_time)
        args_list.append(args)


    cur = dbForOwner.cursor()

    try:
        for i in args_list:
            cur.execute(sql, i)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

def get_yesterdat_info():
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    today = datetime.datetime.now()
    yesterday = today + datetime.timedelta(days=-1)
    sql = "select * from previous_stock where date=%s"
    args = [yesterday.strftime("%Y-%m-%d"),]

    cur = dbForOwner.cursor()
    results = []

    try:
        cur.execute(sql, args)
        results = cur.fetchall()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return results


if __name__ == "__main__":
    stock_info_yesterday = get_yesterdat_info()
    while True:
        time.sleep(1)
        stock_change(stock_info_yesterday)
