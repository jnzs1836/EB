from flask import Flask,render_template,request,redirect,url_for,flash,session
import DB_Connector as DB
import os
from configure import APP_STATIC_TXT
from datetime import timedelta
from urllib.parse import urlencode
from pager import Pagination

app = Flask(__name__)

# 设置session的secret key
app.config['SECRET_KEY'] = os.urandom(24)

# 设置session内存的东西可以保持1小时，即账户能保持一小时登录
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=10)

# 设置请求内容的大小限制，即限制了上传文件的大小
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# 设置上传文件存放的目录
UPLOAD_FOLDER = "./static"

# 存查询结果，为了分页用
r = []

# 主页面
@app.route('/', methods=['GET','POST'])
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
    else:   # 每次回到登录界面把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("login.html")


# 注册页面
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':  # 注册
        if DB.Register(request.form['username'], request.form['password'], request.form['telephone']) == 1:
            return redirect(url_for('login'))
        else:
            flash("用户名或密码错误！！", 'err')
            return redirect(url_for('register'))
    else:   # 每次回到登录界面把账号密码记录清除
        if session.get("username"):
            session.pop("username")
        if session.get("password"):
            session.pop("password")
        return render_template("register.html")


# 密码找回
@app.route('/modify', methods=['GET','POST'])
def modify():
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

# 主页面
@app.route('/modify', methods=['GET','POST'])
def modify():
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

# 修改密码
@app.route('/modify', methods=['GET','POST'])
def modify():
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

# 账号升级或续费
@app.route('/modify', methods=['GET','POST'])
def modify():
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

# 查询
@app.route('/modify', methods=['GET','POST'])
def modify():
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
    app.debug = True
    app.run()