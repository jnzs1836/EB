import pymysql
import hashlib

def Login(user_name, user_password):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="library",
                                 host="localhost",
                                 charset='utf8mb4')
    md5 = hashlib.md5()
    md5.update(user_password.encode('utf-8'))
    md5Password = md5.hexdigest()   # 把输入的密码变成MD5与数据库中存的MD5值对照
    flag = 0
    sql = "select admin_id, password from administrator"

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            if user_name == row[0] and md5Password == row[1]:
                flag = 1
                break

    except Exception as e:
        raise e

    finally:
        dbForOwner.close()
        if flag == 1:
            return 1
        else:
            return 0