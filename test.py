import random

from pyecharts import Kline
from flask import Flask, render_template


app = Flask(__name__)


REMOTE_HOST = "https://pyecharts.github.io/assets/js"

@app.route("/")
def g():
    a = []
    for i in range(20):
        b = []
        n = int(random.random()*100)
        b.append(n)
        b.append(n + int(random.uniform(1.1,10.1)*100)/100.0-6)
        b.append(n + int(random.uniform(1.1,11.2) * 100) / 100.0 - 6)
        b.append(n + int(random.uniform(1.1,10.5) * 100) / 100.0 - 6)
        a.append(b)
    kline = Kline("K 线图示例")
    kline.add("日K", ["2017/7/{}".format(i + 1) for i in range(20)], a)
    return render_template(
        "try.html",
        myechart=kline.render_embed(),
        host=REMOTE_HOST,
        script_list=kline.get_js_dependencies(),
    )


if __name__ == "__main__":
    # app.run(port=1234)
    # 看情况换端口
    app.run(debug=True)