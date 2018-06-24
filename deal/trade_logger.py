import datetime
import mysql

class TradeLogger:
    def __init__(self, stock_id, db_conn):
        self.db = db_conn
        self.stock_id = stock_id


def get_data(conn):
    conn = mysql.connector.connect(user=db_user, password=db_secret, database='EB', use_unicode=True)
    cursor = conn.cursor()
    present_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 已经是str对象了,此时的时间
    previous_5_time = (datetime.datetime.now() + datetime.timedelta(seconds=-5)).strftime(
        "%Y-%m-%d %H:%M:%S")  # 已经是str对象了，向前推移5秒

    sql = "select price from trade_log where stock_id=%s and create_time>=%s and create_time<=%s"
    args_list = [stock_id, previous_5_time, present_time]
    cursor.execute(sql,args_list)
    result = cursor.fetchall()

    sum = 0
    for i in results:
        sum = sum + i[0]

    average = sum / len(results)

    print(present_time)
    print(previous_5_time)
    return
    # create table trade_log（
    #   id int unsigned not null primary key AUTO_INCREMENT,
    #   stock_id varchar(20),
    #   buy_id varchar(20),
    #   sell_id varchar(20),
    #   price decimal(5,2),
    #   volume integer,
    #   create_time timestamp not null default current_timestamp
    # )