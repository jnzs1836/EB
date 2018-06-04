from flask import Flask, render_template, request, redirect, url_for, flash, session
import DB_Connector as DB
import config
from urllib.parse import urlencode
from pager import Pagination
import random
from pyecharts import Kline
from functools import wraps

app = Flask(__name__)

app.config.from_object(config)  # 配置文件

# 设置上传文件存放的目录
# UPLOAD_FOLDER = "./static"  # 预留


# 画图用
REMOTE_HOST = "https://pyecharts.github.io/assets/js"


# 登录
@app.route('/', methods=['GET', 'POST'])  # "/" 说明url为"http://127.0.0.1:5000/"调用这个函数，接受post和get两个请求
def login():
    session.clear()
    if request.method == 'POST':  # 登录     当为post请求时，即发送表单时
        if DB.Login(request.form['username'], request.form['password']) == 1:  # 列出所有账号密码，再进行查询确定
            session["username"] = request.form['username']
            session.permanent = True
            DB.login_log(request.form['username'], "S")
            return redirect(url_for("home"))
        else:
            DB.login_log(request.form['username'], "F")
            flash("用户名或密码错误！！", 'err')
            return redirect(url_for('login'))   # 账号密码错误，提示错误信息，再次返回到登录页面，即再次调用login()函数
    else:
        return render_template("login.html")    # 除了post请求外，比如随便输入网站进去，返回登录页面


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()  # 清除session
    if request.method == 'POST':  # 注册
        if DB.Register(request.form['username'], request.form['password1'], request.form['telephone']) == 1:
            return redirect(url_for('login'))
        else:
            flash("wrong！！", 'err')
            return redirect(url_for('register'))
    else:
        return render_template("register.html")


# 密码找回
@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    session.clear()
    if request.method == 'POST':  # 密码找回
        if DB.Modify(request.form['username'], request.form['password1'])==1:
            return redirect(url_for('login'))
        else:
            flash("wrong！！", 'err')
            return redirect(url_for('retrieve'))
    else:
        return render_template("retrieve.html")


# 登录限制，防止输入url登入
def login_required(func):

    @wraps(func)
    def judge(*args, **kwargs):
        if session.get("username"):
            return func(*args, **kwargs)
        else:
            flash("请先登录！！", 'err')
            return redirect(url_for("login"))

    return judge


# 主页面
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # 预留
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

    # 预留
    # 显示所有股票的代码、名字、价格、涨幅
    # 下面是分页的模板
    # 现在随便模拟写了1，2，3，4保证不报错
    result = DB.query_all()
    result = [1, 2, 3, 4]
    result = list(result)
    pager_obj = Pagination(request.args.get("page", 1), len(result), request.path, request.args,
                           per_page_count=20)  # 每页显示20个查询结果
    present_results = result[pager_obj.start:pager_obj.end]  # 现在要显示的结果
    html = pager_obj.page_html()
    get_dict = request.args.to_dict()
    path = urlencode(get_dict)  # 转化成urlencode格式的
    get_dict["_list_filter"] = path
    return render_template("home.html",
                            presentResults=present_results,
                            html=html,
                            myechart=kline.render_embed(),
                            host=REMOTE_HOST,
                            script_list=kline.get_js_dependencies())


# 修改密码
@app.route('/modify', methods=['GET', 'POST'])
@login_required
def modify():
    username = session.get("username")
    if request.method == 'POST':  # 修改密码
        # 判断验证码的逻辑未加
        if DB.Modify(username, request.form['password2']) == 1:
            return redirect(url_for('login'))
        else:
            flash("wrong!!", 'err')
            return redirect(url_for('modify'))
    else:
        return render_template("modify.html")


# 账号升级或续费
@app.route('/renew', methods=['GET', 'POST'])
@login_required
def renew():
    username = session.get("username")
    if request.method == 'POST':  # 账号升级
        duration = request.form['select']
        if duration == "1个月":
            duration = 1
        elif duration == "3个月":
            duration = 3
        elif duration == "6个月":
            duration = 6
        elif duration == "12个月":
            duration = 12

        if DB.Renew(username, duration) == 1:
            return redirect(url_for('home'))
        else:
            flash("wrong", 'err')
            return redirect(url_for('renew'))
    else:
        return render_template("renew.html")


# 查询
@app.route('/query', methods=['GET', 'POST'])
@login_required
def query():
    username = session.get("username")
    if request.method == 'POST':
        user_type = DB.get_type(username)
        stock = request.form['stock']
        # 判断，预留

        # 预留
        # 显示股票曲线 这里模拟一些数据
        # 根据用户类型显示k线
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

        return render_template("query.html",
                               myechart=kline.render_embed(),
                               host=REMOTE_HOST,
                               script_list=kline.get_js_dependencies())
    else:
        return redirect(url_for('home'))


# 显示用户类型
@app.context_processor
def show_type():
    username = session.get("username")
    if username:
        user_type = DB.get_type(username)
        if user_type == "H":
            user_type = "账户续费"
        else:
            user_type = "账户升级"
        return {"user_type": user_type}
    else:
        return {"user_type": None}


if __name__ == "__main__":
    # app.run(port=1234)
    # 看情况换端口
    app.run()
