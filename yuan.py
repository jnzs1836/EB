import pymysql
import hashlib
import datetime
import random

# 登录
def Login(user_name, user_password):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    md5 = hashlib.md5()
    md5.update(user_password.encode('utf-8'))
    md5Password = md5.hexdigest()   # 把输入的密码变成MD5与数据库中存的MD5值对照
    flag = 0
    sql = "select user_name, user_password from user"

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            if user_name == row[0] and md5Password == row[1]:
                flag = 1
                break

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

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

#判断用户名与手机号是否一致
def check_username_telephone(username, telephone):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0;
    sql = "select user_name, telephone from user"

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            if username == row[0] and telephone == row[1]:
                flag = 1
                break

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

#判断用户名密码与手机号是否一致
def check_user(username,password, telephone):
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    md5Password = md5.hexdigest()
    flag = 0;
    sql = "select user_password, telephone from user where user_name=%s"
    args = [username, ]

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql, args)
        results = cur.fetchall()
        for row in results:
            if md5Password == row[0] and telephone == row[1]:
                flag = 1
                break
    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

#验证用户名是否存在
def isExisted(username):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0;
    sql = "select user_name from user"
    cur = dbForOwner.cursor()

    try:
        cur.execute(sql)
        results = cur.fetchall()
        for row in results:
            if username == row[0]:
                flag = 1
                break

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

def addVcode(tel):
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0;
    temp = ''
    for i in range(6):
        rad = random.randrange(0, 10)
        temp = temp + str(rad)
    sql = "insert into vcode (`telephone`, `code`) values(%s, %s)"
    args=[tel, temp]
    cur = dbForOwner.cursor()

    try:
        cur.execute(sql, args)
        dbForOwner.commit()

    except Exception as e:
        flag = 0

    sql = "SELECT LAST_INSERT_ID()"
    cur.execute(sql)
    results = cur.fetchall()
    for row in results:
        flag = row[0]

    dbForOwner.close()
    return flag


# 验证码
def Verificate(code, no):
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0;
    sql = "select code from vcode where no=%s"
    args = [no, ]
    cur = dbForOwner.cursor()
    try:
        cur.execute(sql, args)
        results = cur.fetchall()
        for row in results:
            if code == row[0]:
                flag = 1
                break

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag


# 修改密码
def Modify(user_name, user_password):
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
    sql = "update user set user_password=%s where user_name=%s"
    args = [md5Password, user_name]

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

# 续费升级
def Renew(user_name, duration):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0
    cur = dbForOwner.cursor()
    user_type = ''
    start_time = ''
    day_left = 0
    try:
        sql = "select user_type, start_time, day_left from user where user_name=%s"
        args = [user_name, ]
        cur.execute(sql, args)
        results = cur.fetchall()
        for row in results:
            user_type = row[0]
            start_time = row[1]
            day_left = row[2]
            if user_type == "H":
                day_left = day_left + duration * 30  # 这里加法可能会错误
            else:
                user_type = "H"
                start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                day_left = duration * 30

        sql = "update user set user_type=%s, start_time=%s, day_left=%s where user_name=%s"
        args = [user_type, start_time, day_left, user_name]
        cur.execute(sql, args)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

def get_type(user_name):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0
    sql = "select type from user where user_name=%s"
    args = [user_name, ]

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql, args)
        results = cur.fetchall()
        user_type = results[0]
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        if flag:
            return user_type
        else:
            return flag

# 主页显示所有股票价格
def query_all():
    pass

# 查询某一股票的价格,name为ID或者名字,option选择名字还是ID
def query(name, option):
    pass

def login_log(user_name, state): # 输入用户名以及登录状态
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0
    present_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = "insert into login_log values(%s, %s, %s)"
    args = [user_name, present_time, state]

    cur = dbForOwner.cursor()

    try:
        cur.execute(sql, args) # 写入数据库
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag
