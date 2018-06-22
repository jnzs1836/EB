from flask import Flask, render_template, request, flash
import pymysql
import config

app = Flask(__name__)

app.config.from_object(config)


def get_vcode(telephone):
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')
    flag = 0
    temp = ''
    sql = "SELECT max(no) FROM vcode where telephone=%s group by telephone"
    args = [telephone, ]
    vno = 0
    cur = dbForOwner.cursor()
    cur.execute(sql, args)
    results = cur.fetchall()
    for row in results:
        vno = row[0]
    sql = "select code from vcode where no=%s"
    args = [vno, ]
    try:
        cur.execute(sql, args)
        results = cur.fetchall()
        for row in results:
            temp = row[0]
            flag = 1
    except Exception as e:
        flag = 0
    finally:
        dbForOwner.close()
        if flag:
            return temp
        else:
            return flag


@app.route('/', methods=['POST', 'GET'])
def mobile():
    if request.method == 'POST':
        telephone = request.form['telephone']
        code = get_vcode(telephone)
        if code == 0:
            t = '未收到验证码'
            return render_template("mobile.html", value = telephone,msg = t)
        else:
            t = '收到验证码：'+code
            return render_template("mobile.html", value = telephone, msg = t)
    else:
        return render_template("mobile.html")



if __name__ == "__main__":
    # app.run(port=1234)
    # 看情况换端口
    # app.run(host="0.0.0.0") 换成这ip，则校内所有人都可以访问，可用于测试
    app.run(host="0.0.0.0", port=1234)