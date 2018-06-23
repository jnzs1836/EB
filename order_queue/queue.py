
import redis
from order_queue.order import Order
from order_queue.constant import *
# import random
class Queue :
    def __init__(self, stock_id, direction = LONG, r = None):
        self.id  = stock_id
        if r:
            self.r = r
        else:
            self.r = redis.Redis()
        self.count = 0

    def push(self, order):
        if isinstance(order,Order):
            pass
        else:
            return 0
        order.set_id(self.count)
        self.count  = self.count + 1
        print(self.id)
        self.r.zadd(self.id,order.get_score(),order.get_id())
        # self.r.zadd(self.id,order.get_id(),order.get_score())
        self.r.hmset(order.get_id(),order.get_map())
        return order.get_id()

    def remove(self,order_id):
        if isinstance(order_id,str):
            pass
        else:
            return 0
        self.r.zrem(self.id,order_id)
        self.r.delete(order_id)
        return 1

    def get_all(self):
        order_ids = self.r.zrangebyscore(self.id, '-inf', 'inf')
        order_list = []
        for order_id in order_ids:
            order_dict = self.r.hgetall(order_id)
            order = dict()
            for key, value in order_dict.items():
                order[key.decode('utf-8')] = value.decode('utf-8')
            print(order)
            order_list.append(order)
            # order_list.append(self.r.hget())
        return order_list
    def get(self,order_id):
        return self.r.hvals(order_id)

    def user_orders(self,user_id):
        pattern = '*' + user_id + '*'
        order_ids = self.r.keys(pattern)
        orders = []
        for order_id in order_ids:
            orders.append(order_id.decode('utf-8'))
        return orders

    def pop(self):
        order_list = self.r.zrange(self.id,0,0)
        if not order_list:
            return None
        order_id = order_list[0]
        order_dict = self.r.hgetall(order_id)
        self.r.delete(order_id)
        self.r.zrem(self.id,order_id)
        print(order_dict)
        if order_dict:
            order = Order(self.id,order_dict['user_id'.encode('utf-8')].decode('utf-8'),
                          order_dict['price'.encode('utf-8')].decode('utf-8'),
                          order_dict['volume'.encode('utf-8')].decode('utf-8'),
                          order_dict['direction'.encode('utf-8')].decode('utf-8'))
        else:
            order = None
        return order


    def clean(self):
        order_ids = self.r.zrangebyscore(self.id, '-inf', 'inf')
        print(order_ids)
        for order_id in order_ids:
            order = self.r.hkeys(order_id)
            print(order)
            self.r.delete(order_id)
        self.r.zremrangebyscore(self.id, '-inf', 'inf')


def test_queue():
    queue = Queue("BABA")
    order = Order("BABA", "uid123", 16, 100, LONG)
    queue.push(order)
    order = Order("BABA", "uid124", 16, 100, LONG)
    queue.push(order)
    order = Order("BABA", "uid125", 16, 100, LONG)
    queue.push(order)
    queue.remove("BABA1")
    c = queue.get('BABA0')
    queue.clean()
    return str(c)

# if __name__ == '__main__':
#     order_queue = Queue("BABA")
#     order = Order("BABA","uid123",16,100,LONG)
#     order_queue.push(order)
#     order = Order("BABA","uid124",16,100,LONG)
#     order_queue.push(order)
#     order = Order("BABA","uid125",16,100,LONG)
#     order_queue.push(order)