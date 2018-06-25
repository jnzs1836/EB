from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import DB_Connector as DB
# import config
from urllib.parse import urlencode
from pager import Pagination
from pyecharts import Kline, Line, Overlap
from functools import wraps
import json
import kline_control
import Jiang
import yuan
from flask_sqlalchemy import SQLAlchemy
from decimal import *
import os
from datetime import timedelta
from db_config import *
from order_queue.queue import Queue,test_queue
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import datetime
from trading.order import *

app = Flask(__name__)

# app.config.from_object(config)  # 配置文件

# 配置flask配置对象中键：SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://%s:%s@localhost/EB" % (db_user,db_secret)
# 配置flask配置对象中键：SQLALCHEMY_COMMIT_TEARDOWN,设置为True,应用会自动在每次请求结束后提交数据库中变动
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 获取SQLAlchemy实例对象，接下来就可以使用对象调用数据
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=10)
app.debug = True
db = SQLAlchemy(app)

# from manage.manage import *


class User(db.Model):
    __tablename__ = 'admin_user'
    user_id = db.Column(db.String(10), primary_key=True)
    user_password = db.Column(db.String(32))
    super = db.Column(db.Boolean)


class StockState(db.Model):
    __tablename__ = 'stock_state'
    stock_id = db.Column(db.String(10), primary_key=True)
    status = db.Column(db.Boolean)
    gains = db.Column(db.Float(10, 2))
    decline = db.Column(db.Float(10, 2))


class StockInfo(db.Model):
    __tablename__ = 'stock_info'
    stock_id = db.Column(db.String(10), primary_key=True)
    stock_name = db.Column(db.String(32))
    newest_price = db.Column(db.Float(10, 2))
    newest = db.Column(db.Integer)


class UserStock(db.Model):
    __tablename__ = 'user_stock'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(10))
    stock_id = db.Column(db.String(10))


class Buy(db.Model):
    __tablename__ = 'buy'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(10))
    stock_name = db.Column(db.String(32))
    price = db.Column(db.Float(10, 2))
    time = db.Column(db.DateTime)
    share = db.Column(db.Integer)


class Sell(db.Model):
    __tablename__ = 'sell'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.String(10))
    stock_name = db.Column(db.String(32))
    price = db.Column(db.Float(10, 2))
    time = db.Column(db.DateTime)
    share = db.Column(db.Integer)


class Manager:
    def __init__(self, app, db):
        self.app = app
        self.db = db

    def get_token(self, id):
        config = self.app.config
        secret_key = config.setdefault('SECRET_KEY')
        salt = config.setdefault('SECURITY_PASSWORD_SALT')
        serializer = URLSafeTimedSerializer(secret_key)
        token = serializer.dumps(id, salt=salt)
        return token

    def check_token(self, token, max_age=86400):
        if token is None:
            return False
        config = self.app.config
        secret_key = config.setdefault('SECRET_KEY')
        salt = config.setdefault('SECURITY_PASSWORD_SALT')
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            id = serializer.loads(token, salt=salt, max_age=max_age)
        except BadSignature:
            return False
        except SignatureExpired:
            return False
        user = User.query.filter_by(user_id=id).first()
        if user is None:
            return False
        return True

    def parse_token(self, token, max_age=86400):
        config = self.app.config
        secret_key = config.setdefault('SECRET_KEY')
        salt = config.setdefault('SECURITY_PASSWORD_SALT')
        serializer = URLSafeTimedSerializer(secret_key)
        id = serializer.loads(token, salt=salt, max_age=max_age)
        return id

    def check_password(self, user_id, old_password, new_password="12345678", confirm_password="12345678"):
        if new_password != confirm_password:
            return {'result': False, 'msg': 'confirm password fail!', 'code': 1}
        if len(new_password) > 20 or len(new_password) < 6:
            return {'result': False, 'msg': 'new password is too long or too short!', 'code': 2}
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return {'result': False, 'msg': 'user doesn\'t exist', 'code': 3}
        if user.user_password != old_password:
            return {'result': False, 'msg': 'wrong password', 'code': 4}
        return {'result': True, 'msg': 'reset successfully'}

    def reset_password(self, user_id, new_password):
        try:
            user = User.query.filter_by(user_id=user_id).first()
            user.user_password = new_password
            db.session.commit()
        except:
            return False
        return True

    def user_stock_auth(self, user_id, stock_id):
        user_stock = UserStock.query.filter_by(user_id=user_id, stock_id=stock_id).first()
        if user_stock is None:
            return False
        else:
            return True

    # def get_stock_info(stock_id):
    #     stock_info = StockInfo.query.filter_by(stock_id=stock_id).first()
    #     stock_state = get_stock_state(stock_id)
    #     if stock_info is None or stock_state is None:
    #         return {}
    #     dict = {'stock_id': stock_info.stock_id, 'stock_name': stock_info.stock_name,
    #             'newest_price': float(stock_info.newest_price), 'newest': float(stock_info.newest),
    #             'status': stock_state['status'], 'gains': stock_state['gains'], 'decline': stock_state['decline']}
    #     return dict

    # def change_stock_status(stock_id, status):
    #     stock_state = StockState.query.filter_by(stock_id=stock_id).first()
    #     if stock_state is None:
    #         return False
    #     try:
    #         stock_state.status = status
    #         app.db.session.commit()
    #     except:
    #         return False
    #     return True

    # def set_price_limit(stock_id, price, is_gains):
    #     # 这里需要一些对price的检查
    #     stock_state = StockState.query.filter_by(stock_id=stock_id).first()
    #     if stock_state is None:
    #         return False
    #     try:
    #         if is_gains:
    #             stock_state.gains = price
    #         else:
    #             stock_state.decline = price
    #         app.db.session.commit()
    #     except:
    #         return False
    #     return True

    # def get_buy_sell_items(stock_id, is_buy):
    #     try:
    #         if is_buy:
    #             slist = Buy.query.filter_by(stock_id=stock_id).all()
    #         else:
    #             slist = Sell.query.filter_by(stock_id=stock_id).all()
    #         return_list = []
    #         for item in slist:
    #             item_dict = {
    #                 'stock_id': item.stock_id,
    #                 'stock_name': item.stock_name,
    #                 'price': float(item.price),
    #                 'time': str(item.time),
    #                 'share': item.share
    #             }
    #             return_list.append(item_dict)
    #         return return_list
    #     except Exception as e:
    #         print(e)
    #         return []

    def add_authorization(self, user_id, stock_id):
        try:
            user = User.query.filter_by(user_id=user_id).first()
            if user is None:
                return {'code': 0, 'msg': 'user does not exist'}
            stock = StockInfo.query.filter_by(stock_id=stock_id).first()
            if stock is None:
                return {'code': 0, 'msg': 'stock does not exist'}
            user_stock = UserStock.query.filter_by(user_id=user_id, stock_id=stock_id).first()
            if user_stock is not None:
                return {'code': 0, 'msg': 'authorization exist'}
            user_stock = UserStock(user_id=user_id, stock_id=stock_id)
            db.session.add(user_stock)
            db.session.commit()
            return {'code': 1, 'msg': 'success'}
        except Exception as e:
            print(e)
            return {'code': 0, 'msg': "error"}

    def delete_authorization(self, user_id, stock_id):
        try:
            user = User.query.filter_by(user_id=user_id).first()
            if user is None:
                return {'code': 0, 'msg': 'user does not exist'}
            stock = StockInfo.query.filter_by(stock_id=stock_id).first()
            if stock_id is None:
                return {'code': 0, 'msg': 'stock does not exist'}
            user_stock = UserStock.query.filter_by(user_id=user_id, stock_id=stock_id).first()
            if user_stock is None:
                return {'code': 0, 'msg': 'authorization does not exist'}
            db.session.delete(user_stock)
            db.session.commit()
            return {'code': 1, 'msg': 'success'}
        except Exception as e:
            print(e)
            return {'code': 0, 'msg': "error"}


manager = Manager(app, db)

# 画图用
REMOTE_HOST = "https://pyecharts.github.io/assets/js"


####################################################外部操作########################################################

# 输入一个股票id，获得实时价格
def get_stock_price(stock_id):
    tmp = Jiang.qid(stock_id)
    if tmp["state"] == "true":
        return tmp["present_price"]
    else:
        return None

# 中央交易系统给我们提供的函数，我这里随便模拟数据
def get_stock_info(stock_id):
    dic = get_stock_current_state(stock_id)
    return dic


# 输入股票名字模糊查找
def get_info_name(stock_name):
    # 根据股票名字进行模糊查找，得到最匹配的一个股票的id
    stock_id = Jiang.changename(stock_name)
    dic = get_info_id(stock_id)
    return dic


# 输入股票id精确查找
def get_info_id(stock_id):
    dic = {}
    tmp = get_stock_info(stock_id)
    now = Jiang.qid(stock_id)
    ret = {}
    ret["state"] = now["state"]
    if now["state"] == "true":
        dic["latest_price"] = tmp["latest_price"]
        dic["buy_highest_price"] = tmp["buy_highest_price"]
        dic["sale_lowest_price"] = tmp["sale_lowest_price"]

        dic["today_price"] = {"highest_price": now["day_h_price"], "lowest_price": now["day_l_price"]}
        dic["week_price"] = {"highest_price": now["week_h_price"], "lowest_price": now["week_l_price"]}
        dic["month_price"] = {"highest_price": now["month_h_price"], "lowest_price": now["month_l_price"]}
        dic["stock_info"] = now["notice"]
        dic["current_price"] = now["present_price"]
    ret["stock_price"] = dic
    return ret


# 提供给交易客户端的端口
@app.route('/stock', methods=['POST'])
def send_stock_info():
    if request.method == 'POST':
        data = json.loads(request.get_data())

        return_data = {}
        if "code" in data.keys():
            stock_id = data["code"]
            return_data = get_info_id(stock_id)
        if "name" in data.keys():
            stock_name = data["name"]
            return_data = get_info_name(stock_name)
        return jsonify(return_data)
##################################################################################################################


###############################################内部操作############################################################

# 9字段 为主界面以及query界面表格中各属性
def get_stock_info_in(stock_id):
    result = Jiang.query(stock_id, 0)
    return result

# 局部动态更新
@app.route('/AJAXinfo', methods=['POST'])
def AJAXinfo():
    idlist = json.loads(request.form['list'])
    idlist = list(idlist.values())

    result = []
    for i in idlist:
        tmp = Jiang.query(i, 0)
        result.append(tmp)

    #处理成字符串格式
    js = ""
    ifirst = True
    for i in result:
        if ifirst:
            ifirst = False
        else:
            js += ';'

        jfirst = True
        for j in i:
            if jfirst:
                jfirst = False
            else:
                js += ','
            js += str(j)

    return js


# 欢迎界面
@app.route('/', methods=['GET', 'POST'])
def welcome():
    if session.get("info_username"):
        session.pop("info_username", None)

    if request.method == 'POST':  # 登录
        if DB.Login(request.form['username'], request.form['password']) == 1:  # 列出所有账号密码，再进行查询确定
            session["info_username"] = request.form['username']
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("info_username"):
        session.pop("info_username", None)

    if request.method == 'POST':  # 登录
        if DB.Login(request.form['username'], request.form['password']) == 1:  # 列出所有账号密码，再进行查询确定
            session["info_username"] = request.form['username']
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
    if session.get("info_username"):
        session.pop("info_username", None)

    if request.method == 'POST':  # 注册
        if request.form['password1'] != request.form['password2']:
            flash('两次密码输入不一致')
            return redirect(url_for("register"))
        elif yuan.isExisted(request.form['username']) == 1:
            flash('用户名已存在')
            return redirect(url_for("register"))
        else:
            session["r_vno"] = yuan.addVcode(request.form['telephone'])
            session["r_username"] = request.form['username']
            session["r_password"] = request.form['password1']
            session["r_telephone"] = request.form['telephone']
            if session["r_vno"] > 0:
                return redirect(url_for("register_code"))
            else:
                return redirect(url_for("register_code"))
    else:
        return render_template("register.html")


#注册验证码
@app.route('/register/verification', methods=['GET', 'POST'])
def register_code():
    if session.get("r_vno"):
        r_vno = session.get("r_vno")
    else:
        return redirect(url_for('register'))

    username = session.get("r_username")
    password = session.get("r_password")
    telephone = session.get("r_telephone")
    if request.method == 'POST':
        r_vno = request.form['vno']
        code = request.form['verification']
        if yuan.Verificate(code, r_vno) == 1:
            if yuan.Register(username, password, telephone) == 1:
                session.pop("r_username")
                session.pop("r_password")
                session.pop("r_telephone")
                return redirect(url_for('login'))
        else:
            flash('验证码错误')
            time = request.form['_time']
            return render_template("register_code.html", last_url = url_for('register'),vno=r_vno, user_name=username, password=password,telephone=telephone, time=time)
    else:
        if r_vno > 0:
            return render_template("register_code.html", last_url = url_for('register'), vno=r_vno, user_name=username, password=password,telephone=telephone, time=60)
        return render_template("register_code.html", last_url = url_for('register'))


# 密码找回
@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve():
    if session.get("info_username"):
        session.pop("info_username", None)

    if request.method == 'POST':  # 密码找回
        if yuan.check_username_telephone(request.form['username'], request.form['telephone']) == 1:
            session["re_vno"] = yuan.addVcode(request.form['telephone'])
            session["re_username"] = request.form['username']
            session["re_telephone"] = request.form['telephone']
            return redirect(url_for('retrieve_code'))
        else:
            flash('用户名或手机号不正确')
            return redirect(url_for('retrieve'))
    else:
        return render_template("retrieve.html")


#找回密码验证码
@app.route('/retrieve/verification', methods=['GET', 'POST'])
def retrieve_code():
    if session.get("re_vno"):
        re_vno = session.get("re_vno")
    else:
        return redirect(url_for('retrieve'))

    username = session.get("re_username")
    telephone = session.get("re_telephone")
    if request.method == 'POST':
        if request.form['password1']!=request.form['password2']:
            flash('两次密码输入不一致')
            time = request.form['_time']
            return render_template("retrieve_code.html", last_url = url_for('retrieve'), vno=re_vno, user_name=username, telephone=telephone, time = time)
        re_vno = request.form['vno']
        code = request.form['verification']
        password = request.form['password1']
        if yuan.Verificate(code, re_vno) == 1:
            if yuan.Modify(username, password) == 1:
                session.pop("re_username")
                session.pop("re_telephone")
                return redirect(url_for('login'))
        else:
            flash('验证码错误')
            time = request.form['_time']
            return render_template("retrieve_code.html", last_url = url_for('retrieve'), vno=re_vno, user_name=username, telephone=telephone, time=time)
    else:
        if re_vno > 0:
            return render_template("retrieve_code.html", last_url = url_for('retrieve'), vno=re_vno, user_name=username,telephone=telephone, time = 60)
        return render_template("retrieve_code.html")


# 登录限制，防止输入url登入
def login_required(func):

    @wraps(func)
    def judge(*args, **kwargs):
        if session.get("info_username"):
            return func(*args, **kwargs)
        else:
            flash("请先登录！！", 'err')
            return redirect(url_for("login"))

    return judge


# 主页面
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    x1 = []
    y1 = []
    info = Jiang.dayk("123")  # 大盘暂定代码为123
    for i in range(len(info)):
        x1.append(info[i][0])
        y1.append(info[i][1:])
    day_kline = Kline("大盘日K线图")
    day_kline.add("日K", x1, y1, is_datazoom_show=True, is_toolbox_show=False)

    # 显示所有股票的代码、名字、价格、涨幅
    result = Jiang.query_all()
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
    username = session.get("info_username")
    if request.method == 'POST':  # 修改密码
        if yuan.check_user(username, request.form['password1'], request.form['telephone']) == 1:
            session["m_vno"] = yuan.addVcode(request.form['telephone'])
            session["m_username"] = username
            session["m_telephone"] = request.form['telephone']
            return redirect(url_for('modify_code'))
        else:
            flash('密码或手机号不正确')
            return redirect(url_for('modify'))
    else:
        return render_template("modify.html")


#修改密码验证码
@app.route('/modify/verification', methods=['GET', 'POST'])
def modify_code():
    if session.get("m_vno"):
        m_vno = session.get("m_vno")
    else:
        return redirect(url_for('modify'))
    username = session.get("m_username")
    telephone = session.get("m_telephone")
    if request.method == 'POST':
        if request.form['password2'] != request.form['password3']:
            flash('两次密码输入不一致')
            time = request.form['_time']
            return render_template("modify_code.html", vno=m_vno, user_name=username, telephone=telephone, time=time)
        m_vno = request.form['vno']
        code = request.form['verification']
        password = request.form['password2']
        if yuan.Verificate(code, m_vno)==1:
            if yuan.Modify(username, password) == 1:
                return redirect(url_for('home'))
        else:
            flash('验证码错误')
            time = request.form['_time']
            return render_template("modify_code.html", vno=m_vno, user_name=username, telephone=telephone, time=time)
    else:
        if m_vno > 0:
            return render_template("modify_code.html", vno=m_vno, user_name=username, telephone=telephone,time=60)
        return render_template("modify_code.html")


# 账号升级或续费
@app.route('/renew', methods=['GET', 'POST'])
@login_required
def renew():
    username = session.get("info_username")
    if request.method == 'POST':  # 账号升级或续费
        if yuan.check_username_telephone(username, request.form['telephone']) == 1:
            session["ren_vno"] = yuan.addVcode(request.form['telephone'])
            session["ren_username"] = username
            session["ren_telephone"] = request.form['telephone']
            duration = request.form['select']
            if duration == "1个月":
                duration = 1
            elif duration == "3个月":
                duration = 3
            elif duration == "6个月":
                duration = 6
            elif duration == "12个月":
                duration = 12
            session["duration"] = duration
            return redirect(url_for('renew_code'))
        else:
            flash('手机号不正确')
            return redirect(url_for('renew'))
    else:
        return render_template("renew.html")


#账号升级或续费验证码
@app.route('/renew/verification', methods=['GET', 'POST'])
def renew_code():
    if session.get("ren_vno"):
        ren_vno = session.get("ren_vno")
    else:
        return redirect(url_for('renew'))
    username = session.get("ren_username")
    telephone = session.get("ren_telephone")
    duration = session.get("duration")
    if request.method == 'POST':
        ren_vno = request.form['vno']
        code = request.form['verification']
        if yuan.Verificate(code, ren_vno) == 1:
            if yuan.Renew(username, duration) == 1:
                DB.vip_log(username, duration)
                return redirect(url_for('home'))
        else:
            flash('验证码错误')
            time = request.form['_time']
            return render_template("renew_code.html", vno=ren_vno, user_name=username, telephone=telephone,time=time, select=duration)
    else:
        if ren_vno > 0:
            return render_template("renew_code.html", vno=ren_vno, user_name=username, telephone=telephone, time=60, select=duration)
        return render_template("renew_code.html")


@app.route('/agreement', methods=['GET', 'POST'])
def agreement():
    return render_template("agreement.html")

@app.route('/ajax', methods=['GET'])
def ajax():
    if request.args.get("tel"):
        telephone = request.args.get("tel")
        r_vno = yuan.addVcode(telephone)
        return jsonify({"vno": r_vno})
    else:
        return jsonify({"vno": -1})

def ltos(infos):
    s = ""
    for i in range(len(infos)):
        for j in range(9):
            s = s + str(infos[i][j]) + " "
    return s

def stol(s):
    l = s.split()
    n = len(l) / 9
    infos = []
    for i in range(int(n)):
        list = []
        list.append(l[i * 9])
        list.append(l[i * 9 + 1])
        list.append(float(l[i * 9 + 2]))
        list.append(float(l[i * 9 + 3]))
        list.append(float(l[i * 9 + 4]))
        list.append(float(l[i * 9 + 5]))
        list.append(float(l[i * 9 + 6]))
        list.append(float(l[i * 9 + 7]))
        list.append(float(l[i * 9 + 8]))
        infos.append(list)
    return infos

# 查询
@app.route('/query', methods=['GET', 'POST'])
@login_required
def query():
    username = session.get("info_username")
    if request.method == 'POST':
        user_type = DB.get_type(username)
        name = request.form['optionsRadiosinline']

        if name == "stockcode":
            infos = [Jiang.query(request.form['name'], 0)]
        else:
            infos = Jiang.query(request.form['name'], 1)

        if len(infos[0]) == 0:
            flash("无结果", 'err')
            return redirect(url_for('home'))

        stock_id = infos[0][0]
        session["infos"] = ltos(infos)

        page_now = request.args.get("page", 1)
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
            info = Jiang.dayk(infos[0][0])
            
            for i in range(len(info)):
                x1.append(info[i][0])
                y1.append(info[i][1:])
            day_kline = Kline("日K线图")
            day_kline.add("日K", x1, y1, is_datazoom_show=True, is_toolbox_show=False)

            x2 = []
            y2 = []
            info = Jiang.monthk(infos[0][0])
            for i in range(len(info)):
                x2.append(info[i][0])
                y2.append(info[i][1:])
            month_kline = Kline("月K线图")
            month_kline.add("月K", x2, y2, is_datazoom_show=True, is_toolbox_show=False)

            x3 = []
            y3 = []
            info = Jiang.yeark(infos[0][0])
            for i in range(len(info)):
                x3.append(info[i][0])
                y3.append(info[i][1:])
            year_kline = Kline("年K线图")
            year_kline.add("年K", x3, y3, is_datazoom_show=True, is_toolbox_show=False)

            x_pma_5 = kline_control.get_info(5, stock_id)[0]
            y_pma_5 = kline_control.get_info(5, stock_id)[1]
            pma_5 = Line()
            pma_5.add("5 PMA", x_pma_5, y_pma_5, is_datazoom_show=True, is_toolbox_show=False)

            x_pma_10 = kline_control.get_info(10, stock_id)[0]
            y_pma_10 = kline_control.get_info(10, stock_id)[1]
            pma_10 = Line()
            pma_10.add("10 PMA", x_pma_10, y_pma_10, is_datazoom_show=True, is_toolbox_show=False)

            x_pma_30 = kline_control.get_info(30, stock_id)[0]
            y_pma_30 = kline_control.get_info(30, stock_id)[1]
            pma_30 = Line()
            pma_30.add("30 PMA", x_pma_30, y_pma_30, is_datazoom_show=True, is_toolbox_show=False)

            # 集成了日k线，5日均线，10日均线，30均线
            overlap = Overlap()
            overlap.add(day_kline)
            overlap.add(pma_5)
            overlap.add(pma_10)
            overlap.add(pma_30)

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
                                   flag=1,
                                   kid=present_results[0][0],
                                   page_now=page_now)
        else:
            return render_template("query.html",
                                   presentResults=present_results,
                                   html=html,
                                   kid=present_results[0][0],
                                   flag=0,
                                   page_now=page_now)
    else:
        if request.args.get('id', None):
            stock_id = request.args.get('id')
            infos = stol(session.get("infos"))

            page_now = request.args.get("page", 1)
            pager_obj = Pagination(request.args.get("page", 1), len(infos), request.path, request.args,
                                   per_page_count=20)  # 每页显示20个查询结果
            present_results = infos[pager_obj.start:pager_obj.end]  # 现在要显示的结果
            html = pager_obj.page_html()
            get_dict = request.args.to_dict()
            path = urlencode(get_dict)  # 转化成urlencode格式的
            get_dict["_list_filter"] = path

            user_type = DB.get_type(username)
            if user_type == "H":
                x1 = []
                y1 = []
                info = Jiang.dayk(stock_id)

                for i in range(len(info)):
                    x1.append(info[i][0])
                    y1.append(info[i][1:])
                day_kline = Kline("日K线图")
                day_kline.add("日K", x1, y1, is_datazoom_show=True, is_toolbox_show=False)

                x2 = []
                y2 = []
                info = Jiang.monthk(stock_id)
                for i in range(len(info)):
                    x2.append(info[i][0])
                    y2.append(info[i][1:])
                month_kline = Kline("月K线图")
                month_kline.add("月K", x2, y2, is_datazoom_show=True, is_toolbox_show=False)

                x3 = []
                y3 = []
                info = Jiang.yeark(stock_id)
                for i in range(len(info)):
                    x3.append(info[i][0])
                    y3.append(info[i][1:])
                year_kline = Kline("年K线图")
                year_kline.add("年K", x3, y3, is_datazoom_show=True, is_toolbox_show=False)

                x_pma_5 = kline_control.get_info(5, stock_id)[0]
                y_pma_5 = kline_control.get_info(5, stock_id)[1]
                pma_5 = Line()
                pma_5.add("5 PMA", x_pma_5, y_pma_5, is_datazoom_show=True, is_toolbox_show=False)

                x_pma_10 = kline_control.get_info(10, stock_id)[0]
                y_pma_10 = kline_control.get_info(10, stock_id)[1]
                pma_10 = Line()
                pma_10.add("10 PMA", x_pma_10, y_pma_10, is_datazoom_show=True, is_toolbox_show=False)

                x_pma_30 = kline_control.get_info(30, stock_id)[0]
                y_pma_30 = kline_control.get_info(30, stock_id)[1]
                pma_30 = Line()
                pma_30.add("30 PMA", x_pma_30, y_pma_30, is_datazoom_show=True, is_toolbox_show=False)

                # 集成了日k线，5日均线，10日均线，30均线
                overlap = Overlap()
                overlap.add(day_kline)
                overlap.add(pma_5)
                overlap.add(pma_10)
                overlap.add(pma_30)

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
                                       flag=1,
                                       kid=stock_id,
                                       page_now=page_now)
            else:
                return render_template("query.html",
                                       presentResults=present_results,
                                       html=html,
                                       kid=stock_id,
                                       flag=0,
                                       page_now=page_now)
        elif request.args.get('page'):
            # stock_id = request.args.get('id')
            infos = stol(session.get("infos"))
            stock_id = infos[20 * (int(request.args.get('page')) - 1)][0]

            page_now = request.args.get("page", 1)
            pager_obj = Pagination(request.args.get("page", 1), len(infos), request.path, request.args,
                                   per_page_count=20)  # 每页显示20个查询结果
            present_results = infos[pager_obj.start:pager_obj.end]  # 现在要显示的结果
            html = pager_obj.page_html()
            get_dict = request.args.to_dict()
            path = urlencode(get_dict)  # 转化成urlencode格式的
            get_dict["_list_filter"] = path

            user_type = DB.get_type(username)
            if user_type == "H":
                x1 = []
                y1 = []
                info = Jiang.dayk(stock_id)

                for i in range(len(info)):
                    x1.append(info[i][0])
                    y1.append(info[i][1:])
                day_kline = Kline("日K线图")
                day_kline.add("日K", x1, y1, is_datazoom_show=True, is_toolbox_show=False)

                x2 = []
                y2 = []
                info = Jiang.monthk(stock_id)
                for i in range(len(info)):
                    x2.append(info[i][0])
                    y2.append(info[i][1:])
                month_kline = Kline("月K线图")
                month_kline.add("月K", x2, y2, is_datazoom_show=True, is_toolbox_show=False)

                x3 = []
                y3 = []
                info = Jiang.yeark(stock_id)
                for i in range(len(info)):
                    x3.append(info[i][0])
                    y3.append(info[i][1:])
                year_kline = Kline("年K线图")
                year_kline.add("年K", x3, y3, is_datazoom_show=True, is_toolbox_show=False)

                x_pma_5 = kline_control.get_info(5, stock_id)[0]
                y_pma_5 = kline_control.get_info(5, stock_id)[1]
                pma_5 = Line()
                pma_5.add("5 PMA", x_pma_5, y_pma_5, is_datazoom_show=True, is_toolbox_show=False)

                x_pma_10 = kline_control.get_info(10, stock_id)[0]
                y_pma_10 = kline_control.get_info(10, stock_id)[1]
                pma_10 = Line()
                pma_10.add("10 PMA", x_pma_10, y_pma_10, is_datazoom_show=True, is_toolbox_show=False)

                x_pma_30 = kline_control.get_info(30, stock_id)[0]
                y_pma_30 = kline_control.get_info(30, stock_id)[1]
                pma_30 = Line()
                pma_30.add("30 PMA", x_pma_30, y_pma_30, is_datazoom_show=True, is_toolbox_show=False)

                # 集成了日k线，5日均线，10日均线，30均线
                overlap = Overlap()
                overlap.add(day_kline)
                overlap.add(pma_5)
                overlap.add(pma_10)
                overlap.add(pma_30)

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
                                       flag=1,
                                       kid=stock_id,
                                       page_now=page_now)
            else:
                return render_template("query.html",
                                       presentResults=present_results,
                                       html=html,
                                       kid=stock_id,
                                       flag=0,
                                       page_now=page_now)
        else:
            return redirect(url_for('home'))


# 显示用户类型
@app.context_processor
def show_type():
    username = session.get("info_username")
    if username:
        user_type = DB.get_type(username)
        if user_type == "H":
            user_type = "账户续费"
        elif user_type == "L":
            user_type = "账户升级"
        return {"user_type": user_type}
    else:
        return {"user_type": None}


###############交易客户端代码##################

@app.route('/index')
@login_required
def index():
    if not session.get('userid'):
        return render_template("log_in.html")
    else:
        return render_template("index.html")


@app.route('/image/<path:filename>')
@login_required
def image(filename):
    return send_file('image/%s' % filename)


@app.route('/public/<path:filename>')
@login_required
def public(filename):
    return send_file('public/%s' % filename)


@app.route('/modules/<path:filename>')
@login_required
def modules(filename):
    return send_file('modules/%s' % filename)


@app.route('/fonts/<path:filename>')
@login_required
def fonts(filename):
    return send_file('/public/fonts/%s' % filename)


@app.route('/info')
@login_required
def info():
    if not session.get('userid'):
        return render_template("log_in.html")
    else:
        return render_template("info.html")


@app.route('/log_in')
@login_required
def log_in():
    return render_template("log_in.html")



@app.route("/buy")
@login_required
def buy():
    if not session.get('userid'):
       return render_template("log_in.html")
    else:
        return render_template("buy.html")


@app.route("/sell")
@login_required
def sell():
    if not session.get('userid'):
       return render_template("log_in.html")
    else:
        return render_template("sell.html")


@app.route("/cancel")
@login_required
def cancel():
    if not session.get('userid'):
        return render_template("log_in.html")
    else:
        return render_template("cancel.html")


@app.route("/stock_info")
@login_required
def stock_info():
    if not session.get('userid'):
        return render_template("log_in.html")
    else:
        return render_template("stock_info.html")


@app.route("/fund_info")
@login_required
def fund_info():
    if not session.get('userid'):
        return render_template("log_in.html")
    else:
        return render_template("fund_info.html")


@app.route("/stock_query", methods=['GET', 'POST'])
@login_required
def stock_query():
    if not session.get('userid'):
        return render_template("log_in.html")
    else:
        return render_template("stock_query.html")

###########################################

####################账户管理系统####################

# 资金主页面
@app.route('/fund_main')
def fund_main():
    if not session.get('username'):
        return redirect('fund_manager_login')  # 未登录跳回登录界面
    return render_template('fund_main.html', error_message="")


# 资金账户登录
@app.route('/fund_manager_login', methods=['GET', 'POST'])
def fund_manager_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = db.session.execute(
            "select * from fund_account_manager where username ='"
            + username + "'and password='" + password + "';"
        )
        if result.first() is None:
            return render_template('fund_manager_login.html', error_message='账户或密码错误!')
        else:
            session['username'] = username
            return redirect(url_for('fund_main'))
    return render_template('fund_manager_login.html', error_message="")


# 资金账户登出
@app.route('/fund_manager_logout')
def fund_manager_logout():
    session.pop('username', None)
    return redirect(url_for('fund_manager_login'))


# 资金账户销户
@app.route('/fund_logoff', methods=['GET', 'POST'])
def fund_logoff():
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))
    if request.method == 'POST':
        ID_card = request.form['ID_card']
        security_account = request.form['security_account']
        username = request.form['username']
        password = request.form['password']
        result = db.session.execute(
            "select * from fund_account_user where username = '" + username +
            "' and password = '" + password +
            "' and ID_card = '" + ID_card +
            "' and is_enabled = 'Y' and security_account = '" + security_account + "';"
        )
        if result.first() is None:
            result = db.session.execute(
                "select * from fund_account_user where username = 'U" + username +
                "' and password = '" + password +
                "' and ID_card = '" + ID_card +
                "' and security_account = '" + security_account + "';"
            )
            if result.first() is None:
                return render_template('fund_logoff.html', error_message='密码错误!')
            return render_template('fund_logoff.html', error_message='账户已失效!')
        else:
            result = db.session.execute(
                "select * from fund_account_user where username = '" + username +
                "' and enabled_money <= 0 and freezing_money <= 0;"
            )
            if result.first() is None:
                return render_template('fund_logoff.html', error_message='资金未取出!')
            db.session.execute(
                "UPDATE fund_account_user SET is_enabled = 'N' WHERE username = '"
                + username + "';"
            )
            db.session.execute(
                "UPDATE fund_account_user SET username = 'U"
                + username + "' WHERE username ='" + username + "';"
            )
            return render_template('fund_logoff.html', error_message='销户成功!')
    return render_template('fund_logoff.html', error_message="")


# 资金账户注册
@app.route('/fund_user_reg', methods=['GET', 'POST'])
def fund_user_reg():
    if not session.get('username'):
        return redirect('fund_manager_login')  # 未登录跳回登录界面
    if request.method == 'GET':
        return render_template( 'fund_user_reg.html',error_message="")
    else:  # 建立资金账户
        if (request.form['password'] == "" or
                request.form['fund_pwd'] == "" or request.form['ID_card'] == ""):
            return render_template('fund_user_reg.html', error_message='必要信息为空')
        if (request.form['password'] !=
                request.form['password_again']):
            return render_template('fund_user_reg.html', error_message='两次密码不同')

        items = db.session.execute("select count(*) from fund_account_user")  # 查找下一编号
        for data in items:
            username = "F"+(str)(data[0]+1000000)
        security_account=request.form['security_account']
        if security_account[0] =='P':#个人证券账户
            items=db.session.execute("select username from security_account_personal_user where is_enabled='Y'and fund_account='' and username='"
                                     +security_account+"'and ID_card='"+request.form['ID_card']+"'")
            if items.first() is not None:  # 可用账户存在(enabled=Y 且无关联资金账户)
                items=db.session.execute("update security_account_personal_user set fund_account='"+username+"' where username='"
                                     +security_account+"'")
            else:#假的证券账户号
                return render_template( 'fund_user_reg.html',error_message='错误的证券账户号')
        else:#法人证券账户
            items=db.session.execute("select username from security_account_coporate_user where is_enabled='Y'and fund_account='' and username='"
                                     +security_account+"'and ID_card='"+request.form['ID_card']+"'")
            if items.first() is not None:#可用账户存在(enabled=Y 且无关联资金账户)
                items=db.session.execute("update security_account_coporate_user set fund_account='"+username+"' where username='"
                                     +security_account+"'")
            else:# 假的证券账户号
                return render_template( 'fund_user_reg.html',error_message='错误的证券账户号')
        items=db.session.execute("insert into fund_account_user values('"+username
                                     +"','"+request.form['password']+"','"+request.form['fund_pwd']+"','"
                                     +request.form['ID_card']+"','0','0','Y','"+security_account+"')")
        return render_template( 'fund_user_reg.html',error_message='注册成功,资金账户号码是：'+username)


# 资金账户挂失
@app.route('/fund_report_loss',methods=['GET','POST'])#资金挂失
def fund_report_loss():
    if not session.get('username'):
        return redirect('fund_manager_login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template( 'fund_report_loss.html',error_message="")
    else:
        security_account=request.form['security_account']
        items=db.session.execute("select * from fund_account_user where is_enabled='Y' and username ='"+request.form['username'] +
                             "'and security_account='"+security_account+"'and ID_card='"+request.form['ID_card']+"'")
        if items.first() is not None:#找到对应可用账户且身份验证正确
            db.session.execute("update fund_account_user set is_enabled='N' where username ='"+request.form['username'] +"'")#冻结
            if security_account[0]=="P":
                db.session.execute("update security_account_personal_user set is_enabled='N' where username ='"+security_account +"'")#冻结
            else:
                db.session.execute("update security_account_coporate_user set is_enabled='N' where username ='"+security_account +"'")#冻结
            return redirect('fund_issue')
        else:#账户错误或与身份信息或证券账户不匹配
            return render_template( 'fund_report_loss.html',error_message='账号错误或与身份信息或证券账户不匹配')


# 补办资金账户
@app.route('/fund_issue',methods=['GET','POST'])#资金补办
def fund_issue():
    if not session.get('username'):
        return redirect('login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template( 'fund_issue.html',error_message="")
    else:
        old_fund_account=request.form['old_fund_account']
        security_account=request.form['security_account']
        if(security_account[0]=="U" or old_fund_account[0]=="U"):
            return render_template( 'fund_issue.html',error_message='已经销户的账号')
        items=db.session.execute("select enabled_money,freezing_money from fund_account_user where is_enabled='N' and username='"+old_fund_account+
                                  "'and security_account='"+security_account+"' and ID_card='"+request.form['ID_card']+"'")
        if items.first() is not None:
            items=db.session.execute("select enabled_money,freezing_money from fund_account_user where is_enabled='N' and username='"+old_fund_account+"'")
            for data in items:
                old_enabled_money=str(data[0].quantize(Decimal('0.00')))
                old_freezing_money=str(data[1].quantize(Decimal('0.00')))
        else:
            return render_template( 'fund_issue.html',error_message='账户或身份验证错误')
        #此处为创建新的资金账户
        if(request.form['password']=="" or request.form['fund_pwd']=="" or request.form['ID_card']==""):
            return render_template( 'fund_user_reg.html',error_message='必要信息为空')
        if(request.form['password']!=request.form['password_again']):
            return render_template( 'fund_user_reg.html',error_message='两次密码不同')

        items=db.session.execute("select count(*) from fund_account_user")#查找下一编号
        for data in items:
            username="F"+(str)(data[0]+1000000)
        #激活证券账户并与新资金账户关联
        if security_account[0] =='P':#个人证券账户
            items=db.session.execute("update security_account_personal_user set fund_account='"+username+"',is_enabled='Y' where username='"
                                     +security_account+"'")
        else:#法人证券账户
            items=db.session.execute("update security_account_coporate_user set fund_account='"+username+"',is_enabled='Y' where username='"
                                     +security_account+"'")
        items=db.session.execute("insert into fund_account_user values('"+username
                                     +"','"+request.form['password']+"','"+request.form['fund_pwd']+"','"
                                     +request.form['ID_card']+"','0','0','Y','"+security_account+"')")

        db.session.execute("update fund_account_user set enabled_money='"+old_enabled_money+"',freezing_money='"+old_freezing_money+"' where username ='"+username +"'")#转移资金
        db.session.execute("update fund_account_user set username='U"+old_fund_account[1:8]+"' where is_enabled='N' and username ='"+old_fund_account +"'")#注销之前的资金账号
        return render_template('fund_issue.html',error_message='补办成功,新的资金账户是'+username)


# 修改资金账户密码
@app.route('/fund_change_password', methods=['GET', 'POST'])
def manager_change_password():
    # 未登录
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))

    else:
        # get
        if request.method == 'GET':
            return render_template('fund_change_password.html', error_message="")
        # post
        else:
            username = request.form['username']
            password = request.form['password']
            new_pwd1 = request.form['password_new']
            new_pwd2 = request.form['password_again']

            result = db.session.execute(
                "select * from fund_account_user where username ='" + username + "' and password='" + password + "'and is_enabled='Y'")
            if result.first() is None:
                return render_template('fund_change_password.html', error_message='账号密码错误或账户不存在')
            if new_pwd1 != new_pwd2:
                return render_template('fund_change_password.html', error_message='两次输入密码不一致')
            result = db.session.execute(
                "update fund_account_user set password='" + new_pwd1 + "'where username='" + username + "'")
            return render_template('fund_change_password.html', error_message='修改成功')


# 修改交易密码
@app.route('/fund_change_fund_pwd', methods=['GET', 'POST'])
def manager_change_fund_pwd():
    # 未登录
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))

    else:
        # get
        if request.method == 'GET':
            return render_template('fund_change_password.html', error_message="")
        # post
        else:
            username = request.form['username']
            password = request.form['password']
            new_pwd1 = request.form['fund_pwd_new']
            new_pwd2 = request.form['fund_pwd_again']
            result = db.session.execute(
                "select * from fund_account_user where username ='" + username + "' and password='" + password + "'and is_enabled='Y'")
            if result.first() is None:
                return render_template('fund_change_password.html', error_message="账号密码错误或账号不存在")
            if new_pwd1 != new_pwd2:
                return render_template('fund_change_password.html', error_message="两次输入密码不一致")
            result = db.session.execute(
                "update fund_account_user set fund_pwd='" + new_pwd1 + "'where username='" + username + "'and is_enabled='Y'")
            return render_template('fund_change_password.html', error_message="修改成功")


@app.route('/fund_operate', methods=['GET'])
def fund_oprate():
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))
    return render_template('fund_operate.html', error_message='')


# 存钱
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))
    else:
        if request.method == 'GET':
            return render_template('fund_operate.html', error_message="")
        else:
            username = request.form['username']
            password = request.form['fund_pwd']
            money = request.form['money']
            result = db.session.execute(
                "select enabled_money from fund_account_user where username ='" + username + "'and fund_pwd='" + password + "'and is_enabled='Y'")
            if result.first() is None:
                return render_template('fund_operate.html', error_message="账号密码错误或账户不可用")
            fund = 0
            result = db.session.execute(
                "select enabled_money from fund_account_user where username ='" + username + "'and fund_pwd='" + password + "'")
            for query_result in result:
                fund = query_result[0] + Decimal.from_float(float(money))
            fund = str(fund)
            print(
                "update fund_account_user set enabled_money=" + fund + "where username ='" + username + "' and fund_pwd='" + password + "'")
            result = db.session.execute(
                "update fund_account_user set enabled_money=" + fund + "where username ='" + username + "' and fund_pwd='" + password + "'and is_enabled='Y'")
            return render_template('fund_operate.html', error_message="存款成功")


# 取款
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))
    else:
        if request.method == 'GET':
            return render_template('fund_operate.html', error_message="")
        else:
            username = request.form['username']
            password = request.form['fund_pwd']
            money = request.form['money']
            result = db.session.execute(
                "select enabled_money,freezing_money from fund_account_user where username ='" + username + "'and fund_pwd='" + password + "'and is_enabled='Y'")
            if result.first() is None:
                return render_template('fund_operate.html', error_message="账号密码错误或账户不可用")
            total_fund = 0
            freezing_fund = 0
            result = db.session.execute(
                "select enabled_money,freezing_money from fund_account_user where username ='" + username + "'and fund_pwd='" + password + "'and is_enabled='Y'")
            for query_result in result:
                total_fund = query_result[0]
                freezing_fund = query_result[1]
            fund = total_fund - Decimal.from_float(float(money))
            if fund - freezing_fund < 0:
                return render_template('fund_operate.html', error_message="可用资金不足")
            fund = str(fund)
            result = db.session.execute(
                "update fund_account_user set enabled_money=" + fund + "where username ='" + username + "'and fund_pwd='" + password + "'")
            return render_template('fund_operate.html', error_message="取款成功")


# 资金查询
@app.route('/fund_search', methods=['GET', 'POST'])
def fund_search():
    if not session.get('username'):
        return redirect(url_for('fund_manager_login'))
    else:
        if request.method == 'GET':
            return render_template('fund_search.html', error_message="")
        else:
            username = request.form['username']
            password = request.form['password']
            result = db.session.execute("select * from fund_account_user where username ='" + username + "'")
            if result.first() is None:
                return render_template('fund_search.html', error_message="账号密码错误")
            else:
                result = db.session.execute(
                    "select security_account,ID_card,enabled_money,freezing_money,is_enabled  from fund_account_user where username ='" + username + "'")
                for query_result in result:
                    account = query_result[0]
                    idcard = query_result[1]
                    fund = str(query_result[2])
                    freeze_fund = str(query_result[3])
                    is_enabled = query_result[4]
                return render_template(
                    'fund_search_output.html',
                    username=account,
                    ID_card=idcard,
                    enabled_money=fund,
                    freezing_money=freeze_fund,
                    is_enabled=is_enabled,
                    error_message="查询成功"
                )
                # 返回总资金和可用资金


# 交易客户端登录
@app.route('/account_user_login', methods=['POST'])
def account_user_login():
    dict = json.loads(request.get_data())
    username = dict['username']
    password = dict['password']
    result = db.session.execute(
        "select * from fund_account_user where username ='" + username + "'and password='" + password + "'")
    if result.first() is None:
        data = {"state": "false", "msg": "登录失败"}
        return jsonify(data)
    else:
        session['userid'] = username
        data = {"state": "true", "security_username": username}
        return jsonify(data)


# 交易客户端修改密码
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    # 未登录
    if not session.get('userid'):
        data = {"state": "false", "msg": "未登录或登录过期"}
        return jsonify(data)
    else:
        # get
        if request.method == 'GET':
            if not session.get('userid'):
                return render_template("log_in.html")
            else:
                return render_template("change_password.html")
        # post
        else:
            dict = json.loads(request.get_data())
            username = dict['username']
            password = dict['password']
            new_pwd = dict['new_password']
            result = db.session.execute(
                "select * from fund_account_user where username ='" + username + "'and password='" + password + "'and is_enabled='Y'")
            if result.first() is None:
                data = {"state": "false", "msg": "账号密码错误或账户不可用"}
                return jsonify(data)
            print("update fund_account_user set password='" + new_pwd + "where username='" + username + "'")
            result = db.session.execute(
                "update fund_account_user set password='" + new_pwd + "'where username='" + username + "'")
            data = {"state": "true", "msg": "修改成功"}
            return jsonify(data)


# 交易客户端查询资金
@app.route('/fund_account', methods=['POST'])
def fund_account():
    if not session.get('userid'):
        data = {"state": "false", "msg": "未登录或登录过期"}
        return jsonify(data)
    else:
        # get
        if request.method == 'GET':
            pass
        # post
        else:
            dict = json.loads(request.get_data())
            username = dict['username']
            result = db.session.execute("select * from fund_account_user where username ='" + username + "'")
            if result.first() is None:
                data = {"state": "false", "msg": "查询失败"}
                return jsonify(data)
            else:
                result = db.session.execute(
                    "select enabled_money,freezing_money from fund_account_user where username ='" + username + "'")
                for query_result in result:
                    fund = str(query_result[0])
                    freeze_fund = str(query_result[1])
                # 返回总资金和可用资金
                data = {'fund': fund, 'freeze_fund': freeze_fund}
                return jsonify(data)


# 交易客户端证券账户查询
@app.route('/security_account', methods=['GET', 'POST'])
def security_account():
    if not session.get('userid'):
        data = {"state": "false", "msg": "未登录或登录过期"}
        return jsonify(data)
    else:
        # get
        if request.method == 'GET':
            pass
        # post
        else:
            dict = json.loads(request.get_data())
            fund_username = dict['username']
            result = db.session.execute(
                "select security_account from fund_account_user where username ='" + fund_username + "'")
            if result.first() is None:
                data = {"state": "false", "msg": "查询失败"}
                return jsonify(data)
            result = db.session.execute(
                "select security_account from fund_account_user where username ='" + fund_username + "'")
            username = ""
            for query_result in result:
                username = query_result[0]
            result = db.session.execute("select * from security_in_account where username ='" + username + "'")
            if result.first() is None:
                list=[]
                dict= {"name": "", "num": "", "price": "", "cost": "", "profit": ""}
               # list.append(dict)
                response = app.response_class(
                    response=json.dumps({"stock":list}),
                    status=200,
                    mimetype='application/json'
                )
                return response

            else:
                list = []
                result = db.session.execute("select * from security_in_account where username ='" + username + "'")
                for query_result in result:
                    id = query_result[1]
                    name = query_result[2]
                    num = query_result[3]
                    price = get_stock_price(id)  # 调用信息发布api
                    cost = float(str(query_result[4]))
                    profit = price * num - cost
                    dict = {"name": name, "num": num, "price": price, "cost": cost, "profit": profit}
                    list.append(dict)
                    response = app.response_class(
                        response=json.dumps({"stock": list}),
                        status=200,
                        mimetype='application/json'
                    )
                return response

#中央交易系统
def trade_fund(username,money,operation_type):
    result=db.session.execute("select * from fund_account_user where username ='"+username +"'")
    if result.first() is None:
        return False
    result=db.session.execute("select enabled_money,freezing_money from fund_account_user where username ='"+username +"'")
    fund=0
    freeze_fund=0
    new_fund=0
    new_freeze_fund=0
    for query_result in result:
        fund=float(str(query_result[0]))
        freeze_fund=float(str(query_result[1]))
    if operation_type=="buy":
        new_fund=fund
        new_freeze_fund=freeze_fund+money
    elif operation_type=="sell":
        new_fund=fund+money
        new_freeze_fund=freeze_fund
    if new_fund>=new_freeze_fund:
        new_fund=str(new_fund)
        new_freeze_fund=str(new_freeze_fund)
        print(new_fund)
        result=db.session.execute("update fund_account_user set enabled_money="+new_fund
                                  +",freezing_money="+new_freeze_fund+" where username ='"+username +"'")
        return True
    else:
        return False

def trade_security(username,security_number,amount,operation_type):
    result=db.session.execute("select * from security_in_account where username ='"
                              +username +"' and security_number='"+security_number+"'")
    if result.first() is None:
        return False
    result=db.session.execute("select amount,freezing_amount from security_in_account where username ='"
                              +username +"' and security_number='"+security_number+"'")
    security=0
    freeze_security=0
    new_security=0
    new_freeze_security=0
    for query_result in result:
        security=query_result[0]
        freeze_security=query_result[1]
    if operation_type=="sell":
        new_security=security
        new_freeze_security=freeze_security+amount
    elif operation_type=="buy":
        new_security=security+amount
        new_freeze_security=freeze_security
    if new_security>=new_freeze_security:
        new_security=str(new_security)
        new_freeze_security=str(new_freeze_security)
        result=db.session.execute("update security_in_account set amount="+new_security
                                  +",freezing_amount="+new_freeze_security+" where username ='"+username
                                  +"' and security_number='"+security_number+"'")
        return True
    else:
        return False


# 主页面
@app.route('/security_main')
def security_main():
    if not session.get('username'):
        return redirect('fund_manager_login')  # 未登录跳回登录界面
    return render_template('security_main.html', error_message="")


# 登出
@app.route('/security_manager_logout')
def manager_logout():
    session.pop('username', None)
    return redirect(url_for('security_manager_login'))


# 登录
@app.route('/security_manager_login', methods=['GET', 'POST'])
def security_manager_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = db.session.execute(
            "select * from security_account_manager where username ='" + username + "'and password='" + password + "';"
        )
        if result.first() is None:
            return render_template('security_manager_login.html', error_message='密码错误!')
        else:
            session['username'] = username
            return redirect(url_for('security_main'))
    return render_template('security_manager_login.html', error_message="")


# 个人销户
@app.route('/security_logoff', methods=['GET', 'POST'])
def security_logoff():
    if not session.get('username'):
        return redirect(url_for('manager_login'))
    if request.method == 'POST':
        id_card = request.form['ID_card']
        username = request.form['username']
        result = db.session.execute(
            "select * from security_account_personal_user where username = '" + username +
            "'and ID_card = '" + id_card + "'and is_enabled = 'Y';"
        )
        if result.first() is None:
            result = db.session.execute(
                "select * from security_account_personal_user where username = 'U" + username +
                "'and ID_card = '" + id_card + "';"
            )
            if result.first() is None:
                return render_template('security_logoff.html', error_message='密码错误!')
            else:
                return render_template('security_logoff.html', error_message='证券账户已销户!')
        else:
            result = db.session.execute(
                "select * from security_in_account where username = '" + username + "'"
            )
            if result.first() is not None:
                return render_template('security_logoff.html', error_message='证券未售出!')
            db.session.execute(
                "UPDATE security_account_personal_user SET is_enabled = 'N' WHERE username = '"
                + username + "';"
            )
            db.session.execute(
                "UPDATE security_account_personal_user SET username = 'U"
                + username + "' WHERE username ='" + username + "';"
            )
            db.session.execute(
                "update fund_account_user set is_enabled = 'N' where security_account ='" + username + "'")
            db.session.execute(
                "UPDATE security_account_personal_user SET fund_account = '' WHERE username ='U" + username + "';"
            )
            return render_template('security_logoff.html', error_message='销户成功!')
    return render_template('security_logoff.html', error_message="")


# 法人销户
@app.route('/security_logoff_agent', methods=['GET', 'POST'])
def security_logoff_agent():
    print("in")
    if not session.get('username'):
        return redirect(url_for('manager_login'))
    if request.method == 'POST':
        registration_number = request.form['registration_number']
        username = request.form['username']
        result = db.session.execute(
            "select * from security_account_coporate_user where username = '" + username +
            "' and registration_number = '" + registration_number + "' and is_enabled = 'Y';"
        )
        if result.first() is None:
            result = db.session.execute(
                "select * from security_account_coporate_user where username = 'U" + username +
                "' and registration_number = '" + registration_number + "';"
            )
            if result.first() is None:
                return render_template('security_logoff.html', error_message='密码错误!')
            else:
                return render_template('security_logoff.html', error_message='证券账户已销户!')
        else:
            result = db.session.execute(
                "select * from security_in_account where username = '" + username + "'"
            )
            if result.first() is not None:
                return render_template('security_logoff.html', error_message='证券未售出!')
            db.session.execute(
                "UPDATE security_account_coporate_user SET is_enabled = 'N' WHERE username ='"
                + username + "';"
            )
            db.session.execute(
                "UPDATE security_account_coporate_user SET username = 'U"
                + username + "' WHERE username ='" + username + "';"
            )
            db.session.execute(
                "update fund_account_user set is_enabled = 'N' where security_account ='" + username + "'")
            db.session.execute(
                "UPDATE security_account_coporate_user SET fund_account = '' WHERE username ='U" + username + "';"
            )
            return render_template('security_logoff.html', error_message='销户成功!')
    # return redirect(url_for('security_logoff'))
    return render_template('security_logoff.html', error_message="")


# 法人注册
@app.route('/security_coporate_user_reg',methods=['GET','POST'])
def security_coporate_user_reg():
    if not session.get('username'):
        return redirect('security_manager_login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template( 'security_coporate_user_reg.html',error_message='')

    if(request.form['password']=="" or request.form['name']=="" or request.form['ID_card']=="" or
    request.form['address']==""  or request.form['phone']=="" or request.form['registration_number']==""
    or request.form['business_number']=="" or request.form['executor']=="" or request.form['executor_ID_card']==""
    or request.form['executor_phone']=="" or request.form['executor_address']==""):
        return render_template( 'security_coporate_user_reg.html',error_message='必要信息为空')

    if(request.form['password']!=request.form['password_again']):
        return render_template( 'security_coporate_user_reg.html',error_message='两次密码不同')
    items=db.session.execute("select count(*) from security_account_coporate_user")#查找下一编号
    for data in items:
        username="C"+(str)(data[0]+1000000)
    items=db.session.execute("insert into security_account_coporate_user values('"+username
                                     +"','"+request.form['password']+"','"+request.form['registration_number']+"','"
                                     +request.form['business_number']+"','"+request.form['ID_card']+"','"+request.form['name']
                                     +"','"+request.form['phone']+"','"+request.form['address']+"','"+request.form['executor']
                                     +"','"+request.form['executor_ID_card']+"','"+request.form['executor_phone']+"','"+request.form['executor_address']
                                     +"','Y',''"+")")
    return render_template( 'security_coporate_user_reg.html',error_message='注册成功，您的账号是：'+username)


# 个人注册
@app.route('/security_personal_user_reg',methods=['GET','POST'])
def security_personal_user_reg():
    if not session.get('username'):
        return redirect('security_manager_login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template( 'security_personal_user_reg.html',error_message='')
    else:
        if(request.form['password']=="" or request.form['name']=="" or request.form['ID_card']=="" or
        request.form['address']==""  or request.form['phone']=="" or request.form['profession']==""
        or request.form['educational_background']=="" or request.form['company']==""):
            return render_template( 'security_personal_user_reg.html',error_message='必要信息为空')
        if(request.form['password']!=request.form['password_again']):
            return render_template( 'security_personal_user_reg.html',error_message='两次密码不同')

        items=db.session.execute("select count(*) from security_account_personal_user")#查找下一编号
        for data in items:
            username="P"+(str)(data[0]+1000000)
        items=db.session.execute("insert into security_account_personal_user values('"+username
                                     +"','"+request.form['password']+"','"+request.form['name']+"','"
                                     +request.form['sex']+"','"+request.form['ID_card']+"','"+request.form['address']+
                                     "','"+request.form['profession']+"','"+request.form['educational_background']
                                     +"','"+request.form['company']+"','"+request.form['phone']+"','Y',''"+")")

        return render_template( 'security_personal_user_reg.html',error_message='注册成功,您的账号是：'+username)


# 证券挂失
@app.route('/security_report_loss',methods=['GET','POST'])
def security_report_loss():
    if not session.get('username'):
        return redirect('security_manager_login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template( 'security_report_loss.html',error_message='')
    else:
        username=request.form['username']
        if username[0] =="P":#个人证券账户
            items=db.session.execute("select * from security_account_personal_user where is_enabled='Y' and username ='"+ username +
                             "'and ID_card='"+request.form['ID_card']+"'")
            if items.first() is not None:#找到对应可用账户且身份验证正确
                db.session.execute("update security_account_personal_user set is_enabled='N' where username ='"+username +"'")#冻结
                return redirect('security_per_issue')#跳转补办
            else:#账户错误或与身份证不匹配
                return render_template( 'security_report_loss.html',error_message='账户错误或与身份证不匹配')
        else:#法人证券账户
            items=db.session.execute("select * from security_account_coporate_user where is_enabled='Y' and username ='"+username +
                             "'and registration_number='"+request.form['registration_number']+"'")
            if items.first() is not None:#找到对应账户且身份验证正确
                db.session.execute("update security_account_coporate_user set is_enabled='N' where username ='"+username +"'")#冻结
                return redirect('security_cor_issue')#跳转补办
            else:#账户错误或与法人注册登记号不匹配
                return render_template( 'security_report_loss.html',error_message='账户错误或与法人注册登记号不匹配')


# 个人证券补办
@app.route('/security_per_issue',methods=['GET','POST'])
def security_per_issue():
    if not session.get('username'):
        return redirect('security_manager_login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template('security_per_issue.html',error_message='')
    else:
        old_security_account=request.form['old_security_account']
        if(old_security_account[0]=="U"):
            return render_template( 'security_per_issue.html',error_message='已经销户的账号')
        items=db.session.execute("select fund_account from security_account_personal_user where is_enabled='N' and username='"+old_security_account+
                                  "'and ID_card='"+request.form['ID_card']+"'")
        if items.first() is not None:
            items=db.session.execute("select fund_account from security_account_personal_user where username='"+old_security_account+"'")
            for data in items:
                fund_account=data[0]
        else:
            return render_template( 'security_per_issue.html',error_message='账户或身份验证错误')
        #注册新个人证券账户
        if(request.form['password']=="" or request.form['name']=="" or request.form['ID_card']=="" or
        request.form['address']==""  or request.form['phone']=="" or request.form['profession']==""
        or request.form['educational_background']=="" or request.form['company']==""):
            return render_template( 'security_personal_user_reg.html',error_message='必要信息为空')
        if(request.form['password']!=request.form['password_again']):
            return render_template( 'security_personal_user_reg.html',error_message='两次密码不同')

        items=db.session.execute("select count(*) from security_account_personal_user")#查找下一编号
        for data in items:
            username="P"+(str)(data[0]+1000000)
        items=db.session.execute("insert into security_account_personal_user values('"+username
                                     +"','"+request.form['password']+"','"+request.form['name']+"','"
                                     +request.form['sex']+"','"+request.form['ID_card']+"','"+request.form['address']+
                                     "','"+request.form['profession']+"','"+request.form['educational_background']
                                     +"','"+request.form['company']+"','"+request.form['phone']+"','Y','"+fund_account+"')")
        db.session.execute("update security_in_account set username='"+username+"' where username='"+old_security_account+"'")#转移证券
        db.session.execute("update security_account_personal_user set username='U"+old_security_account[1:8]+"' where is_enabled='N' and username='"+old_security_account+"'")#注销原证券账户
        db.session.execute("update fund_account_user set security_account='"+username+"' where username ='"+fund_account +"'")#资金账户关联新证券
        return render_template('security_per_issue.html',error_message='补办成功,新的的账号是：'+username)


# 法人证券补办
@app.route('/security_cor_issue',methods=['GET','POST'])
def security_cor_issue():
    if not session.get('username'):
        return redirect('security_manager_login')#未登录跳回登录界面
    if request.method=='GET':
        return render_template('security_cor_issue.html',error_message='')
    else:
        old_security_account=request.form['old_security_account']
        if(old_security_account[0]=="U"):
            return render_template('security_cor_issue.html',error_message='已经销户的账号')
        items=db.session.execute("select fund_account from security_account_coporate_user where is_enabled='N' and username='"+
                                  old_security_account+"'and registration_number='"+request.form['registration_number']+"'")
        if items.first() is not None:
            items=db.session.execute("select fund_account from security_account_coporate_user where username='"+old_security_account+"'")
            for data in items:
                fund_account=data[0]
        else:
            return render_template( 'security_cor_issue.html',error_message='账户或身份验证错误')
        #注册新法人证券账户
        if(request.form['password']=="" or request.form['name']=="" or request.form['ID_card']=="" or
                request.form['address']==""  or request.form['phone']=="" or request.form['registration_number']==""
                or request.form['business_number']=="" or request.form['executor']=="" or request.form['executor_ID_card']==""
                or request.form['executor_phone']=="" or request.form['executor_address']==""):
            return render_template( 'security_coporate_user_reg.html',error_message='必要信息为空')

        if(request.form['password']!=request.form['password_again']):
            return render_template( 'security_coporate_user_reg.html',error_message='两次密码不同')
        items=db.session.execute("select count(*) from security_account_coporate_user")#查找下一编号
        for data in items:
            username="C"+(str)(data[0]+1000000)
        items=db.session.execute("insert into security_account_coporate_user values('"+username
                                     +"','"+request.form['password']+"','"+request.form['registration_number']+"','"
                                     +request.form['business_number']+"','"+request.form['ID_card']+"','"+request.form['name']
                                     +"','"+request.form['phone']+"','"+request.form['address']+"','"+request.form['executor']
                                     +"','"+request.form['executor_ID_card']+"','"+request.form['executor_phone']+"','"+request.form['executor_address']
                                     +"','Y','"+fund_account+"'"+")")
        db.session.execute("update security_in_account set username='"+username+"' where username='"+old_security_account+"'")#转移证券
        db.session.execute("update security_account_coporate_user set username='U"+old_security_account[1:8]+"' where is_enabled='N' and username='"+old_security_account+"'")#注销原证券账户
        db.session.execute("update fund_account_user set security_account='"+username+"' where username ='"+fund_account +"'")#资金账户关联新证券

        return render_template('security_cor_issue.html',error_message='注册成功,新的账号是：'+username)


@app.route('/admin/trade/clean',methods=['POST'])
def clean_queue_handler():
    # ctx = app.app_context()
    # ctx.push()
    data = request.get_json()
    stock_id = data['stock_id']
    clean_queue(stock_id)
    json_data = {
        "state": 'true',
    }
    response = app.response_class(
        response=json.dumps(json_data),
        status=200,
        mimetype='application/json'
    )
    return response
#
# @app.route('/admin/trade/start',methods=['POST'])
# def start_stock():
#     data = request.get_json()
#     stock_id = data['stock_id']
#     start_trading(stock_id)
#     json_data = {
#         "state": 'true',
#     }
#     response = app.response_class(
#         response=json.dumps(json_data),
#         status=200,
#         mimetype='application/json'
#     )
#     return response


# @app.route('/admin/trade/stop',methods=['POST'])
# def start_stock():
#     data = request.get_json()
#     stock_id = data['stock_id']
#     stop_trading(stock_id)
#     json_data = {
#         "state": 'true',
#     }
#     response = app.response_class(
#         response=json.dumps(json_data),
#         status=200,
#         mimetype='application/json'
#     )
#     return response
#
# @app.route('/admin/trade/price',methods=['POST'])
# def start_stock():
#     data = request.get_json()
#     stock_id = data['stock_id']
#     stop_trading(stock_id)
#     json_data = {
#         "state": 'true',
#         "data" : 3,
#     }
#     response = app.response_class(
#         response=json.dumps(json_data),
#         status=200,
#         mimetype='application/json'
#     )
#     return response

@app.route('/transaction_state',methods=['POST'])
def cancel_order():
    data = request.get_json()
    order_id = data['transaction_id']
    order_type = data['order_type']
    if order_type == 2:
        remove_order(order_id)
        json_data = {
            "status":True,
            'msg':'删除成功'
        }
        response = app.response_class(
            response=json.dumps(json_data),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        status = get_order_status(order_id)
        if status:
            json_data = {
                "status":True,
                'msg':"订单存在"
            }
        else:
            json_data = {
                "status":False,
                'msg':"订单不存在或已完成"
            }
        response = app.response_class(
            response=json.dumps(json_data),
            status=200,
            mimetype='application/json'
        )
        return response




@app.route('/admin/orders_info',methods=['GET','POST'])
def stock_orders_info():
    data = request.get_json()
    # user_id = 'test'
    data_get = get_stock_orders(data['stock_id'],data['type'])

    json_data = data_get
    response = app.response_class(
        response=json.dumps(json_data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/all_transaction',methods=['GET','POST'])
def orders_info():
    data = request.get_json()
    user_id = session.get('userid')
    # user_id = 'F1000000'
    json_data = {
        "state":'true',
        'message':'Hello World',
        'data':get_user_orders(user_id)
    }
    response = app.response_class(
        response=json.dumps(json_data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/trade_shares',methods=['POST','GET'])
def order_handler():
    print("jjjjjjjjjjj")
    if request.method == 'POST':
        data = request.get_json()
        user_id = session.get('userid')
        # user_id = 'F1000000'
        # print(user_id)
        # user_id = 'uid001'
        order_id = create_order(user_id,data['stock_id'],data['order_type'],data['price'],data['volume'],db)
        if order_id == -1:
            msg = {
                'state': 'false',
                'transaction_id': order_id
            }
        else:
            msg = {
                'state':'true',
                'transaction_id':order_id
            }
        response = app.response_class(
            response=json.dumps(msg),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        return 'HELLO'

@app.route('/manage/api/login', methods=['POST'])
def login_api():
    response_dict = {}
    print(request.get_data())
    data = request.get_json()
    print(data)
    input_id = data['username']
    input_password = data['password']
    if input_id is None or input_password is None:
        response_dict['msg'] = 'no username or password'
        response_dict['code'] = 0
    else:
        user = User.query.filter_by(user_id=input_id).first()
        if user is not None and user.user_password == input_password:
            response_dict['token'] = manager.get_token(input_id)
            response_dict['code'] = 1
        elif user is not None:
            response_dict['code'] = 2
            response_dict['msg'] = 'wrong password'
        else:
            response_dict['code'] = 3
            response_dict['msg'] = "the user doesn't exist"
    return jsonify(response_dict)


@app.route('/manage/api/check-token', methods=['POST', 'GET'])
def check_token_api():
    response_dict = {}
    try:
        token = request.headers.get('token')
        if token is None or token == 'null':
            token = request.cookies.get('geeky-token')
        if manager.check_token(token):
            user_id = manager.parse_token(token)
            return jsonify({'code': 1, 'user_id': user_id, 'msg': 'successful'})
    except Exception as e:
        return jsonify({'code': 0, 'msg': str(e)})
    return jsonify({'code': 0, 'msg': 'error'})


@app.route('/manage/api/stock', methods=['POST', 'GET'])
def get_stock_list_api():
    token = request.headers.get('token')
    if not manager.check_token(token):
        return "{'msg':'login fail'}"
    try:
        user_id = manager.parse_token(token)
        user_stock_list = UserStock.query.filter_by(user_id=user_id).all()
        stock_list = []
        for stock in user_stock_list:
            stock_dict = {}
            stock_info = get_stock_info_manage(stock.stock_id)
            stock_list.append(stock_info)
        response_dict = {'user_id': user_id, 'stock_list': stock_list}
        return jsonify(response_dict)
    except Exception as e:
        print(e)
        return jsonify({'msg': 'error'})


@app.route('/manage/api/super-stock', methods=['POST', 'GET'])
def get_super_stock_list_api():
    token = request.headers.get('token')
    data = request.get_json()
    if not manager.check_token(token):
        return "{'msg':'login fail'}"
    try:
        user_id = manager.parse_token(token)
        user = User.query.filter_by(user_id=user_id).first()
        if user is None or not user.super:
            return jsonify({'msg': 'error'})
        user_id = data['user_id']
        user_stock_list = UserStock.query.filter_by(user_id=user_id).all()
        stock_list = []
        for stock in user_stock_list:
            stock_dict = get_stock_info_manage(stock.stock_id)
            stock_list.append(stock_dict)
        response_dict = {'user_id': user_id, 'stock_list': stock_list}
        return jsonify(response_dict)
    except Exception as e:
        print(e)
        return jsonify({'msg': 'error'})


@app.route('/manage/api/reset-password', methods=['POST', 'GET'])
def reset_password_api():
    token = request.headers.get('token')
    print(token)
    if not manager.check_token(token):
        return jsonify({'msg': 'login fail'})
    user_id = manager.parse_token(token)
    data = request.get_json()
    print(data)
    try:
        old_password = data['old_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        check_password_result = manager.check_password(user_id, old_password, new_password, confirm_password)
        if not check_password_result['result']:
            return check_password_result
        if not manager.reset_password(user_id, new_password):
            return jsonify({'msg': 'resetting error!', 'code': 0})
    except Exception as e:
        return jsonify({'msg': e})
    return jsonify({'msg': 'reset successfully', 'result': True})

@app.route('/manage/api/change-stock-status', methods=['POST', 'GET'])
def restart_stock_api():
    token = request.headers.get('token')
    if not manager.check_token(token):
        return "{'msg':'login fail'}"
    user_id = manager.parse_token(token)
    data = request.get_json()
    try:
        stock_id = data['stock_id']
        status = data['status']
        if not manager.user_stock_auth(user_id, stock_id):
            return jsonify({'msg': 'error'})
        if not change_stock_status(stock_id, status):
            return jsonify({'msg': 'error'})
        return jsonify({'msg': 'restart successfully'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'error'})


@app.route('/manage/api/set-price-limit', methods=['POST', 'GET'])
def set_price_limit_api():
    token = request.headers.get('token')
    if not manager.check_token(token):
        return jsonify({'msg': 'error'})
    user_id = manager.parse_token(token)
    data = request.get_json()
    print(data)
    try:
        stock_id = data['stock_id']
        gains = data['gains']
        decline = data['decline']
        if not manager.user_stock_auth(user_id, stock_id):
            return jsonify({'msg': 'error'})
        if not set_price_limit(stock_id, gains, True):
            return jsonify({'msg': 'error'})
        if not set_price_limit(stock_id, decline, False):
            return jsonify({'msg': 'error'})
        return jsonify({'msg': 'reset successfully'})
    except Exception as e:
        print(e)
        return jsonify({'msg': 'error'})


@app.route('/manage/api/stock-info', methods=['POST', 'GET'])
def get_buy_sell_items_api():
    token = request.headers.get('token')
    if not manager.check_token(token):
        return jsonify([])
    user_id = manager.parse_token(token)
    data = request.get_json()
    try:
        stock_id = data['stock_id']
        if not manager.user_stock_auth(user_id, stock_id):
            return jsonify([])
        stock_info = StockInfo.query.filter_by(stock_id=stock_id).first()

        if stock_info is None:
            return jsonify({'msg': 'error'})
        sell_list = get_buy_sell_items(stock_id, False)
        buy_list = get_buy_sell_items(stock_id, True)
        print(sell_list)
        print(buy_list)
        response_json = {'stock_id': stock_id, 'stock_name': stock_info.stock_name,
                         'newest_price': float(stock_info.newest_price),
                         'newest': stock_info.newest, 'sell_list': sell_list, 'buy_list': buy_list}
        print(response_json)
        return jsonify(response_json)
    except Exception as e:
        print(e)
        return jsonify({'msg': 'error'})


@app.route('/manage/api/add-auth', methods=['POST', 'GET'])
def add_authorization_api():
    token = request.headers.get('token')
    if not manager.check_token(token):
        return jsonify({'code': 0, 'msg': 'error'})
    super_id = manager.parse_token(token)
    data = request.get_json()
    super_user = User.query.filter_by(user_id=super_id).first()
    if not super_user.super:
        return jsonify({'code': 0, 'msg': 'not super user'})
    try:
        user_id = data['user_id']
        stock_id = data['stock_id']
        return jsonify(manager.add_authorization(user_id, stock_id))
    except Exception as e:
        print(e)
        return jsonify({'code': 0, 'msg': 'error'})


@app.route('/manage/api/delete-auth', methods=['POST', 'GET'])
def delete_authorization_api():
    token = request.headers.get('token')
    if not manager.check_token(token):
        return jsonify({'code': 0, 'msg': 'error'})
    super_id = manager.parse_token(token)
    data = request.get_json()
    super_user = User.query.filter_by(user_id=super_id).first()
    if not super_user.super:
        return jsonify({'code': 0, 'msg': 'not super user'})
    try:
        user_id = data['user_id']
        stock_id = data['stock_id']
        return jsonify(manager.delete_authorization(user_id, stock_id))
    except Exception as e:
        print(e)
        return jsonify({'code': 0, 'msg': 'error'})


@app.route('/manage/homepage', methods=['GET'])
def homepage():
    return render_template('homepage.html')


@app.route('/manage/template', methods=['GET'])
def template():
    return render_template('template.html')


# @app.route('/manage/stock-info', methods=['GET'])
# def show_stock_info():
#     token = request.cookies.get('geeky-token')
#     if not manager.check_token(token):
#         return "{'msg':'login fail'}"
#     try:
#         user_id = manager.parse_token(token)
#         stock_id = request.args['stock-id']
#         if not manager.user_stock_auth(user_id, stock_id):
#             return jsonify({'msg': 'error'})
#         stock_info = manager.get_stock_info(stock_id)
#         buy_list = get_buy_sell_items(stock_id, True)
#         sell_list = get_buy_sell_items(stock_id, False)
#         now_time = datetime.datetime.now()
#         sell_monthly = 0
#         sell_weekly = 0
#         sell_daily = 0
#         for sell in sell_list:
#             seconds = time.mktime(time.strptime(sell['time'], '%Y-%m-%d %H:%M:%S'))
#             date_time = datetime.datetime.utcfromtimestamp(seconds)
#             if now_time - date_time < datetime.timedelta(days=7):
#                 sell_weekly += 1
#             if now_time - date_time < datetime.timedelta(days=30):
#                 sell_monthly += 1
#             if now_time - date_time < datetime.timedelta(days=1):
#                 sell_daily += 1
#         buy_monthly = 0
#         buy_weekly = 0
#         buy_daily = 0
#         for buy in buy_list:
#             seconds = time.mktime(time.strptime(buy['time'], '%Y-%m-%d %H:%M:%S'))
#             date_time = datetime.datetime.utcfromtimestamp(seconds)
#             if now_time - date_time < datetime.timedelta(days=7):
#                 buy_weekly += 1
#             if now_time - date_time < datetime.timedelta(days=30):
#                 buy_monthly += 1
#             if now_time - date_time < datetime.timedelta(days=1):
#                 buy_daily += 1
#         statistics = {'buy': {'daily': buy_daily, 'weekly': buy_weekly, 'monthly': buy_monthly},
#                       'sell': {'daily': sell_daily, 'weekly': sell_weekly}, 'monthly': sell_monthly}
#         print(buy_list)
#         print(sell_list)
#         return render_template("stock-info-1.html", stock_info=stock_info, buy_list=buy_list, sell_list=sell_list,
#                                statistics=statistics)
#     except Exception as e:
#         print(e)
#         return "error"


@app.route('/manage/auth-manage', methods=['GET'])
def auth_manage():
    return render_template("auth-manage.html")


@app.route('/manage/stock-info', methods=['GET'])
def stock_info_2():
    stock_id = request.args.get('stock-id');
    return render_template('stock-info.html', stock_id=stock_id);

####################################################################################


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True)
    # app.run(host="0.0.0.0", ssl_context='adhoc')
