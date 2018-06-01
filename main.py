from flask import Flask, render_template, request, redirect, url_for, flash, session
import DB_Connector as DB
import config
from urllib.parse import urlencode
from pager import Pagination
import random
from pyecharts import Kline

app = Flask(__name__)

app.config.from_object(config) # 配置文件

# 设置上传文件存放的目录
UPLOAD_FOLDER = "./static" # 预留

# 存查询结果，为了分页用
r = []

# 画图用
REMOTE_HOST = "https://pyecharts.github.io/assets/js"

# 登录
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':  # 登录
        if DB.Login(request.form['username'], request.form['password'])==1: # 列出所有账号密码，再进行查询确定
            session.clear()
            session["username"] = request.form['username']
            session["password"] = request.form['password']
            session.permanent = True
            return render_template("index.html")
        else:
            flash("用户名或密码错误！！", 'err')
            return redirect(url_for('login'))
    else:   # 把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("login.html")


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':  # 注册
        if DB.Register(request.form['username'], request.form['password1'], request.form['telephone']) == 1:
            return redirect(url_for('login'))
        else:
            flash("wrong！！", 'err')
            return redirect(url_for('register'))
    else:   # 把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("register.html")


# 密码找回
@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    if request.method=='POST':  # 注册
        if DB.Modify(request.form['username'], request.form['password'])==1:
            return redirect(url_for('login'))
        else:
            flash("wrong！！", 'err')
            return redirect(url_for('retrieve'))
    else:   # 把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("retrieve.html")

# 主页面
@app.route('/home', methods=['GET','POST'])
def home():
    global r
    # username = session.get("username")
    # password = session.get("password")
    username = 1
    password = 1
    if username == None or password == None:  # 防止未登入直接进入以及防止账号密码过期还想操作
        flash("The user login has expired!!", 'err')
        return redirect(url_for('login'))
    else:
        # user_type = DB.get_type(username)
        user_type = "H"
        if user_type=="H":
            user_type = "账户续费"
        else:
            user_type = "账户升级"

        # 显示大盘曲线 这里模拟一些数据
        a = []
        for i in range(20):
            b = []
            n = int(random.random() * 100)
            b.append(n)
            b.append(n + int(random.uniform(1.1, 10.1) * 100) / 100.0 - 6)
            b.append(n + int(random.uniform(1.1, 11.2) * 100) / 100.0 - 6)
            b.append(n + int(random.uniform(1.1, 10.5) * 100) / 100.0 - 6)
            a.append(b)
        kline = Kline("K 线图示例")
        kline.add("日K", ["2018/5/{}".format(i + 1) for i in range(20)], a)



        # 显示所有股票的代码、名字、价格、涨幅
        # 下面是分页的模板
        result = DB.query_all()
        result = list(result)
        r = result
        pager_obj = Pagination(request.args.get("page", 1), len(r), request.path, request.args,
                               per_page_count=5)  # 每页显示5个查询结果
        presentResults = r[pager_obj.start:pager_obj.end]  # 现在要显示的结果
        html = pager_obj.page_html()
        get_dict = request.args.to_dict()
        path = urlencode(get_dict)  # 转化成urlencode格式的
        get_dict["_list_filter"] = path
        return render_template("home.html", user_type=user_type, presentResults=presentResults, html=html,
                                myechart=kline.render_embed(),
                                host=REMOTE_HOST,
                                script_list=kline.get_js_dependencies())

# 修改密码
@app.route('/modify', methods=['GET','POST'])
def modify():
    if request.method=='POST':  # 修改密码
        if DB.Modify(request.form['username'], request.form['password2'])==1:
            return redirect(url_for('login'))
        else:
            flash("wrong！！", 'err')
            return redirect(url_for('modify'))
    else:
        return render_template("modify.html")

# 账号升级或续费
@app.route('/renew', methods=['GET','POST'])
def renew():
    if request.method=='POST':  # 账号升级
        if DB.Modify(request.form['username'], request.form['password'])==1:
            return redirect(url_for('login'))
        else:
            flash("用户名或密码错误！！", 'err')
            return redirect(url_for('modify'))
    else:   # 每次回到登录界面把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("modify.html")

# 查询
@app.route('/query', methods=['GET','POST'])
def query():
    if request.method=='POST':  # 注册
        if DB.Modify(request.form['username'], request.form['password'])==1:
            return redirect(url_for('login'))
        else:
            flash("用户名或密码错误！！", 'err')
            return redirect(url_for('modify'))
    else:   # 每次回到登录界面把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("modify.html")



if __name__ == "__main__":
    # app.run(port=1234)
    # 看情况换端口
    app.run()