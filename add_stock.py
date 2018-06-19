import pymysql
import datetime
import re
import random
import time

def add_stocks(stocks):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "insert into stock_set values(%s, %s)"
    args_list = []
    for i in stocks:
        args = []
        args.append(i)
        args.append(stocks[i])
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

def add_stocks_previous_price(stocks):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    year = 2018
    month = 5
    day = 1
    date = [year, month, day]

    today = [2018, 6, 19]

    flag = 0
    sql = "insert into previous_stock values(%s, %s, %s, %s, %s, %s, %s)"


    cur = dbForOwner.cursor()

    try:
        n = len(stocks)
        t = 0

        args_list = []
        now_day = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])
        for i in stocks:
            args = []
            args.append(i)
            args.append(stocks[i])
            max_price = random.uniform(5.0, 100.0)
            min_price = max_price - max_price * random.uniform(0, 0.11)
            start_price = max_price
            end_price = max_price
            while start_price > max_price or start_price < min_price:
                start_price = max_price - max_price * random.uniform(0, 0.11)
            while end_price > max_price or end_price < min_price:
                end_price = max_price - max_price * random.uniform(0, 0.11)
            args.append(start_price)
            args.append(end_price)
            args.append(max_price)
            args.append(min_price)
            args.append(now_day)
            args_list.append(args)

        date_increase(date)

        while 1:
            f = False
            if date[0] < today[0]:
                f = True
            elif date[0] == today[0]:
                if date[1] < today[1]:
                    f = True
                elif date[1] == today[1]:
                    if date[2] < today[2]:
                        f = True
                    else:
                        f = False

            if f:
                now_day = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])
                j = 0
                for i in stocks:
                    args = []
                    args.append(i)
                    args.append(stocks[i])
                    max_price = args_list[t+j][3] + args_list[t+j][3] * random.uniform(-0.07, 0.1)
                    min_price = max_price + 1
                    while min_price > max_price or min_price < args_list[t+j][3] * 0.9:
                        min_price = max_price - max_price * random.uniform(0, 0.11)
                    start_price = max_price + 1
                    end_price = max_price + 1
                    while start_price > max_price or start_price < min_price:
                        start_price = max_price - max_price * random.uniform(0, 0.11)
                    while end_price > max_price or end_price < min_price:
                        end_price = max_price - max_price * random.uniform(0, 0.11)
                    args.append(start_price)
                    args.append(end_price)
                    args.append(max_price)
                    args.append(min_price)
                    args.append(now_day)
                    args_list.append(args)
                    j = j + 1

                t = t + n
                date_increase(date)
            else:
                break

        for i in args_list:
            cur.execute(sql, i)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0
        raise e

    finally:
        dbForOwner.close()
        return flag


def date_increase(date):
    month = date[1]
    day = date[2]
    max_day = get_day(date)
    if day < max_day:
        date[2] = date[2] + 1
    else:
        date[2] = 1
        if month < 12:
            date[1] = date[1] + 1
        else:
            date[1] = 1
            date[0] = date[0] + 1

def get_day(date):
    year = date[0]
    month = date[1]
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return 31
    elif month == 2:
        if year % 400 == 0 or (year % 4 == 0 and year % 100 !=0):
            return 29
        else:
            return 28
    else:
        return 30


if __name__ == "__main__":
    stocks = {}  # id: name
    stocks[123] = "s1"
    stocks[456] = "s2"
    stocks[789] = "s3"
    # add_stocks(stocks)
    add_stocks_previous_price(stocks)
