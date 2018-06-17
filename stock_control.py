import pymysql
import datetime
import re


def stock_change():
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "update user set user_password=%s where user_name=%s"
    args = []

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql, args)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

def get_closing_price():
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    # present_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    yesterday = get_yesterday(today)
    sql = "select * from previous_stock where date=%s"
    args = [yesterday,]

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql, args)
        results = cur.fetchall()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

def get_yesterday(today):
    words = re.split("[ -]", today)
    year = int(words[0])
    month = int(words[1])
    day = int(words[2])
    if day > 1:
        day = day + 1
        return str(year) + "-" + str(month) + "-" + str(day)
    else:
        if month > 3 or month == 2:
            month = month - 1
            return str(year) + "-" + str(month) + "-" + str(day)
        elif month == 3:
            month = month - 1
            if year % 400 == 0 or (year % 100 != 0 and year % 4 == 0):
                day = 29
                return str(year) + "-" + str(month) + "-" + str(day)
            else:
                day = 28
                return str(year) + "-" + str(month) + "-" + str(day)
        elif month == 1:
            month = 12
            year = year - 1
            day = 31
            return str(year) + "-" + str(month) + "-" + str(day)




if __name__ == "__main__":

    stock_info_yesterday = get_closing_price()

    pass
