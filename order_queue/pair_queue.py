from order_queue.queue import Queue
from order_queue.order import Order
from order_queue.constant import *
import redis
class PairQueue :
    def __init__(self, stock_id, stock_name = None, r=None):
        if r:
            self.r = r
        else:
            self.r = redis.Redis()
        self.stock_id = stock_id
        self.stock_name = stock_name
        self.short_queue = Queue(stock_id,direction=SHORT,r=self.r)
        self.long_queue = Queue(stock_id,direction=LONG,r=self.r)

    def get_long_orders(self):
        get = self.long_queue.get_all()
        return get

    def get_short_orders(self):
        return self.short_queue.get_all()

    def push(self,order):
        if order.direction == LONG:
            return self.long_queue.push(order)
        else:
            return self.short_queue.push(order)

    def pop(self):
        return self.long_queue.pop(),self.short_queue.pop()

    def remove(self,order_id, order_direction):
        if order_direction == LONG:
            self.long_queue.remove(order_id)
        else:
            self.short_queue.remove(order_id)

    def user_orders(self,user_id):
        orders = []
        orders.extend(self.long_queue.user_orders(user_id))
        orders.extend(self.short_queue.user_orders(user_id))
        return orders

    def clean(self):
        self.long_queue.clean()
        self.short_queue.clean()

