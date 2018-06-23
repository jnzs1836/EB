from order_queue.constant import *
import time
class Order:
    def __init__(self, stock_id, user_id, price, volume, direction):
        self.stock_id = stock_id
        self.user_id = user_id
        self.price = price
        self.volume = volume
        self.direction = direction
        self._time = time.localtime(time.time())
        self.id = None

    def set_id(self, order_id):
        direction_map = {
            LONG:'LONG',
            SHORT:'SHORT'

        }
        segment = '__'
        self.id = self.stock_id + segment + self.user_id + segment + direction_map[int(self.direction)] +segment +  str(order_id)

    def get_string(self):
        return str(self.price) + "xinghong"

    def get_score(self):
        return self.price

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

    def get_stock_id(self):
        return self.stock_id

    def get_volume(self):
        return self.volume

    def get_user_id(self):
        return self.user_id

    def get_direction(self):
        return self.direction

    def get_map(self):
        return {
            'user_id':self.user_id,
            'price':self.price,
            'volume':self.volume,
            'direction':self.direction,
        }