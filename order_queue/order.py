from order_queue.constant import *
import time
# segment = '__'
segment = '__'

class Order:
    def __init__(self, stock_id, user_id, price, volume, direction):
        self.stock_id = stock_id
        self.user_id = user_id
        self.price = price
        self.volume = volume
        self.direction = direction
        self._time = time.localtime(time.time())
        self.id = None
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    def set_id(self, order_id, stock_key):
        direction_map = {
            LONG:'LONG',
            SHORT:'SHORT'

        }
        self.id = 'order' + stock_key + segment + 'uid' +self.user_id + segment + direction_map[int(self.direction)] +segment +  str(order_id)
    def from_hash(self,hash):
        self.id = hash['id'.encode('utf-8')].decode('utf-8')
        self.timestamp = hash['timestamp'.encode('utf-8')].decode('utf-8')

    def get_stock_id(self):
        return self.stock_id


    def get_string(self):
        return str(self.price) + "xinghong"

    def get_score(self):
        if self.direction == SHORT:
            return float(self.price)
        else:
            return 10000.0/float(self.price)


    def get_price(self):
        return self.price

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self,value):
        self._time = value

    def get_id(self):
        return self.id


    def get_volume(self):
        return self.volume

    def get_user_id(self):
        return self.user_id

    def get_direction(self):
        return self.direction

    def get_map(self):
        # now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        return {
            'id':self.id,
            'user_id':self.user_id,
            'stock_id':self.stock_id,
            'price':self.price,
            'volume':self.volume,
            'direction':self.direction,
            'timestamp':self.timestamp,
            'time': self.timestamp

        }