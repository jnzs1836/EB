import ctypes
import time
from order_queue.order import Order

class stock(ctypes.Structure):
    _fields_ = [('stock_id', ctypes.c_int), ('order_type',ctypes.c_int),('Time',ctypes.c_char * 40),('user_id',ctypes.c_int),('volume',ctypes.c_int,4),
                ('price',ctypes.c_double)
        ]
class exchange(ctypes.Structure):
    _fields_ = [
        ('stock_id',ctypes.c_int),
        ('buy_id',ctypes.c_int),
        ('sell_id',ctypes.c_int),
        ('Time',ctypes.c_char * 40),
        ('volume',ctypes.c_int),
        ('price',ctypes.c_double)
    ]
class TestSturcture(ctypes.Structure):
    _fields_ = [
        ('a',ctypes.c_int),
        ('n',ctypes.c_int)
    ]
def time_conversion(input):
    get = time.strftime("%H:%M:%S", input).encode('utf-8')
    return get

def order_conversion(order):
    get_time = time_conversion(order.time)
    print(order.get_user_id())
    print(float(order.get_price()))
    print(int(order.get_user_id()[1:]))
    get = stock(int(order.get_stock_id()),int(order.get_direction()),get_time,int(order.get_user_id()[1:]),int(order.get_volume()),float(order.get_price()))
    return get

def regenerate_order(result,long_order,short_order):
    deal_volume = result.volume
    if int(long_order.get_volume()) != result.volume:
        left_volume = int(long_order.get_volume()) - result.volume
        left_order = long_order
    elif int(short_order.get_volume()) != result.volume:
        left_volume = int(long_order.get_volume()) - result.volume
        left_order = short_order
    else:
        return None

    order = Order( left_order.get_stock_id(),left_order.get_user_id(),left_order.get_price(),left_volume,left_order.get_direction())
    return order

if __name__ == '__main__':
    print(time_conversion(time.localtime(time.time())))