import pymysql
import hashlib
import datetime



# 注册
def Register(user_name, user_password, telephone):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    md5 = hashlib.md5()
    md5.update(user_password.encode('utf-8'))
    md5Password = md5.hexdigest()  # 把输入的密码变成MD5与数据库中存的MD5值对照
    flag = 0
    sql = "insert into user values(%s, %s, %s, %s, %s, %s)"
    present_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args = [user_name, md5Password, telephone, "L", present_time, 0]

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

Register("xin", "123456", "15068831024")
