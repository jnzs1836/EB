from deal.deal_engine import DealEngine
import ctypes
from deal.deal import TestSturcture
import mysql.connector
import redis
from db_config import *
from multiprocessing import Pool
from trading.order import QueueManager


def clean():
    redis_conn = redis.Redis()
    conn = mysql.connector.connect(user=db_user, password=db_secret, database='EB', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute('select * from stock_set')
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    agents = len(result)
    data_set = []
    queue_manager = QueueManager()
    queue_manager.set_count()
    for item in result:
        stock_id = item[0]
        pair_queue = queue_manager.get_pair_queue(stock_id)
        pair_queue.clean()

if __name__ == '__main__':
    clean()