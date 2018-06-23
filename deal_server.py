from deal.deal_engine import DealEngine
import ctypes
from deal.deal import TestSturcture
import mysql.connector
import redis


if __name__ == '__main__':
    redis_conn = redis.Redis()
    conn = mysql.connector.connect(user='root', password='77122100Aa', database='test', use_unicode=True)
    deal_engine = DealEngine('0',db_conn=conn,redis_conn=redis_conn)
    deal_engine.run()
    dll = ctypes.CDLL('./deal/libdeal.so')
    dll.testFunction.restype = TestSturcture
    k = dll.testFunction(2)
    print(k.a)