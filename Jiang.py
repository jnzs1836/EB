import pymysql
import datetime
from db_config import *

def ftof2(f):
    f = int(f * 100)
    f = f / 100
    return f

# 主页显示所有股票价格
def query_all():

    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )


    cur = db.cursor()

    sql = "select stock_id from stock_set"
    cur.execute(sql)
    results = cur.fetchall()
    fres = []

    for i in results:
        now = qid(i[0])
        fadd = [now["id"], now["name"], now["present_price"], now["rise_rate"], now["rise"], now["end_price"], now["start_price"], now["day_h_price"], now["day_l_price"]]
        fres.append(fadd)
    
    return fres

# 查询某一股票的价格,name为ID或者名字,option选择名字还是ID
# option: 0->ID 1->名字
def query(name, option):

    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )


    cur = db.cursor()

    if option == 0:
        now = qid(name)
        fres = []
        if now["state"] == "true":
            fres = [now["id"], now["name"], now["present_price"], now["rise_rate"], now["rise"], now["end_price"], now["start_price"], now["day_h_price"], now["day_l_price"]]
        return fres
    else:
        fres = []

        sql = "select stock_id from stock_set where stock_name like %s"
        args = ['%'+name+'%']
        cur.execute(sql, args)
        results = cur.fetchall()
        if results:
            for i in results:
                now = qid(i[0])
                fadd = [now["id"], now["name"], now["present_price"], now["rise_rate"], now["rise"], now["end_price"], now["start_price"], now["day_h_price"], now["day_l_price"]]
                fres.append(fadd)
        if not fres:
            fres.append([])
        return fres


# 用名称换id(精确)
def changename(name):
    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )
    cur = db.cursor()
    sql = "select stock_id from stock_set where stock_name like %s"
    args = ['%' + name + '%']
    cur.execute(sql, args)
    results = cur.fetchall()
    if results:
        return results[0][0]
    else:
        return ""
    

#用id获取全部信息
def qid(name):

    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )
    cur = db.cursor()

    fres = {"state": "false", "id": name}
    td = datetime.datetime.now()
    yd = td + datetime.timedelta(days = -1)
    wd = td + datetime.timedelta(days = -td.weekday())
    md = datetime.datetime(yd.year, yd.month, 1)
    tdate = td.strftime("%Y-%m-%d")
    ydate = yd.strftime("%Y-%m-%d")
    wdate = wd.strftime("%Y-%m-%d")
    mdate = md.strftime("%Y-%m-%d")

    sql = "select stock_name from stock_set where stock_id = %s"
    args = [name]
    cur.execute(sql, args)
    results = cur.fetchall()
    if results:
        fres["state"] = "true"
        fres["name"] = results[0][0]
    else:
        return fres

    sql = "select price from today_stock where stock_id = %s and date = (select min(date) from today_stock where stock_id = %s)"
    args = [name, name]
    cur.execute(sql, args)
    results = cur.fetchall()
    fres["start_price"] = ftof2(float(results[0][0]))

    sql = "select end_price from previous_stock where stock_id = %s and date >= %s and date < %s"
    args = [name, ydate, tdate]
    cur.execute(sql, args)
    results = cur.fetchall()
    fres["end_price"] = ftof2(float(results[0][0]))
    
    sql = "select price from today_stock where stock_id = %s and date = (select max(date) from today_stock where stock_id = %s)"
    args = [name, name]
    cur.execute(sql, args)
    results = cur.fetchall()
    fres["present_price"] = ftof2(float(results[0][0]))
    fres["rise"] = ftof2(fres["present_price"] - fres["end_price"])
    fres["rise_rate"] = round(fres["rise"] / fres["end_price"] * 100, 2)

    sql = "select max(price),min(price) from today_stock where stock_id = %s"
    args = [name]
    cur.execute(sql, args)
    results = cur.fetchall()
    fres["day_h_price"] = ftof2(float(results[0][0]))
    fres["day_l_price"] = ftof2(float(results[0][1]))

    sql = "select max(max_price),min(min_price) from previous_stock where stock_id = %s and date >= %s and date < %s"
    args = [name, wdate, tdate]
    cur.execute(sql, args)
    results = cur.fetchall()
    fres["week_h_price"] = ftof2(float(results[0][0])) if float(results[0][0]) > fres["day_h_price"] else fres["day_h_price"]
    fres["week_l_price"] = ftof2(float(results[0][1])) if float(results[0][1]) < fres["day_l_price"] else fres["day_l_price"]

    sql = "select max(max_price),min(min_price) from previous_stock where stock_id = %s and date >= %s and date < %s"
    args = [name, mdate, tdate]
    cur.execute(sql, args)
    results = cur.fetchall()
    fres["month_h_price"] = ftof2(float(results[0][0])) if float(results[0][0]) > fres["day_h_price"] else fres["day_h_price"]
    fres["month_l_price"] = ftof2(float(results[0][1])) if float(results[0][1]) < fres["day_l_price"] else fres["day_l_price"]

    sql = "select stock_notice from notice where stock_id = %s"
    args = [name]
    cur.execute(sql, args)
    results = cur.fetchall()
    if results:
        fres["notice"] = results[0][0]
    else:
        fres["notice"] = ""

    return fres

#开盘 收盘 最低 最高
def dayk(id):

    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )

    #print("----1")
    cur = db.cursor()
    
    sql = "select min(date) from previous_stock where stock_id = %s"
    pars = [id]
    cur.execute(sql,pars)
    results = cur.fetchall()
    endd = results[0][0]

    #print("----2")

    sql = "select date from today_stock where stock_id = %s"
    pars = [id]
    cur.execute(sql, pars)
    results = cur.fetchall()
    stad = datetime.datetime(results[0][0].year, results[0][0].month, results[0][0].day)

    #print("-----3")

    fres = []
    nd = stad + datetime.timedelta(days = -1)
    cnt = 0
    while nd >= endd and cnt < 90:
        sql = "select start_price,end_price,min_price,max_price from previous_stock where stock_id = %s and date = %s"
        pars = [id, nd.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd = [nd.strftime("%Y-%m-%d"), ftof2(float(results[0][0])), ftof2(float(results[0][1])), ftof2(float(results[0][2])), ftof2(float(results[0][3]))]
        fres.append(fadd)
        nd += datetime.timedelta(days = -1)
        cnt += 1

    fres.reverse()
    return fres

def monthk(id):

    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )


    cur = db.cursor()
    
    sql = "select min(date) from previous_stock where stock_id = %s"
    pars = [id]
    cur.execute(sql,pars)
    results = cur.fetchall()
    endd = results[0][0]

    sql = "select date from today_stock where stock_id = %s"
    pars = [id]
    cur.execute(sql, pars)
    results = cur.fetchall()
    stad = datetime.datetime(results[0][0].year, results[0][0].month, results[0][0].day)

    fres = []
    nd = datetime.datetime(stad.year, stad.month, 1)
    cnt = 0
    while nd >= endd and cnt < 90:
        d2 = nd + datetime.timedelta(days = -1)
        d1 = datetime.datetime(d2.year, d2.month, 1)

        fadd = [d1.strftime("%Y-%m")]

        sql = "select start_price from previous_stock where stock_id = %s and date = %s"
        pars = [id, d1.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))

        sql = "select end_price from previous_stock where stock_id = %s and date = %s"
        pars = [id, d2.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))

        sql = "select min(min_price) from previous_stock where stock_id = %s and date >= %s and date <= %s"
        pars = [id, d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))

        sql = "select max(max_price) from previous_stock where stock_id = %s and date >= %s and date <= %s"
        pars = [id, d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))
        
        fres.append(fadd)
        nd = d1
        cnt += 1

    fres.reverse()
    #print(fres)
    return fres

def yeark(id):

    db = pymysql.connect(
        user=db_user,
        password=db_secret,
        db="EB",
        host="localhost",
        charset='utf8mb4'
    )


    cur = db.cursor()
    
    sql = "select min(date) from previous_stock where stock_id = %s"
    pars = [id]
    cur.execute(sql,pars)
    results = cur.fetchall()
    endd = results[0][0]

    sql = "select date from today_stock where stock_id = %s"
    pars = [id]
    cur.execute(sql, pars)
    results = cur.fetchall()
    stad = datetime.datetime(results[0][0].year, results[0][0].month, results[0][0].day)

    fres = []
    nd = datetime.datetime(stad.year, 1, 1)
    cnt = 0
    while nd >= endd and cnt < 90:
        d2 = nd + datetime.timedelta(days = -1)
        d1 = datetime.datetime(d2.year, 1, 1)

        fadd = [d1.strftime("%Y")]

        sql = "select start_price from previous_stock where stock_id = %s and date = %s"
        pars = [id, d1.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))

        sql = "select end_price from previous_stock where stock_id = %s and date = %s"
        pars = [id, d2.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))

        sql = "select min(min_price) from previous_stock where stock_id = %s and date >= %s and date <= %s"
        pars = [id, d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))

        sql = "select max(max_price) from previous_stock where stock_id = %s and date >= %s and date <= %s"
        pars = [id, d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")]
        cur.execute(sql, pars)
        results = cur.fetchall()
        if not results:
            break
        fadd.append(ftof2(float(results[0][0])))
        
        fres.append(fadd)
        nd = d1
        cnt += 1

    fres.reverse()
    #print(fres)
    return fres