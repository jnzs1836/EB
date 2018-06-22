from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import DB_Connector as DB
import config
from urllib.parse import urlencode
from pager import Pagination
from pyecharts import Kline, Line, Overlap
from functools import wraps
import json
import kline_control
import Jiang
import yuan

app = Flask(__name__)

app.config.from_object(config)  # 配置文件


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
    dic = {"latest_price": "1.11", "buy_highest_price": "2.22", "sale_lowest_price": "3.33"}
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

    dic["state"] = now["state"]
    if now["state"] == "true":
        dic["latest_price"] = tmp["latest_price"]
        dic["buy_highest_price"] = tmp["buy_highest_price"]
        dic["sale_lowest_price"] = tmp["sale_lowest_price"]

        dic["today_price"] = {"highest_price": now["day_h_price"], "lowest_price": now["day_l_price"]}
        dic["week_price"] = {"highest_price": now["week_h_price"], "lowest_price": now["week_l_price"]}
        dic["month_price"] = {"highest_price": now["month_h_price"], "lowest_price": now["month_l_price"]}
        dic["stock_info"] = now["notice"]
        dic["current_price"] = now["present_price"]
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
    if session.get("username"):
        session.pop("username", None)

    if request.method == 'POST':  # 登录
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("username"):
        session.pop("username", None)

    if request.method == 'POST':  # 登录
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
    if session.get("username"):
        session.pop("username", None)

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
    username = session.get("username")
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
    username = session.get("username")
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
    print(n)
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
    username = session.get("username")
    if request.method == 'POST':
        user_type = DB.get_type(username)
        name = request.form['optionsRadiosinline']

        if name == "stockcode":
            infos = [Jiang.query(request.form['name'], 0)]
        else:
            infos = Jiang.query(request.form['name'], 1)

        stock_id = infos[0][0]
        session["infos"] = ltos(infos)

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
                                   kid=present_results[0][0])
        else:
            return render_template("query.html",
                                   presentResults=present_results,
                                   html=html,
                                   kid=present_results[0][0],
                                   flag=0)
    else:
        if request.args.get('id', None):
            stock_id = request.args.get('id')
            infos = stol(session.get("infos"))

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
                                       kid=stock_id)
            else:
                return render_template("query.html",
                                       presentResults=present_results,
                                       html=html,
                                       kid=stock_id,
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
        elif user_type == "L":
            user_type = "账户升级"
        return {"user_type": user_type}
    else:
        return {"user_type": None}


if __name__ == "__main__":
    app.run(host="0.0.0.0")
