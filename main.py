from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import DB_Connector as DB
import config
from urllib.parse import urlencode
from pager import Pagination
import random
from pyecharts import Kline, Line, Overlap
from functools import wraps
import json

app = Flask(__name__)

app.config.from_object(config)  # 配置文件

# 设置上传文件存放的目录
# UPLOAD_FOLDER = "./static"  # 预留


# 画图用
REMOTE_HOST = "https://pyecharts.github.io/assets/js"

######

# 输入一个股票id，获得实时价格
def get_stock_price(stock_id):
    pass

######


##################################################################################################################
# 中央交易系统给我们提供的函数，我这里随便模拟数据
def get_stock_info(stock_id):
    dic = {"latest_price": "1.11", "buy_highest_price": "2.22", "sale_lowest_price": "3.33"}
    return dic


# 输入股票名字模糊查找
def get_info_name(stock_name):
    # 根据股票名字进行模糊查找，得到最匹配的一个股票的id
    stock_id = ""
    dic = get_info_id(stock_id)
    return dic


# 输入股票id精确查找
def get_info_id(stock_id):
    dic = {}
    tmp = get_stock_info(stock_id)
    dic["latest_price"] = tmp["latest_price"]
    dic["buy_highest_price"] = tmp["buy_highest_price"]
    dic["sale_lowest_price"] = tmp["sale_lowest_price"]
    dic["today_price"] = {"highest_price":"", "lowest_price":""}
    dic["week_price"] = {"highest_price":"", "lowest_price":""}
    dic["month_price"] = {"highest_price":"", "lowest_price":""}
    dic["stock_info"] = ""
    dic["current_price"] = ""
    return dic


# 提供给交易客户端的端口
@app.route('/stock', methods=['POST'])
def send_stock_info():
    if request.method == 'POST':
        data = json.loads(request.get_data())
        stock_id = data["code"]
        stock_name = data["name"]
        return_data = {}
        if stock_id and stock_name == "":
            return_data = get_info_id(stock_id)
        if stock_name and stock_id == "":
            return_data = get_info_name(stock_name)

        return jsonify(return_data)
##################################################################################################################



########


def get_stock_info(stock_id):
    id = ""  # 股票代码
    name = ""  # 股票名称
    present_price = ""  # 当前价格（元）
    price_rise_rate = ""  # 涨幅（%）
    price_rise = ""  # 涨跌（元）
    yesterday_end_price = ""  # 昨日收盘价（元）
    today_start_price = ""  # 今日开盘价（元）
    today_max_price = ""  # 今日最高价（元）
    today_min_price = ""  # 今日最低价（元）

    result = [id, name, present_price, price_rise_rate, price_rise, yesterday_end_price, today_start_price, today_max_price, today_min_price]

    return result



########


# 欢迎
@app.route('/', methods=['GET', 'POST'])  # "/" 说明url为"http://127.0.0.1:5000/"调用这个函数，接受post和get两个请求
def welcome():
    if session.get("username"):
        session.pop("username", None)

    if request.method == 'POST':  # 登录     当为post请求时，即发送表单时
        if DB.Login(request.form['username'], request.form['password']) == 1:  # 列出所有账号密码，再进行查询确定
            session["username"] = request.form['username']
            session.permanent = True
            DB.login_log(request.form['username'], "S")  # 登录成功日志
            return redirect(url_for("home"))
        else:
            DB.login_log(request.form['username'], "F")  # 登录失败日志
            flash("用户名或密码错误", 'err')
            return redirect(url_for('/'))   # 账号密码错误，提示错误信息，再次返回到登录页面，即再次调用login()函数
    else:
        return render_template("welcome.html")    # 除了post请求外，比如随便输入网站进去，返回登录页面


# 登录
@app.route('/login', methods=['GET', 'POST'])  # "/" 说明url为"http://127.0.0.1:5000/"调用这个函数，接受post和get两个请求
def login():
    if session.get("username"):
        session.pop("username", None)

    if request.method == 'POST':  # 登录     当为post请求时，即发送表单时
        if DB.Login(request.form['username'], request.form['password']) == 1:  # 列出所有账号密码，再进行查询确定
            session["username"] = request.form['username']
            session.permanent = True
            DB.login_log(request.form['username'], "S")  # 登录成功日志
            return redirect(url_for("home"))
        else:
            DB.login_log(request.form['username'], "F")  # 登录失败日志
            flash("用户名或密码错误", 'err')
            return redirect(url_for('login'))   # 账号密码错误，提示错误信息，再次返回到登录页面，即再次调用login()函数
    else:
        return render_template("login.html")    # 除了post请求外，比如随便输入网站进去，返回登录页面


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("username"):
        session.pop("username", None)

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
    if session.get("username"):
        session.pop("username", None)

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

    x1 = []
    y1 = []
    day_kline = Kline("大盘日K线图")
    day_kline.add("日K", x1, y1, is_datazoom_show=True, is_toolbox_show=False)

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
                            myechart=day_kline.render_embed(),
                            host=REMOTE_HOST,
                            script_list=day_kline.get_js_dependencies())


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
        # 查询

        infos = []

        pager_obj = Pagination(request.args.get("page", 1), len(infos), request.path, request.args,
                               per_page_count=20)  # 每页显示20个查询结果
        present_results = infos[pager_obj.start:pager_obj.end]  # 现在要显示的结果
        html = pager_obj.page_html()
        get_dict = request.args.to_dict()
        path = urlencode(get_dict)  # 转化成urlencode格式的
        get_dict["_list_filter"] = path

        if user_type == "H":
            x1 = []
            y1 = []
            day_kline = Kline("日K线图")
            day_kline.add("日K", x1, y1, is_datazoom_show=True, is_toolbox_show=False)

            x2 = []
            y2 = []
            month_kline = Kline("月K线图")
            month_kline.add("月K", x2, y2, is_datazoom_show=True, is_toolbox_show=False)

            x3 = []
            y3 = []
            year_kline = Kline("月K线图")
            year_kline.add("年K", x3, y3, is_datazoom_show=True, is_toolbox_show=False)

            x_pma_5 = []
            y_pma_5 = []
            pma_5 = Line()
            pma_5.add("5 PMA", x_pma_5, y_pma_5, is_datazoom_show=True, is_toolbox_show=False)

            x_pma_10 = []
            y_pma_10 = []
            pma_10 = Line()
            pma_10.add("10 PMA", x_pma_10, y_pma_10, is_datazoom_show=True, is_toolbox_show=False)

            x_pma_30 = []
            y_pma_30 = []
            pma_30 = Line()
            pma_30.add("30 PMA", x_pma_30, y_pma_30, is_datazoom_show=True, is_toolbox_show=False)

            # 集成了日k线，5日均线，10日均线，30均线
            overlap = Overlap()
            overlap.add(day_kline)
            overlap.add(pma_5)
            overlap.add(pma_10)
            overlap.add(pma_30)


            # kline.add("日K", ["2018/5/{}".format(i + 1) for i in range(20)], a, is_datazoom_show=True, is_toolbox_show=False)


            return render_template("query.html",
                                   host=REMOTE_HOST,
                                   myechart1=overlap.render_embed(),
                                   script_list1=overlap.get_js_dependencies(),
                                   myechart2=month_kline.render_embed(),
                                   script_list2=month_kline.get_js_dependencies(),
                                   myechart3=year_kline.render_embed(),
                                   script_list3=year_kline.get_js_dependencies(),
                                   presentResults=present_results,
                                   html=html,
                                   flag=1)
        else:
            return render_template("query.html",
                                   presentResults=present_results,
                                   html=html,
                                   flag=0)

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
    # app.run(host="0.0.0.0") 换成这ip，则校内所有人都可以访问，可用于测试
    app.run()
