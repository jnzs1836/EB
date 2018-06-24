from deal.deal_engine import DealEngine
import ctypes
from deal.deal import TestSturcture
import mysql.connector
import redis
from db_config import *
from multiprocessing import Pool

def single_run(item):
    conn = mysql.connector.connect(user=db_user, password=db_secret, database='EB', use_unicode=True)
    redis_conn = redis.Redis()

    deal_engine = DealEngine(str(item[0]), db_conn=conn, redis_conn=redis_conn)
    deal_engine.run()

def all_run():
    redis_conn = redis.Redis()
    conn = mysql.connector.connect(user=db_user, password=db_secret, database='EB', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute('select * from stock_set')
    result = cursor.fetchall()
    agents = len(result)
    data_set = []
    for item in result:
        stock_id = item[0]
        my = []
        my.append(stock_id)
        my.append(None)
        my.append(None)
        data_set.append(my)
    with Pool(processes=agents) as pool:
        pool.map(single_run,data_set)




if __name__ == '__main__':
    all_run()
    # redis_conn = redis.Redis()
    # conn = mysql.connector.connect(user=db_user, password=db_secret, database='EB', use_unicode=True)
    # deal_engine = DealEngine('130',db_conn=conn,redis_conn=redis_conn)
    # deal_engine.run()
    # dll = ctypes.CDLL('./deal/libdeal.so')
    # dll.testFunction.restype = TestSturcture
    # k = dll.testFunction(2)
    # print(k.a)