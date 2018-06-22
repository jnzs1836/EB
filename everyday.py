import pymysql
import datetime
import time

def waitToTomorrow():
    """Wait to tommorow 00:00 am"""
    tomorrow = datetime.datetime.replace(datetime.datetime.now() + datetime.timedelta(days=1), hour=0, minute=0, second=0)
    delta = tomorrow - datetime.datetime.now()
    time.sleep(delta.seconds)

def update():
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0
    cur = dbForOwner.cursor()
    try:
        sql = "select user_type, day_left, user_name from user"
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            user_type = row[0]
            day_left = row[1]
            user_name = row[2]
            if user_type == "H":
                day_left = day_left - 1  # 这里加法可能会错误
            if day_left == 0:
                user_type = 'L'
            sql = "update user set user_type=%s, day_left=%s where user_name=%s"
            args = [user_type, day_left, user_name]
            cur.execute(sql, args)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

if __name__ == "__main__":
    while True:
        waitToTomorrow()
        update()