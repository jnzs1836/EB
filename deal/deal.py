import ctypes
import time

class stock(ctypes.Structure):
    _fields_ = [('stock_id', ctypes.c_int), ('buy_id',ctypes.c_int),('sell_id',ctypes.c_int),('volume',ctypes.c_int),
                ('price',ctypes.c_double),('Time',ctypes.c_char_p)
                ]
class exchange(ctypes.Structure):
    _fields_ = [
        ('stock_id',ctypes.c_int),
        ('buy_id',ctypes.c_int),
        ('sell_id',ctypes.c_int),
        ('Time',ctypes.c_char * 40),
        ('volume',ctypes.c_int),
        ('price',ctypes.c_float)
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
    get = stock(int(order.get_stock_id()),int(order.get_user_id()[3:]),int(order.get_user_id()[3:]),int(order.get_volume()),int(order.get_price()),get_time)
    return get

def regenerate_order(result):
    return None

if __name__ == '__main__':
    print(time_conversion(time.localtime(time.time())))