from deal.deal import *
from order_queue.order import Order
from order_queue.pair_queue import PairQueue
import ctypes
from log.logger import Logger
import redis
from order_queue.constant import *
import time
# create table trade_log (id int unsigned not null primary key AUTO_INCREMENT, stock_id varchar(20), buy_id varchar(20), sell_id varchar(20), price integer, volume integer time timestamp not null default current_timestamp)

class DealEngine:
    def __init__(self, stock_id, db_conn = None, redis_conn = None):
        self.stock_id = stock_id
        self.stock_name = 'Not Set'
        self.pair_queue = PairQueue(stock_id)
        self.logger = Logger('engine')
        self.db_conn = db_conn
        self.limit = 2
        self.close_price = 10
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.stock_name = 'sss'



        if redis_conn is None:
            self.r = redis.Redis()
        else:
            self.r = redis_conn
        cursor = self.db_conn.cursor()
        try:
            cursor.execute('select stock_name from stock_set where stock_id=%s',
                           [str(self.stock_id)])
            result = cursor.fetchall()[0]
            self.stock_name = result[0]
            cursor.execute('select gains,decline,status,close_price from stock_state where stock_id=%s',[str(self.stock_id)])
            result = cursor.fetchall()
            self.limit = result[0][0]
            self.gains = self.limit
            self.decline = result[0][1]
            status = int(result[0][2])
            self.close_price = float(result[0][3])
            self.last_price = self.close_price
            self.exist = True
            self.r.hset(stock_id, 'engine_exist', True)
            if status == 1:
                self.redis_init(True,True,self.gains,self.decline,self.close_price)
                self.on = True
                print(str(stock_id) + " is running")
            else:
                self.redis_init(False,True,self.gains,self.decline,self.close_price)
                self.on = False
                print(str(stock_id) + " is pending")
            # self.last_price = float(self.r.hget(self.stock_id,'newest_price').decode('utf-8'))

            # self.close_price = self.last_price
            # if self.close_price == 0:
            #     self.close_price = 10
        except Exception as e:
            self.redis_init(False,False,0,0,0)
            self.close_price = 0
            self.on = False
            self.last_price = 0
            print( str(stock_id) +" fails: " + str(e))
            self.exist = False
        finally:
            self.set_open_price()
            # cursor.execute('insert into today_stock (stock_id,stock_name,price,date) values (%s,%s,%s,%s)',
            #                [self.stock_id, self.stock_name, self.close_price, now])
            self.db_conn.commit()
            cursor.close()


        # self.last_price = 4
        # self

    def redis_init(self,status,engine_exists,gains,decline,close_price):
        mapping = {
            'stock_id': self.stock_id,
            'stock_name': self.stock_name,
            'status': status,
            'last_price': close_price,
            'newest_price': close_price,
            'newest': close_price,
            'gains': gains,
            'decline': decline,
            'engine_exist':engine_exists,
            'long_count':0,
            'short_count':0
        }
        self.r.hmset(self.stock_id, mapping)

    def set_open_price(self):
        cursor = self.db_conn.cursor()
        cursor.execute("select max(date) from previous_stock where stock_id = %s",[self.stock_id])
        last_date = cursor.fetchall()[0][0]
        print(last_date)
        cursor.execute("select end_price from previous_stock where stock_id=%s and date=%s",[self.stock_id,last_date])
        price = float(cursor.fetchall()[0][0])
        self.r.hset(self.stock_id,'newest_price',price)
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute('insert into today_stock (stock_id,stock_name,price,date) values (%s,%s,%s,%s)',[self.stock_id,self.stock_name,price,now])

    def is_exist(self):
        return self.exist
    def on_trading(self):
        status = self.r.hget(self.stock_id,'status'.encode('utf-8')).decode('utf-8')
        if self.on is True and status is False:
            print(str(self.stock_id) + ' is stopped')
        elif self.on is False and status is True:
            print(str(self.stock_id) + ' is started')
        self.on = status
        if not self.exist:
            return False

        return self.on

        # if self.on:
        #     return True
        # else:
        #
        #     # time.sleep(1)
        #     cursor = self.db_conn.cursor()
        #     cursor.execute('select status from stock_state where stock_id=%s',[self.stock_id])
        #     status = int(cursor.fetchall()[0][0])
        #     if status ==1 :
        #         self.on = status
        #         return True
        #     else:
        #         return False

    def on_stop(self):
        self.on = False
        self.r.hset(self.id,'status',False)
        pass

    def on_resume(self):
        self.on = True
        self.r.hset(self.id, 'status', True)

    def on_close(self):
        self.on = False
        self.exist = False
        self.r.hest(self.id,'engine_exist',False)
        self.r.hset(self.id, 'status', False)

    def save_deal(self, result,buy_order,sell_order):
        cursor = self.db_conn.cursor()
        # result.price = 2
        # result.buy_id = 1
        # result.sell_id = 1
        print('-----------------------')
        print(result.sell_id)
        buy_fund_id = 'F' + str(result.buy_id)
        sell_fund_id = 'F' + str(result.sell_id)
        cursor.execute('select security_account from fund_account_user where username=%s',(sell_fund_id,))
        sell_id = cursor.fetchall()[0][0]
        cursor.execute('select security_account from fund_account_user where username=%s', (buy_fund_id,))
        buy_id = cursor.fetchall()[0][0]
        cursor.execute('select enabled_money from fund_account_user where username=%s', [buy_fund_id])
        print(buy_id)
        buy_money = float(cursor.fetchall()[0][0])
        cursor.execute('select enabled_money from fund_account_user where username=%s', [sell_fund_id])
        sell_money = float(cursor.fetchall()[0][0])
        buy_money -= result.volume * result.price
        sell_money += result.volume * result.price
        if buy_money < 0:
            return
        cursor.execute('select freezing_amount from security_in_account where username=%s', [sell_id])
        sell_freezing_security = int(cursor.fetchall()[0][0])
        sell_freezing_security -= result.volume

        #---------------------------------------------------------------------------------------------------------------
        # change security
        cursor.execute('select amount from security_in_account where username=%s', [sell_id])
        sell_security = int(cursor.fetchall()[0][0])
        sell_security -= result.volume
        print(sell_security)
        print(sell_freezing_security)
        sql = "update security_in_account set amount = %s, freezing_amount = %s  where username = '%s'" % (sell_security,sell_freezing_security,str(sell_id))
        print(sql)
        cursor.execute(sql)
        # quantity = result.price * result.volume

        cursor.execute('select amount from security_in_account where username=%s', [buy_id])
        buy_security = int(cursor.fetchall()[0][0])
        buy_security += result.volume
        cursor.execute('update security_in_account set amount = %s where username = %s',
                       [buy_security, buy_id])

        #---------------------------------------------------------------------------------------------------------------
        cursor.execute('select freezing_money from fund_account_user where username=%s', [buy_fund_id])
        buy_freezing_money = float(cursor.fetchall()[0][0])
        buy_freezing_money -= float(buy_order.get_price()) * result.volume

        cursor.execute('select freezing_money from fund_account_user where username=%s', [sell_fund_id])
        sell_freezing_money = float(cursor.fetchall()[0][0])
        sell_freezing_money -= float(sell_order.get_price()) * result.volume
        cursor.execute('update fund_account_user set enabled_money=%s, freezing_money = %s where username=%s',[buy_money,buy_freezing_money,buy_fund_id])
        cursor.execute('update fund_account_user set enabled_money=%s, freezing_money = %s where username=%s',[sell_money,sell_freezing_security,sell_fund_id])
        # cursor.execute('update fund_account_user set enabled_money=%s where username=%s',[sell_money,result.sell_id])
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute('insert into today_stock (stock_id,stock_name,price,date) values (%s,%s,%s,%s)',[self.stock_id,self.stock_name,result.price,now])
        cursor.execute('insert into trade_log (stock_id,buy_id,sell_id,price,volume) values (%s,%s,%s,%s,%s) ',[result.stock_id,buy_fund_id,sell_fund_id,int(result.price),result.volume])

        self.db_conn.commit()
        cursor.close()
        self.r.hset(result.stock_id,'last_price',result.price)
        self.r.hset(result.stock_id,'newest_price',result.price)
        self.r.hset(result.stock_id,'newest',result.price)
        print("deal finished")

    def deal(self):
        long_order, short_order = self.pair_queue.get_first_order()
        print(long_order)

        if not long_order:
            # self.logger.info("No Order Now")
            return False

        if not short_order:
            # self.pair_queue.push(long_order)
            # self.logger.info("No Order Now")
            return False
        a = ctypes.c_double(100000.0)
        print('+++')
        print(self.close_price)
        b = ctypes.c_double(self.close_price)
        dll = ctypes.CDLL('./deal/libdeal.so')
        dll.Deal.restype = exchange
        dll.Deal.argtypes = [
            stock,stock, ctypes.c_double, ctypes.c_double
        ]
        # converted_long_order = order_conversion(long_order)
        # converted_short_order = order_conversion(short_order)
        # # print(converted_long_order.buy_id)
        # result = dll.Deal(converted_long_order, converted_short_order, a, b)
        # print(result.volume)
        # self.save_deal(result, long_order, short_order)
        # re_order = regenerate_order(result, long_order, short_order)
        # if re_order:
        #     self.pair_queue.push(re_order)
        # else:
        #     pass
        # self.logger.info("Success")
        try:
            converted_long_order = order_conversion(long_order)
            converted_short_order = order_conversion(short_order)
            print(long_order.volume)
            result = dll.Deal(converted_long_order,converted_short_order,a,b)
            if int(result.volume) == 0:
                raise ctypes.ArgumentError('deal fail')
            print("finish")
            print(result.volume)
            self.save_deal(result,long_order,short_order)
            re_order = regenerate_order(result,long_order,short_order)
            if re_order:
                print("re_order")
                print(re_order)
                self.pair_queue.push(re_order)
            else:
                pass
            self.pair_queue.remove(long_order.id,LONG)
            self.pair_queue.remove(short_order.id,SHORT)
            self.logger.info("Success")
        except ctypes.ArgumentError as e:
            print("in except: " + str(e))
            # self.pair_queue.push(long_order)
            # self.pair_queue.push(short_order)

        # converted_long_order = order_conversion(long_order)
        # converted_short_order = order_conversion(short_order)
        #
        # # dll = ctypes.CDLL('./deal/libdeal.so')
        #
        # a = ctypes.c_double(self.limit)
        # b = ctypes.c_double(self.last_price)
        # # dll.Deal.restype = exchange
        # result = dll.Deal(converted_long_order, converted_short_order,a,b)
        # self.save_deal(result,long_order,short_order)
        # re_order = regenerate_order(result=result)
        # # self.pair_queue.push(re_order)
        self.logger.info("Success")
        return True

    def run(self):
        while self.on_trading():
            self.deal()